
"""Reproducir evaluaciones de los notebooks 04 y 05, sin reentrenamiento.

Ubicar como scripts/reproduce_evaluation.py en la raíz del repositorio.

Predeterminado: únicamente validación, sin escrituras.
Para ejecutar: python scripts/reproduce_evaluation.py --execute

ADVERTENCIA: los notebooks pueden reescribir archivos derivados CSV/PNG en
RSNA_Knee/processed. El script no garantiza una ejecución completamente inocua.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NOTEBOOKS = [
    ROOT / "notebooks" / "04_training_models.ipynb",
    ROOT / "notebooks" / "05_evaluation_ablation_gradcam.ipynb",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Ejecutar notebooks 04 y 05; escribe resultados derivados",
    )
    args = parser.parse_args()

    config_path = ROOT / "config" / "config.yaml"

    if not config_path.is_file():
        print(f"ERROR: Falta {config_path}")
        return 2

    try:
        import yaml
    except ImportError:
        print(
            "ERROR: Falta PyYAML. "
            "Instalar con: python -m pip install -r requirements.txt"
        )
        return 2

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    rel = config.get("data", {}).get("root")

    if not rel:
        print("ERROR: data.root no esta definido en config.yaml")
        return 2

    data_root = (ROOT / rel).resolve()

    required = [
        data_root / "processed" / "images_2_5d_uint8.npy",
        data_root / "processed" / "metadata_2_5d.csv",
        data_root / "processed" / "images_2_5d_axial_uint8.npy",
        data_root / "processed" / "metadata_2_5d_axial.csv",
        *[
            data_root / "checkpoint" / f
            for f in (
                "best_cnn_2_5d.pth",
                "best_efficientnet_2_5d.pth",
                "best_ablacion_bce.pth",
                "best_ablacion_focal.pth",
                "best_ablacion_axial_focal.pth",
            )
        ],
        *NOTEBOOKS,
    ]

    missing = [p for p in required if not p.is_file()]

    print("Repositorio:", ROOT)
    print("Carpeta de datos:", data_root)
    print(
        "Recursos presentes:",
        len(required) - len(missing),
        "/",
        len(required),
    )

    for p in missing:
        print("FALTA:", p)

    if missing:
        return 2

    # Comprobar que los notebooks estén configurados para
    # recuperar checkpoints, no para entrenar nuevamente.
    expected = {
        NOTEBOOKS[0]: {
            "ENTRENAR_CNN_DESDE_CERO": "False",
            "ENTRENAR_EFFICIENTNET": "False",
        },
        NOTEBOOKS[1]: {
            "MODO_ABLACION": '"recuperar"',
            "RECONSTRUIR_TENSOR_AXIAL": "False",
        },
    }

    for nb, switches in expected.items():
        cells = json.loads(nb.read_text(encoding="utf-8"))["cells"]

        source = "\n".join(
            "".join(c.get("source", []))
            for c in cells
            if c.get("cell_type") == "code"
        )

        for var, value in switches.items():
            pattern = (
                rf"(?m)^\s*{re.escape(var)}\s*=\s*"
                rf"{re.escape(value)}(?=\s|#|$)"
            )

            if not re.search(pattern, source):
                print(
                    f"ERROR: No se ha confirmado "
                    f"{var} = {value} en {nb.name}"
                )
                return 2

    print("Comprobados modos de recuperacion (sin entrenar).")

    if not args.execute:
        print("Validacion terminada. Sin modificaciones.")
        print(
            "Para ejecutar evaluaciones: "
            "python scripts/reproduce_evaluation.py --execute"
        )
        return 0

    try:
        import nbconvert
        import ipykernel
    except ImportError:
        print(
            "ERROR: Instalar previamente: "
            "python -m pip install nbconvert ipykernel"
        )
        return 2

    out_dir = ROOT / "runs" / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)

    for nb in NOTEBOOKS:
        print(f"EJECUTANDO: {nb.name}", flush=True)

        cmd = [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=-1",
            "--ExecutePreprocessor.kernel_name=knee-mri-venv",
            "--output-dir",
            str(out_dir),
            "--output",
            nb.stem + "_ejecutado.ipynb",
            str(nb),
        ]

        result = subprocess.run(
            cmd,
            cwd=ROOT,
            check=False,
        )

        if result.returncode:
            print(
                f"ERROR en {nb.name}; "
                "se detiene la ejecucion."
            )
            return result.returncode

    print(
        "Evaluaciones terminadas. "
        "Revisar notebooks ejecutados en",
        out_dir,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
