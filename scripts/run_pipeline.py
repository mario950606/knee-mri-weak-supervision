
"""Verificador seguro del proyecto knee-mri-weak-supervision.

Uso desde la raíz del repositorio:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --strict

Este script NO ejecuta notebooks, NO entrena modelos y NO evalúa HOLDOUT.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = PROJECT_ROOT / "config" / "config.yaml"

NOTEBOOKS = [
    "01_weak_label_extraction.ipynb",
    "02_mri_series_selection.ipynb",
    "03_preprocessing_2_5d.ipynb",
    "04_training_models.ipynb",
    "05_evaluation_ablation_gradcam.ipynb",
    "06_demo_inferencia_mri.ipynb",
]

CHECKPOINTS = [
    "best_cnn_2_5d.pth",
    "best_efficientnet_2_5d.pth",
    "best_ablacion_bce.pth",
    "best_ablacion_focal.pth",
    "best_ablacion_axial_focal.pth",
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica los recursos del proyecto sin ejecutarlos"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Devuelve código de salida 1 si falta algún recurso"
    )
    args = parser.parse_args()

    missing = []
    found = 0

    def check(path: Path, description: str) -> None:
        nonlocal found
        if path.is_file():
            found += 1
            print(f"[OK]    {description}: {path}")
        else:
            missing.append(description)
            print(f"[FALTA] {description}: {path}")

    print("=" * 70)
    print("AUDITORÍA LOCAL | knee-mri-weak-supervision")
    print("No se ejecutan entrenamientos, procesamiento ni HOLDOUT")
    print("=" * 70)

    for filename in [
        "README.md",
        "requirements.txt",
        ".gitignore",
        "src/config.py"
    ]:
        check(PROJECT_ROOT / filename, filename)

    for filename in NOTEBOOKS:
        check(
            PROJECT_ROOT / "notebooks" / filename,
            f"Notebook {filename}"
        )

    check(CONFIG_FILE, "Configuración YAML")

    try:
        import yaml
    except ImportError:
        print(
            "[FALTA] PyYAML. Instala las dependencias con: "
            "python -m pip install -r requirements.txt"
        )
        missing.append("PyYAML")
        yaml = None

    if CONFIG_FILE.is_file() and yaml is not None:
        try:
            with CONFIG_FILE.open("r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if not isinstance(config, dict):
                raise ValueError(
                    "config.yaml no contiene un objeto YAML válido"
                )

            data = config["data"]
            root = Path(data["root"])

            if not root.is_absolute():
                root = (PROJECT_ROOT / root).resolve()

            print(f"\nDATA_ROOT: {root}")

            expected_labels = [
                "ACL",
                "MCL",
                "Medial Meniscus",
                "Lateral Meniscus",
                "Medial OA",
                "Lateral OA",
                "PF OA",
                "Effusion",
                "Synovitis",
                "Baker's",
                "Contusion",
                "Fracture",
            ]

            labels = config.get("labels")

            if labels == expected_labels:
                print("[OK]    12 etiquetas y orden esperado")
                found += 1
            else:
                print(
                    "[FALTA] Las 12 etiquetas no coinciden "
                    "con el orden esperado"
                )
                missing.append("Orden de 12 etiquetas")

            paths = {
                "CSV de entrenamiento": data["train_csv"],
                "CSV de series": data["train_series_csv"],
                "Imágenes sagitales":
                    data["processed"]["sagittal_images"],
                "Metadatos sagitales":
                    data["processed"]["sagittal_metadata"],
                "Imágenes axiales":
                    data["processed"]["axial_images"],
                "Metadatos axiales":
                    data["processed"]["axial_metadata"],
                "Manifiesto sagital":
                    data["manifests"]["sagittal"],
                "Manifiesto axial":
                    data["manifests"]["axial"],
            }

            for description, relative_path in paths.items():
                check(root / relative_path, description)

            checkpoint_dir = (
                root / data["checkpoints"]["directory"]
            )

            for name in CHECKPOINTS:
                check(
                    checkpoint_dir / name,
                    f"Checkpoint {name}"
                )

        except (
            KeyError,
            TypeError,
            ValueError,
            OSError,
            yaml.YAMLError
        ) as exc:
            print(
                f"[ERROR] No se pudo verificar config.yaml: {exc}"
            )
            missing.append("Configuración YAML válida")

    print("\n" + "=" * 70)
    print(
        f"Recursos correctos: {found} | "
        f"Pendientes: {len(missing)}"
    )

    if missing:
        print("Pendientes: " + ", ".join(missing))

    print(
        "Verificación terminada; "
        "no se ha modificado ningún archivo del proyecto."
    )

    return 1 if args.strict and missing else 0


if __name__ == "__main__":
    sys.exit(main())
