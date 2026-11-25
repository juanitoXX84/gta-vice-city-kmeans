from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
RUTA_PROCESADO = Path(__file__).resolve().parent / 'data' / 'dataset_procesado.csv'
RUTA_SEGMENTADO = Path(__file__).resolve().parent / 'data' / 'dataset_segmentado.csv'
CARPETA_GRAFICAS = Path(__file__).resolve().parent / 'graficas'
VARIABLES = ['recommended_num_escalada', 'playtime_forever_escalada', 'votes_up_escalada', 'longitud_texto_escalada']
VALORES_K = [2, 3, 4, 5, 6]
SEMILLA = 42

def cargar_datos() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(RUTA_PROCESADO)
    print(f'Registros cargados: {len(df)}')
    print('\nComprobación de nulos en variables escaladas:')
    print(df[VARIABLES].isnull().sum())
    if df[VARIABLES].isnull().any().any():
        raise ValueError('Hay valores nulos en las variables de entrada.')
    x = df[VARIABLES]
    return (df, x)

def evaluar_k(x: pd.DataFrame) -> pd.DataFrame:
    resultados = []
    for k in VALORES_K:
        modelo = KMeans(n_clusters=k, random_state=SEMILLA, n_init=10)
        etiquetas = modelo.fit_predict(x)
        fila = {'K': k, 'inercia': modelo.inertia_, 'silhouette': silhouette_score(x, etiquetas)}
        resultados.append(fila)
    tabla = pd.DataFrame(resultados)
    print('\n' + '=' * 60)
    print('EVALUACIÓN DE K (2 a 6)')
    print('=' * 60)
    print(tabla.to_string(index=False, float_format=lambda v: f'{v:.4f}'))
    return tabla

def grafica_codo(tabla: pd.DataFrame) -> None:
    CARPETA_GRAFICAS.mkdir(parents=True, exist_ok=True)
    (fig, ax) = plt.subplots(figsize=(8, 5))
    ax.plot(tabla['K'], tabla['inercia'], marker='o', linewidth=2, color='#2980b9')
    ax.set_title('Método del codo: inercia según el número de clústeres')
    ax.set_xlabel('Número de clústeres (K)')
    ax.set_ylabel('Inercia (suma de distancias al centroide)')
    ax.set_xticks(VALORES_K)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    ruta = CARPETA_GRAFICAS / 'metodo_codo.png'
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
    print(f'\nGráfica del codo guardada en: {ruta}')

def elegir_k(tabla: pd.DataFrame) -> int:
    mejoras = []
    inercias = tabla['inercia'].tolist()
    for i in range(1, len(inercias)):
        mejoras.append(inercias[i - 1] - inercias[i])
    k_codo = VALORES_K[-1]
    for (i, mejora) in enumerate(mejoras):
        if i >= 1 and mejora < 0.45 * mejoras[0]:
            k_codo = VALORES_K[i]
            break
    k_silhouette = int(tabla.loc[tabla['silhouette'].idxmax(), 'K'])
    print('\n' + '=' * 60)
    print('SELECCIÓN DE K')
    print('=' * 60)
    print(f'  Sugerencia por codo (inercia): K = {k_codo}')
    print(f'  Mayor silhouette en la tabla: K = {k_silhouette}')
    if k_codo == k_silhouette:
        k_final = k_codo
        motivo = f'Se eligió K = {k_final} porque el codo y el silhouette coinciden: la inercia deja de bajar con fuerza y la separación entre grupos es la mejor probada.'
    elif abs(k_codo - k_silhouette) == 1:
        k_final = k_silhouette
        motivo = f'Se eligió K = {k_final} por el mejor silhouette, cercano al codo (K = {k_codo}). Ofrece grupos más compactos y separados que valores vecinos.'
    else:
        k_final = k_silhouette
        motivo = f'Se eligió K = {k_final} por tener el coeficiente Silhouette más alto. El codo sugirió K = {k_codo}, pero {k_final} agrupa mejor los datos en 4 dimensiones.'
    print(f'\n  K seleccionado: {k_final}')
    print(f'  Justificación: {motivo}')
    return k_final

