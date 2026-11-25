# Análisis y segmentación de reseñas de GTA: Vice City – The Definitive Edition mediante K-Means

Proyecto escolar de minería de datos sobre **500 reseñas reales en español** del juego en Steam. Las opiniones se agrupan con **K-Means** usando cuatro variables numéricas escaladas y se exploran en un **dashboard interactivo** (Streamlit + Plotly).

## Objetivo

Obtener reseñas públicas de Steam, prepararlas y segmentarlas en **4 clústeres (K = 4)** para identificar perfiles de jugadores (satisfechos, críticos, reseñas destacadas y veteranos) y presentar los resultados de forma clara.

## Tecnologías

- Python 3.10+
- Pandas, Requests
- Matplotlib, Seaborn
- Scikit-learn (K-Means, StandardScaler, Silhouette)
- Streamlit, Plotly

## Etapas del proyecto

| Etapa | Script | Descripción |
|------|--------|-------------|
| 1 | `obtener_datos.py` | Descarga reseñas en español desde la API pública de Steam (appid **1546990**) |
| 2 | `exploracion.py` | Exploración inicial y gráficas en `graficas/` |
| 3 | `preparar_datos.py` | Limpieza, variables derivadas y escalado → `data/dataset_procesado.csv` |
| 4 | `entrenar_kmeans.py` | Evalúa K = 2…6, entrena K = 4 → `data/dataset_segmentado.csv` |
| 5 | `analizar_resultados.py` | Interpretación de clústeres, hallazgos y recomendaciones |
| 6 | `dashboard.py` | Dashboard interactivo con filtros |

La documentación completa del informe está en **`documentacion_proyecto.pdf`**.

## Cuatro clústeres (K = 4)

| Clúster | Nombre | Reseñas | Idea principal |
|--------|--------|---------|----------------|
| 0 | Satisfechos habituales | 451 | Mayoría; recomiendan el juego |
| 1 | Críticos del remaster | 38 | No recomiendan; críticas al remaster |
| 2 | Opiniones destacadas y detalladas | 4 | Textos largos y muchos votos útiles |
| 3 | Veteranos con poco texto | 7 | Muchas horas jugadas; comentarios breves |

## Variables para K-Means

Tras el escalado con **StandardScaler**:

- `recommended_num_escalada`
- `playtime_forever_escalada`
- `votes_up_escalada`
- `longitud_texto_escalada`

## Estructura de carpetas

```
Proyecto_KMeans/
├── data/
│   ├── reseñas_gta_vice_city.csv
│   ├── dataset_procesado.csv
│   └── dataset_segmentado.csv
├── graficas/
│   ├── distribucion_recomendacion.png
│   ├── distribucion_tiempo_juego.png
│   ├── distribucion_votos_utiles.png
│   ├── metodo_codo.png
│   └── dispersion_clusters.png
├── obtener_datos.py
├── exploracion.py
├── preparar_datos.py
├── entrenar_kmeans.py
├── analizar_resultados.py
├── dashboard.py
├── requirements.txt
├── documentacion_proyecto.pdf
├── README.md
└── .gitignore
```

## Requisitos

- Python 3.10 o superior
- Conexión a internet (solo si vuelves a ejecutar `obtener_datos.py` contra Steam)

## Instalación

Desde la carpeta del proyecto:

```bash
pip install -r requirements.txt
```

## Ejecutar el dashboard

```bash
streamlit run dashboard.py
```

Se abrirá en el navegador (por defecto `http://localhost:8501`).

## Otros scripts (opcional)

```bash
python exploracion.py
python preparar_datos.py
python entrenar_kmeans.py
python analizar_resultados.py
```

No es necesario volver a entrenar el modelo si ya existen los CSV en `data/`.

## Integrantes

- Juan Jose Martinez
- Kevin Gonzales

**Materia:** Base de Datos · **Grupo:** 9-1 · **Maestra:** Julia Garcia

## Licencia y datos

Las reseñas provienen de la API pública de Steam. Este proyecto es con fines académicos.