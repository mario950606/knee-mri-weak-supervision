
"""Reconstruccion controlada de datos MRI 01-03.

Uso desde la raiz del proyecto:
    .venv\\Scripts\\python.exe scripts\\run_full_rebuild.py

Reutiliza reconstrucciones completas existentes.
No entrena modelos ni modifica los notebooks originales.
"""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs" / "full_rebuild"

NOTEBOOKS = [
    "01_weak_label_extraction",
    "02_mri_series_selection",
    "03_preprocessing_2_5d",
]

OUTPUTS = [
    ["gold_split.csv", "weak_500_reconstruido_validado.csv"],
    ["manifest_sagittal_final.csv"],
    ["images_2_5d_uint8.npy", "metadata_2_5d.csv"],
]


def execute(command):
    subprocess.run(command, cwd=ROOT, check=True)


def main():
    print("=== RECONSTRUCCION MRI 01-03 ===", flush=True)

    originals = [
        ROOT / "notebooks" / f"{n}.ipynb"
        for n in NOTEBOOKS
    ]

    for file in originals:
        if not file.is_file():
            raise FileNotFoundError(file)

    prepared = [OUT / f"{n}.ipynb" for n in NOTEBOOKS]

    if not all(p.is_file() for p in prepared):
        if any(p.exists() for p in prepared):
            raise RuntimeError(
                "Hay copias preparadas incompletas. "
                "Revisalas antes de continuar."
            )

        print("Preparando copias aisladas...", flush=True)
        execute([
            sys.executable,
            str(ROOT / "scripts" / "prepare_rebuild.py"),
        ])

    for name, expected in zip(NOTEBOOKS, OUTPUTS):
        paths = [OUT / f for f in expected]
        exists = [p.is_file() for p in paths]

        if all(exists):
            print(
                f"[EXISTENTE] {name}: sin sobrescribir",
                flush=True,
            )
            continue

        if any(exists):
            raise RuntimeError(
                f"{name}: existen salidas parciales. "
                "No se sobrescribiran automaticamente."
            )

        print(f"[EJECUTANDO] {name}", flush=True)

        execute([
            sys.executable,
            "-m", "jupyter", "nbconvert",
            "--to", "notebook",
            "--execute",
            "--ExecutePreprocessor.timeout=-1",
            "--ExecutePreprocessor.kernel_name=knee-mri-venv",
            f"--output={name}_ejecutado.ipynb",
            f"--output-dir={OUT}",
            str(OUT / f"{name}.ipynb"),
        ])

        for path in paths:
            if not path.is_file():
                raise RuntimeError(
                    f"No se genero el archivo esperado: {path}"
                )

    print("\nVerificando reconstrucciones...", flush=True)

    execute([
        sys.executable,
        str(ROOT / "scripts" / "reproduce_project.py"),
    ])

    print("\nRECONSTRUCCION VERIFICADA", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, FileNotFoundError,
            subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
