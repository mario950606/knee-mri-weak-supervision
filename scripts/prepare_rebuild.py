
"""Prepara copias aisladas de los notebooks 01, 02 y 03.

No ejecuta notebooks ni modifica los archivos originales.
Las salidas reconstruidas se redirigen a runs/full_rebuild/.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "notebooks"
RUN_DIR = ROOT / "runs" / "full_rebuild"
RUN_DIR.mkdir(parents=True, exist_ok=True)


def replace_exact(source, old, new, notebook, cell):
    if source.count(old) != 1:
        raise RuntimeError(
            f"Patron esperado no encontrado exactamente una vez: "
            f"{notebook}, celda {cell}"
        )
    return source.replace(old, new, 1)


def patch_cell(nb, index, old, new, name):
    cell = nb["cells"][index]
    source = "".join(cell["source"])
    source = replace_exact(source, old, new, name, index)
    cell["source"] = source.splitlines(keepends=True)


def prepare(filename, modifications):
    path = SOURCE_DIR / filename
    nb = json.loads(path.read_text(encoding="utf-8"))

    for cell_index, old, new in modifications:
        patch_cell(nb, cell_index, old, new, filename)

    # No arrastrar resultados anteriores a la reconstruccion.
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            cell["outputs"] = []
            cell["execution_count"] = None

    destination = RUN_DIR / filename

    if destination.exists():
        raise FileExistsError(
            f"Ya existe {destination}. No se sobrescribira."
        )

    destination.write_text(
        json.dumps(nb, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    print("[PREPARADO]", destination)


# Notebook 01:
# Redirigir la particion GOLD y el CSV reconstruido.
prepare(
    "01_weak_label_extraction.ipynb",
    [
        (
            8,
            'gold_split.to_csv(',
            'GOLD_SPLIT_PATH = PROJECT_ROOT / "runs" / '
            '"full_rebuild" / "gold_split.csv"\n'
            'gold_split.to_csv(',
        ),
        (
            93,
            'ruta_500 = WEAK_DATA_DIR / nombre_archivo',
            'ruta_500 = PROJECT_ROOT / "runs" / '
            '"full_rebuild" / nombre_archivo',
        ),
    ],
)

# Notebook 02:
# Conservar el inventario historico como entrada
# y exportar el manifiesto nuevo por separado.
prepare(
    "02_mri_series_selection.ipynb",
    [
        (
            45,
            'manifest_sag.to_csv(',
            'MANIFEST_PATH = PROJECT_ROOT / "runs" / '
            '"full_rebuild" / "manifest_sagittal_final.csv"\n'
            'manifest_sag.to_csv(',
        ),
    ],
)

# Notebook 03:
# Leer las particiones y el manifiesto reconstruidos.
# Escribir imagenes y metadatos en una carpeta nueva.
prepare(
    "03_preprocessing_2_5d.ipynb",
    [
        (
            2,
            'MANIFEST_PATH = (\n'
            '    MANIFEST_DIR / "manifest_sagittal_final.csv"\n'
            ')',
            'MANIFEST_PATH = PROJECT_ROOT / "runs" / '
            '"full_rebuild" / "manifest_sagittal_final.csv"',
        ),
        (
            2,
            'GOLD_SPLIT_PATH = (\n'
            '    MANIFEST_DIR / "gold_split.csv"\n'
            ')',
            'GOLD_SPLIT_PATH = PROJECT_ROOT / "runs" / '
            '"full_rebuild" / "gold_split.csv"',
        ),
        (
            41,
            'OUTPUT_DIR = DATA_ROOT / "processed"',
            'OUTPUT_DIR = PROJECT_ROOT / "runs" / '
            '"full_rebuild"',
        ),
    ],
)

print("\nCopias preparadas. No se ejecutaron notebooks.")
print("Los archivos originales permanecen intactos.")
