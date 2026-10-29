# Clasificación multietiqueta de patologías de rodilla en MRI

Proyecto académico de Redes Neuronales y Aprendizaje Profundo (UNI). El sistema utiliza reportes radiológicos para construir **etiquetas débiles** y entrena modelos convolucionales sobre resonancias de rodilla representadas en formato **2.5D**. Predice 12 hallazgos; no es un sistema validado para uso clínico.

## Resumen del método

1. Extraer etiquetas débiles de reportes radiológicos multilingües.
2. Seleccionar series DICOM de rodilla en planos sagital y axial.
3. Preparar tres grupos de cortes por estudio, con representación `(3, 3, 224, 224)`.
4. Entrenar y evaluar una CNN desde cero y EfficientNet-B0.
5. Comparar Weighted BCE frente a Focal Loss, y el plano sagital frente al axial.
6. Evaluar sobre etiquetas GOLD, visualizar Grad-CAM y mostrar inferencia por estudio.

**Particiones utilizadas:** 490 estudios WEAK de entrenamiento, 39 GOLD DEV de validación y 17 GOLD HOLDOUT de evaluación final. Las etiquetas desconocidas (`-1`) se excluyen de las métricas correspondientes.

## Resultados obtenidos

| Experimento | AUC-ROC macro GOLD DEV |
| --- | ---: |
| CNN 2.5D desde cero | 0.6614 |
| EfficientNet-B0 inicial | **0.7665** |
| EfficientNet-B0 + Weighted BCE (ablación) | 0.7360 |
| EfficientNet-B0 + Focal, sagital | 0.7541 |
| EfficientNet-B0 + Focal, axial | 0.7061 |

Para el **modelo Focal sagital** utilizado en la demostración, se seleccionó un umbral de **0.54** usando GOLD DEV. Su AUC-ROC macro en GOLD HOLDOUT fue **0.7107** (17 estudios). El mejor AUC en DEV de la tabla pertenece al EfficientNet-B0 inicial; no debe confundirse con el modelo Focal de la demostración.

Estas cifras proceden de los experimentos del proyecto. La muestra GOLD es pequeña y no permite inferir fiabilidad clínica general.

## Estructura del repositorio

```text
knee-mri-weak-supervision/
├── config/config.yaml
├── src/config.py
├── scripts/run_pipeline.py
├── notebooks/
│   ├── 01_weak_label_extraction.ipynb
│   ├── 02_mri_series_selection.ipynb
│   ├── 03_preprocessing_2_5d.ipynb
│   ├── 04_training_models.ipynb
│   ├── 05_evaluation_ablation_gradcam.ipynb
│   └── 06_demo_inferencia_mri.ipynb
├── requirements.txt
└── README.md
```

## Instalación local

Requisitos: Python, Jupyter/VS Code y acceso autorizado al conjunto de datos de origen. Ejemplo en Windows (CMD):

```cmd
cd C:\ruta\a\knee-mri-weak-supervision
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install ipykernel ipywidgets
```

La configuración `config/config.yaml` establece `data.root: ../RSNA_Knee`, es decir, espera una carpeta `RSNA_Knee` **junto al repositorio**, no dentro de él. Ajustar esa ruta para otras instalaciones.

Se necesitan los CSV de origen, DICOM para regenerar datos, y/o artefactos procesados (`.npy`, metadatos, manifiestos y checkpoints `.pth`) si se usa modo recuperación. **Estos archivos no están publicados en Git** y deben obtenerse o generarse siguiendo las condiciones de acceso del conjunto original. No se garantiza que clonar el repositorio baste para ejecutar la demo.

Comprobar la ruta de datos desde la raíz del proyecto:

```cmd
python src\config.py
```

## Orden de ejecución

| Notebook | Propósito |
| --- | --- |
| 01 | Extracción de etiquetas débiles |
| 02 | Selección de series MRI |
| 03 | Preprocesamiento 2.5D |
| 04 | Entrenamiento y evaluación de arquitecturas |
| 05 | Ablaciones, umbral, métricas, Grad-CAM y HOLDOUT |
| 06 | Demostración interactiva de inferencia sobre GOLD DEV |

Para recuperar los experimentos históricos en el Notebook 05 se utilizan `MODO_ABLACION = "recuperar"` y `RECONSTRUIR_TENSOR_AXIAL = False`. Los modos de reconstrucción o entrenamiento requieren los datos de origen y pueden consumir tiempo y espacio de disco. No reutilizar HOLDOUT para seleccionar parámetros.

La demostración del Notebook 06 usa el checkpoint **`best_ablacion_focal.pth`**, el tensor sagital y el subconjunto GOLD DEV. Muestra probabilidades por etiqueta y su comparación con la referencia GOLD; no reentrena el modelo.

## Limitaciones

- Las etiquetas WEAK son inferidas de texto y pueden contener ruido.
- La representación 2.5D usa cortes seleccionados y no procesa todo el volumen 3D.
- No se realizó una ablación controlada 2D vs. 2.5D vs. 3D.
- Algunos hallazgos son poco frecuentes, lo que dificulta aprender y evaluar su detección.
- Grad-CAM es una explicación visual aproximada, no una localización clínica validada.
- Las métricas de GOLD DEV y HOLDOUT provienen de muestras pequeñas.

## Datos y uso responsable

Respetar las condiciones de la fuente RSNA/Kaggle y no subir informes clínicos, DICOM, datos personales, tensores derivados o checkpoints sin confirmar antes que la licencia y las reglas de acceso lo permiten. `.gitignore` excluye varios formatos grandes, pero también se debe revisar manualmente cada archivo antes de publicarlo.


## Reproducción de evaluaciones

Las evaluaciones de los modelos CNN 2.5D y EfficientNet-B0
pueden reproducirse a partir de los checkpoints entrenados,
sin repetir el entrenamiento.

### Requisitos

- Python 3.12
- Dependencias instaladas desde `requirements.txt`
- Dataset y checkpoints disponibles en `../RSNA_Knee`
- Kernel Jupyter `knee-mri-venv`

### Preparación del entorno

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install nbconvert ipykernel
.venv\Scripts\python.exe -m ipykernel install --user --name knee-mri-venv --display-name "Python (Knee MRI)"
```

### Validar los recursos

```cmd
.venv\Scripts\python.exe scripts\reproduce_evaluation.py
```

### Reproducir las evaluaciones

```cmd
.venv\Scripts\python.exe scripts\reproduce_evaluation.py --execute
```

Los notebooks ejecutados se guardan en `runs/evaluation/`.
La ejecución puede actualizar archivos CSV y PNG derivados
en `RSNA_Knee/processed`.

Este procedimiento recupera los checkpoints existentes y
recalcula las métricas. No reconstruye el entrenamiento
desde los archivos DICOM originales.