def entrenar_final(x: pd.DataFrame, k: int) -> tuple[KMeans, pd.Series]:
    modelo = KMeans(n_clusters=k, random_state=SEMILLA, n_init=10)
    etiquetas = modelo.fit_predict(x)
    print('\n' + '=' * 60)
    print(f'MODELO FINAL (K = {k})')
    print('=' * 60)
    print('\nCentroides (variables escaladas):')
    centroides = pd.DataFrame(modelo.cluster_centers_, columns=VARIABLES)
    centroides.index.name = 'cluster'
    print(centroides.to_string(float_format=lambda v: f'{v:.4f}'))
    print('\nReseñas por clúster:')
    conteos = pd.Series(etiquetas).value_counts().sort_index()
    for (clu, cant) in conteos.items():
        print(f'  Clúster {clu}: {cant} reseñas')
    return (modelo, pd.Series(etiquetas, name='cluster'))

def grafica_dispersion(x: pd.DataFrame, etiquetas: pd.Series, k: int) -> None:
    (fig, ax) = plt.subplots(figsize=(9, 6))
    datos = x.copy()
    datos['cluster'] = etiquetas
    var_x = 'playtime_forever_escalada'
    var_y = 'longitud_texto_escalada'
    sns.scatterplot(data=datos, x=var_x, y=var_y, hue='cluster', palette='tab10', alpha=0.7, ax=ax)
    ax.set_title(f'Clústeres K-Means (K = {k}): tiempo de juego vs. longitud del texto')
    ax.set_xlabel('Tiempo de juego (escalado)')
    ax.set_ylabel('Longitud del texto (escalado)')
    ax.legend(title='Clúster', loc='best')
    fig.tight_layout()
    ruta = CARPETA_GRAFICAS / 'dispersion_clusters.png'
    fig.savefig(ruta, dpi=120)
    plt.close(fig)
    print(f'\nGráfica de dispersión guardada en: {ruta}')

def comparar_configuraciones(x: pd.DataFrame, k_final: int, tabla: pd.DataFrame) -> None:
    k_alterno = 2 if k_final != 2 else 3
    print('\n' + '=' * 60)
    print(f'COMPARACIÓN: K = {k_final} vs K = {k_alterno}')
    print('=' * 60)
    fila_final = tabla[tabla['K'] == k_final].iloc[0]
    fila_alt = tabla[tabla['K'] == k_alterno].iloc[0]
    for k in (k_final, k_alterno):
        modelo = KMeans(n_clusters=k, random_state=SEMILLA, n_init=10)
        etiquetas = modelo.fit_predict(x)
        conteos = pd.Series(etiquetas).value_counts().sort_index()
        print(f'\n  K = {k}')
        print(f'    Grupos: {k}')
        print(f'    Inercia: {modelo.inertia_:.4f}')
        print(f'    Silhouette: {silhouette_score(x, etiquetas):.4f}')
        dist = {int(c): int(n) for (c, n) in conteos.items()}
        print(f'    Distribución: {dist}')
    print(f"\n  Diferencias:\n    - K = {k_alterno} tiene menos grupos; la inercia es {fila_alt['inercia']:.2f} vs {fila_final['inercia']:.2f} en K = {k_final} (a más K, menor inercia).\n    - Silhouette: K = {k_alterno} = {fila_alt['silhouette']:.4f}; K = {k_final} = {fila_final['silhouette']:.4f}.\n    - Con K = {k_final} la segmentación es más fina y suele describir mejor perfiles distintos (experiencia, texto, votos).")

def guardar_segmentado(df: pd.DataFrame, etiquetas: pd.Series) -> None:
    salida = df.copy()
    salida['cluster'] = etiquetas.astype(int)
    salida.to_csv(RUTA_SEGMENTADO, index=False, encoding='utf-8-sig')
    asignados = salida['cluster'].notna().sum()
    print('\n' + '=' * 60)
    print('ARCHIVO GUARDADO')
    print('=' * 60)
    print(f'  Ruta: {RUTA_SEGMENTADO}')
    print(f'  Reseñas con clúster asignado: {asignados} / {len(salida)}')
    if asignados != len(salida):
        raise ValueError('No todas las reseñas tienen clúster asignado.')

def main() -> None:
    (df, x) = cargar_datos()
    tabla = evaluar_k(x)
    grafica_codo(tabla)
    k_final = elegir_k(tabla)
    (_, etiquetas) = entrenar_final(x, k_final)
    grafica_dispersion(x, etiquetas, k_final)
    comparar_configuraciones(x, k_final, tabla)
    guardar_segmentado(df, etiquetas)
    print(f'\n>>> K seleccionado para el proyecto: {k_final}')
    print('>>> Etapa 4 completada. No se ha creado el dashboard.')
if __name__ == '__main__':
    main()
