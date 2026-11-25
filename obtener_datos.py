import json
import time
from pathlib import Path
import pandas as pd
import requests
APP_ID = 1546990
NOMBRE_JUEGO = 'Grand Theft Auto: Vice City – The Definitive Edition'
META_REGISTROS = 500
REGISTROS_POR_PAGINA = 100
PAUSA_SEGUNDOS = 1.0
API_URL = 'https://api.steampowered.com/IUserReviewsService/GetAppReviews/v1/'
RUTA_CSV = Path(__file__).resolve().parent / 'data' / 'reseñas_gta_vice_city.csv'

def comprobar_juego(app_id: int) -> None:
    url = 'https://store.steampowered.com/api/appdetails'
    respuesta = requests.get(url, params={'appids': app_id, 'l': 'spanish'}, timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
    respuesta.raise_for_status()
    datos = respuesta.json().get(str(app_id), {})
    if not datos.get('success'):
        raise RuntimeError(f'No se pudo verificar la ficha de Steam para el appid {app_id}.')
    nombre = datos['data']['name']
    if 'Vice City' not in nombre or 'Definitive' not in nombre:
        raise RuntimeError(f'El appid {app_id} corresponde a «{nombre}», no al juego esperado.')
    print(f'Juego verificado: {nombre} (appid {app_id})')

def obtener_pagina_reseñas(cursor: str) -> dict:
    cuerpo_peticion = {'appid': APP_ID, 'filter': 1, 'languages': ['spanish'], 'review_type': 0, 'purchase_type': 1, 'num_per_page': REGISTROS_POR_PAGINA, 'cursor': cursor, 'filter_offtopic_activity': True}
    respuesta = requests.get(API_URL, params={'format': 'json', 'input_json': json.dumps(cuerpo_peticion, ensure_ascii=False, separators=(',', ':'))}, timeout=30)
    if respuesta.status_code == 429:
        raise RuntimeError('Steam aplicó límite de velocidad (HTTP 429). Espera unos minutos y vuelve a ejecutar.')
    if respuesta.status_code == 403:
        raise RuntimeError('Acceso denegado a la API (HTTP 403). Comprueba tu conexión o inténtalo más tarde.')
    respuesta.raise_for_status()
    carga = respuesta.json()
    cuerpo = carga.get('response')
    if not isinstance(cuerpo, dict) or not isinstance(cuerpo.get('reviews'), list):
        raise RuntimeError('La respuesta de Steam no tiene el formato esperado.')
    return cuerpo

def descargar_reseñas() -> list[dict]:
    reseñas_por_id: dict[str, dict] = {}
    cursor = '*'
    total_disponible = None
    while len(reseñas_por_id) < META_REGISTROS:
        pagina = obtener_pagina_reseñas(cursor)
        if total_disponible is None:
            total_disponible = pagina.get('total_matching')
            resumen = pagina.get('query_summary', {})
            print(f"Reseñas en español disponibles según Steam: {total_disponible} (puntuación: {resumen.get('review_score_desc', 'N/D')})")
        lote = pagina.get('reviews', [])
        if not lote:
            break
        for item in lote:
            if item.get('language') != 'spanish':
                continue
            id_reseña = str(item['recommendationid'])
            if id_reseña in reseñas_por_id:
                continue
            reseñas_por_id[id_reseña] = {'recommendationid': id_reseña, 'review_text': item.get('review', '').strip(), 'recommended': bool(item.get('voted_up')), 'timestamp_created': int(item.get('timestamp_created', 0)), 'votes_up': int(item.get('votes_up', 0)), 'playtime_forever': int(item.get('author', {}).get('playtime_forever', 0))}
        siguiente_cursor = pagina.get('cursor')
        if not siguiente_cursor or siguiente_cursor == cursor:
            break
        cursor = siguiente_cursor
        time.sleep(PAUSA_SEGUNDOS)
    lista = list(reseñas_por_id.values())
    print(f'Reseñas descargadas (sin duplicados): {len(lista)}')
    if len(lista) < META_REGISTROS:
        print(f'AVISO: solo se obtuvieron {len(lista)} reseñas reales en español (objetivo: {META_REGISTROS}).')
    return lista

def guardar_csv(reseñas: list[dict]) -> None:
    RUTA_CSV.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(reseñas)
    columnas = ['recommendationid', 'review_text', 'recommended', 'timestamp_created', 'votes_up', 'playtime_forever']
    df = df[columnas]
    df.to_csv(RUTA_CSV, index=False, encoding='utf-8-sig')

def explorar_datos() -> None:
    print('\n--- Exploración inicial del dataset ---\n')
    df = pd.read_csv(RUTA_CSV)
    print('Primeros 10 registros:')
    print(df.head(10))
    print()
    print(f'Filas: {df.shape[0]}, columnas: {df.shape[1]}')
    print()
    print('Nombres de columnas:')
    print(list(df.columns))
    print()
    print('Tipos de datos:')
    print(df.dtypes)
    print()
    print('Estadísticas descriptivas:')
    print(df.describe(include='all'))
    print()
    print('Valores nulos por columna:')
    print(df.isnull().sum())
    print()
    duplicados_id = df.duplicated(subset=['recommendationid']).sum()
    duplicados_texto = df.duplicated(subset=['review_text']).sum()
    print(f'Registros duplicados (mismo recommendationid): {duplicados_id}')
    print(f'Registros duplicados (mismo review_text): {duplicados_texto}')
    print()
    print(f'Total de reseñas en el archivo: {len(df)}')

def main() -> None:
    print(f'Proyecto: análisis de reseñas de {NOMBRE_JUEGO}\n')
    comprobar_juego(APP_ID)
    reseñas = descargar_reseñas()
    if not reseñas:
        raise RuntimeError('No se obtuvo ninguna reseña. Revisa la conexión o la API de Steam.')
    guardar_csv(reseñas)
    print(f'Archivo guardado en: {RUTA_CSV}')
    explorar_datos()
if __name__ == '__main__':
    main()
