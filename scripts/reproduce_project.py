
"""Verifica la reconstrucción y reproduce las evaluaciones MRI.

Uso:
    python scripts/reproduce_project.py
    python scripts/reproduce_project.py --execute

Modo predeterminado:
    Solo lectura y comparación de resultados históricos.

Modo --execute:
    Verifica las reconstrucciones y ejecuta los notebooks
    04, 05 y 06 usando checkpoints existentes.
    Puede actualizar CSV, PNG y notebooks ejecutados.

No reentrena modelos ni reconstruye automáticamente
las etapas 01, 02 y 03.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
REBUILD = ROOT / "runs" / "full_rebuild"
CONFIG = ROOT / "config" / "config.yaml"

NOTEBOOK_06 = (
    ROOT / "notebooks" / "06_demo_inferencia_mri.ipynb"
)


def load_data_root():
    config = yaml.safe_load(
        CONFIG.read_text(encoding="utf-8")
    )
    root = Path(config["data"]["root"])

    if not root.is_absolute():
        root = ROOT / root

    return root.resolve(), config


def compare_csv(name, reconstructed, historical):
    print(f"\n[{name}]")

    for path in (reconstructed, historical):
        if not path.is_file():
            raise FileNotFoundError(path)

    a = pd.read_csv(
        reconstructed,
        dtype={"StudyInstanceUID": str,
               "SeriesInstanceUID": str},
    )
    b = pd.read_csv(
        historical,
        dtype={"StudyInstanceUID": str,
               "SeriesInstanceUID": str},
    )

    if not a.equals(b):
        raise AssertionError(
            f"{name}: el CSV reconstruido no coincide "
            "con el histórico."
        )

    print(f"  OK: {len(a)} filas idénticas")


def compare_images(reconstructed, historical):
    print("\n[TENSOR MRI 2.5D]")

    x = np.load(reconstructed, mmap_mode="r")
    y = np.load(historical, mmap_mode="r")

    if x.shape != y.shape or x.dtype != y.dtype:
        raise AssertionError(
            "Los tensores tienen formas o tipos diferentes."
        )

    # Comparar por grupos para limitar el uso de RAM.
    for start in range(0, len(x), 16):
        end = min(start + 16, len(x))
        if not np.array_equal(x[start:end], y[start:end]):
            raise AssertionError(
                f"Diferencia de píxeles entre "
                f"los índices {start} y {end - 1}"
            )

    print(f"  OK: {x.shape} idéntico píxel por píxel")


def verify_rebuild():
    data_root, config = load_data_root()
    data = config["data"]

    print("=" * 65)
    print("REPRODUCIBILIDAD MRI - VERIFICACION")
    print("=" * 65)
    print("Datos:", data_root)
    print("Reconstruccion:", REBUILD)

    compare_csv(
        "01 - ETIQUETAS WEAK",
        REBUILD / "weak_500_reconstruido_validado.csv",
        data_root
        / data["processed"]["weak_labels"]
        / "weak_500_final.csv",
    )

    compare_csv(
        "02 - MANIFIESTO SAGITAL",
        REBUILD / "manifest_sagittal_final.csv",
        data_root / data["manifests"]["sagittal"],
    )

    compare_images(
        REBUILD / "images_2_5d_uint8.npy",
        data_root / data["processed"]["sagittal_images"],
    )

    compare_csv(
        "03 - METADATA MRI",
        REBUILD / "metadata_2_5d.csv",
        data_root / data["processed"]["sagittal_metadata"],
    )

    print("\nRECONSTRUCCION VERIFICADA CORRECTAMENTE")


def run_command(cmd):
    print("\nEjecutando:", " ".join(map(str, cmd)), flush=True)
    subprocess.run(
        cmd,
        cwd=ROOT,
        check=True,
    )


def run_evaluations():
    print("\n[04 Y 05 - EVALUACIONES]")

    run_command([
        sys.executable,
        str(ROOT / "scripts" / "reproduce_evaluation.py"),
        "--execute",
    ])

    print("\n[06 - DEMOSTRACION DE INFERENCIA]")

    run_command([
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--ExecutePreprocessor.timeout=-1",
        "--ExecutePreprocessor.kernel_name=knee-mri-venv",
        "--output=06_demo_inferencia_mri_ejecutado.ipynb",
        f"--output-dir={REBUILD}",
        str(NOTEBOOK_06),
    ])


def main():
    parser = argparse.ArgumentParser(
        description="Verificación y evaluación reproducible MRI"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Reejecuta notebooks 04, 05 y 06",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Prepara y verifica las etapas 01-03 antes de continuar",
    )

    args = parser.parse_args()

    try:
        if args.rebuild:
            run_command([
                sys.executable,
                str(ROOT / "scripts" / "run_full_rebuild.py"),
            ])
        else:
            verify_rebuild()

        if args.execute:
            run_evaluations()
            print("\nEVALUACIONES FINALIZADAS")
        else:
            print(
                "\nModo de verificacion completado. "
                "No se modificaron archivos."
            )

        return 0

    except (
        FileNotFoundError,
        KeyError,
        AssertionError,
        ValueError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
