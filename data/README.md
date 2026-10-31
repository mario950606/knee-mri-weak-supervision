# Datos para reproducir el proyecto de MRI de rodilla

## Enlace proporcionado por el equipo

[Carpeta de datos en Google Drive](https://drive.google.com/drive/folders/1hHbz0PYiWFSdxO4C_9M7DRO6DpxJmSp6?usp=sharing)

**Nota:** el contenido exacto de la carpeta y sus permisos no pudieron comprobarse desde este documento. Antes de distribuir los datos, confirma que la licencia/condiciones del dataset RSNA/Kaggle permiten compartir los archivos incluidos y que no contienen información personal identificable.

## Ubicación esperada por el código

En `config/config.yaml`, `data.root` está configurado como `../RSNA_Knee`. Por tanto, deja los archivos autorizados en una carpeta hermana del repositorio:

```text
Documents/
├── knee-mri-weak-supervision/
│   ├── notebooks/
│   ├── scripts/
│   ├── config/config.yaml
│   └── data/README.md
└── RSNA_Knee/
    ├── raw/                 # CSV originales y, si están autorizados, DICOM
    │   ├── train.csv
    │   ├── train_series.csv
    │   ├── sagittal/
    │   └── axial/
    ├── processed/           # Etiquetas, tensores, CSV y otros resultados
    ├── manifest/            # Manifiestos de selección de series
    └── checkpoint/          # Pesos .pth ya entrenados
```

La estructura anterior es la **esperada por los scripts**, no un inventario verificado de Google Drive. Si las carpetas descargadas tienen otra disposición, adapta las rutas y/o `config/config.yaml` antes de ejecutar.

## Procedimiento

1. Consigue acceso autorizado al dataset y descarga los recursos necesarios de la carpeta de Drive, siempre que su distribución esté permitida.
2. Extrae los archivos manteniendo los nombres y la estructura esperados.
3. Comprueba desde la raíz del repositorio la carpeta de datos con `python src\config.py`.
4. Instala las dependencias usando `requirements.txt` y el kernel de Jupyter indicado en el README principal.
5. Para la demostración del Notebook 06, verifica que existan el tensor sagital, los metadatos GOLD DEV y `best_ablacion_focal.pth` en las rutas que el notebook espera.
6. Para reproducir las evaluaciones sin reentrenar, sigue los comandos documentados en el README principal.

## Alcance y precauciones

- Los 490 WEAK se usan para entrenamiento, los 39 GOLD DEV para validación y los 17 GOLD HOLDOUT para evaluación final MRI.
- El procedimiento de recuperación de checkpoints **no** equivale a volver a entrenar todos los modelos desde cero.
- Para reconstrucción desde DICOM son necesarios los datos originales autorizados; para recuperación pueden bastar los artefactos procesados y checkpoints correspondientes.
- No publiques datos médicos, DICOM ni sus derivados sin revisar permisos, licencias y privacidad. Si la redistribución no está autorizada, sustituye la descarga directa por instrucciones para acceder al conjunto original.
