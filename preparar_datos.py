from pathlib import Path
import pandas as pd
from sklearn.preprocessing import StandardScaler
RUTA_ORIGINAL = Path(__file__).resolve().parent / 'data' / 'reseñas_gta_vice_city.csv'
RUTA_PROCESADO = Path(__file__).resolve().parent / 'data' / 'dataset_procesado.csv'
VARIABLES_KMEANS = ['recommended_num', 'playtime_forever', 'votes_up', 'longitud_texto']

def mostrar_nulos(df: pd.DataFrame) -> None:
    print('Valores nulos por columna:')
    print(df.isnull().sum())

def tratar_texto_vacio(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    vacios = df['review_text'].isna()
    print(f'\nReseñas con texto vacío o nulo: {vacios.sum()}')
    df.loc[vacios, 'review_text'] = ''
    return df

def revisar_duplicados(df: pd.DataFrame) -> None:
    print('\nRevisión de duplicados:')
    print(f'  Filas completamente iguales: {df.duplicated().sum()}')
    print(f"  Mismo recommendationid: {df.duplicated(subset=['recommendationid']).sum()}")
    repetidos_texto = df.duplicated(subset=['review_text'], keep=False) & (df['review_text'] != '')
    print(f'  Texto repetido entre usuarios distintos: {repetidos_texto.sum()} filas implicadas')
    print('  Acción: no se eliminan (cada recommendationid es un usuario distinto).')

def convertir_tipos_y_fechas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['recommendationid'] = df['recommendationid'].astype('int64')
    df['votes_up'] = pd.to_numeric(df['votes_up'], errors='coerce').astype('int64')
    df['playtime_forever'] = pd.to_numeric(df['playtime_forever'], errors='coerce').astype('int64')
    df['timestamp_created'] = pd.to_numeric(df['timestamp_created'], errors='coerce').astype('int64')
    df['fecha_publicacion'] = pd.to_datetime(df['timestamp_created'], unit='s', utc=True)
    df['anio_publicacion'] = df['fecha_publicacion'].dt.year.astype('int64')
    df['recommended_num'] = df['recommended'].map({True: 1, False: 0, 'True': 1, 'False': 0})
    if df['recommended_num'].isna().any():
        df['recommended_num'] = df['recommended_num'].fillna(df['recommended'].astype(str).str.lower().eq('true').astype(int))
    df['recommended_num'] = df['recommended_num'].astype('int64')
    df['longitud_texto'] = df['review_text'].astype(str).str.len().astype('int64')
    return df

def revisar_atipicos(df: pd.DataFrame) -> None:
    print('\nRevisión de valores atípicos (método IQR):')
    for columna in ('votes_up', 'playtime_forever'):
        q1 = df[columna].quantile(0.25)
        q3 = df[columna].quantile(0.75)
        iqr = q3 - q1
        limite_inf = q1 - 1.5 * iqr
        limite_sup = q3 + 1.5 * iqr
        atipicos = df[(df[columna] < limite_inf) | (df[columna] > limite_sup)]
        print(f'\n  {columna}:')
        print(f'    Q1={q1:.2f}, Q3={q3:.2f}, IQR={iqr:.2f}')
        print(f'    Límites habituales: [{limite_inf:.2f}, {limite_sup:.2f}]')
        print(f'    Registros fuera de IQR: {len(atipicos)}')
    print('\n  Tratamiento aplicado: no se eliminan atípicos.\n    - votes_up: la mayoría tiene 0 votos; valores altos son reseñas destacadas legítimas en Steam.\n    - playtime_forever: los valores altos corresponden a jugadores con muchas horas registradas; son reales y útiles para segmentar perfiles.')

def escalar_variables(df: pd.DataFrame) -> pd.DataFrame:
    scaler = StandardScaler()
    valores_escalados = scaler.fit_transform(df[VARIABLES_KMEANS])
    df = df.copy()
    for (i, nombre) in enumerate(VARIABLES_KMEANS):
        df[f'{nombre}_escalada'] = valores_escalados[:, i]
    return df

def justificar_variables() -> None:
    print('\nVariables seleccionadas para K-Means:')
    print('  - recommended_num: distingue perfiles satisfechos (1) vs. insatisfechos (0).')
    print('  - playtime_forever: separa jugadores con poca o mucha experiencia en el juego.')
    print('  - votes_up: diferencia reseñas con poco o mucho impacto en la comunidad.')
    print('  - longitud_texto: aproxima si la opinión es breve o elaborada (sin NLP avanzado).')
    print('\nStandardScaler: todas comparten escala para que ninguna domine la distancia.')

def main() -> None:
    df_original = pd.read_csv(RUTA_ORIGINAL)
    registros_original = len(df_original)
    print('=' * 60)
    print('ETAPA 3: LIMPIEZA Y PREPARACIÓN')
    print('=' * 60)
    print(f'\nRegistros en el archivo original: {registros_original}')
    print('\n--- 1. Valores nulos ---')
    mostrar_nulos(df_original)
    df = tratar_texto_vacio(df_original)
    revisar_duplicados(df)
    df = convertir_tipos_y_fechas(df)
    print('\nTipos de datos después de la preparación:')
    print(df.dtypes)
    revisar_atipicos(df)
    df = escalar_variables(df)
    justificar_variables()
    columnas_salida = ['recommendationid', 'review_text', 'recommended', 'recommended_num', 'timestamp_created', 'fecha_publicacion', 'anio_publicacion', 'votes_up', 'playtime_forever', 'longitud_texto', *[f'{v}_escalada' for v in VARIABLES_KMEANS]]
    df[columnas_salida].to_csv(RUTA_PROCESADO, index=False, encoding='utf-8-sig')
    registros_final = len(df)
    print('\n' + '=' * 60)
    print('RESULTADO')
    print('=' * 60)
    print(f'Registros originales:        {registros_original}')
    print(f'Registros después de limpieza: {registros_final}')
    print(f'Archivo guardado: {RUTA_PROCESADO}')
    print('\nPrimeras filas del dataset procesado:')
    print(df[columnas_salida].head(5))
if __name__ == '__main__':
    main()
