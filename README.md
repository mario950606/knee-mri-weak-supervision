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
├── config/
│   └── config.yaml
├── src/
│   └── config.py
├── data/
│   └── README.md
├── scripts/
│   ├── run_pipeline.py
│   ├── prepare_rebuild.py
│   ├── run_full_rebuild.py
│   ├── reproduce_evaluation.py
│   └── reproduce_project.py
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


## Reproducción unificada del proyecto

El repositorio proporciona un procedimiento automatizado para verificar
la reconstrucción de datos MRI y reproducir las evaluaciones de los
modelos CNN 2.5D y EfficientNet-B0.

### Requisitos previos

- Python 3.12 y dependencias de `requirements.txt`.
- Kernel Jupyter `knee-mri-venv`.
- Datos RSNA_Knee disponibles según `config/config.yaml`.
- Checkpoints de los modelos previamente entrenados.
- Reconstrucciones de los Notebooks 01, 02 y 03 disponibles
  en `runs/full_rebuild/`.

### Verificar la reconstrucción de datos

Desde la raíz del repositorio:

```cmd
.venv\Scripts\python.exe scripts\reproduce_project.py
```

Este comando compara los resultados reconstruidos con los históricos:

- 500 estudios con etiquetas débiles.
- 546 series MRI seleccionadas.
- 546 tensores MRI 2.5D, píxel por píxel.
- Metadatos de los 546 estudios.

La verificación es de solo lectura y no modifica archivos.

### Reproducir las evaluaciones e inferencias

```cmd
.venv\Scripts\python.exe scripts\reproduce_project.py --execute
```

Este comando:

1. Verifica la reconstrucción de las etapas 01–03.
2. Ejecuta el Notebook 04 recuperando los modelos CNN y EfficientNet-B0.
3. Ejecuta el Notebook 05 para recalcular ablaciones, métricas
   GOLD DEV/HOLDOUT y Grad-CAM.
4. Ejecuta el Notebook 06 con una demostración de inferencia.

### Resultados esperados

| Experimento | AUC macro |
|---|---:|
| CNN desde cero, GOLD DEV | 0.6614 |
| EfficientNet-B0, GOLD DEV | 0.7665 |
| Weighted BCE sagital, GOLD DEV | 0.7360 |
| Weighted Focal sagital, GOLD DEV | 0.7541 |
| Weighted Focal axial, GOLD DEV | 0.7061 |
| Weighted Focal sagital, GOLD HOLDOUT | 0.7107 |

### Archivos generados

- `runs/evaluation/`: notebooks 04 y 05 ejecutados.
- `runs/full_rebuild/`: reconstrucciones 01–03 y
  notebook 06 ejecutado.
- `RSNA_Knee/processed/`: algunos CSV y PNG derivados
  que pueden actualizarse al ejecutar los notebooks 04 y 05.

La carpeta `runs/` está excluida mediante `.gitignore`.

### Alcance de la reproducibilidad

El comando unificado verifica las reconstrucciones previamente
generadas de las etapas 01–03 y ejecuta las etapas 04–06
utilizando checkpoints existentes.

No reconstruye automáticamente las etapas 01–03 desde cero
ni vuelve a entrenar los modelos.

La reconstrucción de datos 01–03 fue comprobada por separado
y produjo resultados idénticos a los archivos históricos.
```
### Comando unificado de reproducción


### Comando unificado de reproducción

Desde la raíz del repositorio, ejecutar:

```cmd
.venv\Scripts\python.exe scripts\reproduce_project.py --rebuild --execute
```

Este comando realiza las siguientes operaciones:

1. Prepara o reutiliza las reconstrucciones de los Notebooks 01, 02 y 03.
2. Comprueba que las etiquetas WEAK, el manifiesto sagital, el tensor MRI 2.5D y sus metadatos coincidan con los archivos históricos.
3. Ejecuta los Notebooks 04 y 05 recuperando los checkpoints previamente entrenados.
4. Ejecuta el Notebook 06 para demostrar la inferencia de patologías de rodilla.

Las reconstrucciones se almacenan en `runs/full_rebuild/` y los notebooks de evaluación ejecutados se guardan en `runs/evaluation/`.

**Alcance y limitaciones:**

- Si las reconstrucciones ya existen, se reutilizan y verifican sin generarlas nuevamente.
- Si faltan todas las reconstrucciones, el ejecutor intenta generarlas a partir de los datos de entrada disponibles.
- El procedimiento depende de los CSV, inventarios, archivos DICOM, tensores de referencia y checkpoints configurados localmente.
- El comando no vuelve a entrenar los modelos desde pesos iniciales.
- Las evaluaciones pueden actualizar CSV y PNG derivados en `RSNA_Knee/processed/`.
- No se garantiza la ejecución únicamente con clonar el repositorio, porque los datos y checkpoints no están incluidos en GitHub.
