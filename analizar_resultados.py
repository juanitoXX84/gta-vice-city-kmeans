from pathlib import Path
import pandas as pd
from sklearn.preprocessing import StandardScaler
RUTA_SEGMENTADO = Path(__file__).resolve().parent / 'data' / 'dataset_segmentado.csv'
VARIABLES_NUM = ['recommended_num', 'playtime_forever', 'votes_up', 'longitud_texto']
VARIABLES_ESC = ['recommended_num_escalada', 'playtime_forever_escalada', 'votes_up_escalada', 'longitud_texto_escalada']

def cargar_datos() -> pd.DataFrame:
    df = pd.read_csv(RUTA_SEGMENTADO)
    if len(df) != 500:
        print(f'AVISO: se esperaban 500 filas, hay {len(df)}.')
    if df['cluster'].isnull().any():
        raise ValueError('Hay reseñas sin clúster asignado.')
    return df

def resumen_por_cluster(df: pd.DataFrame) -> pd.DataFrame:
    grupos = []
    for cluster in sorted(df['cluster'].unique()):
        sub = df[df['cluster'] == cluster]
        fila = {'cluster': int(cluster), 'cantidad_reseñas': len(sub), 'promedio_playtime_min': round(sub['playtime_forever'].mean(), 1), 'promedio_votes_up': round(sub['votes_up'].mean(), 2), 'pct_recomienda': round(sub['recommended_num'].mean() * 100, 1), 'promedio_longitud_texto': round(sub['longitud_texto'].mean(), 1)}
        grupos.append(fila)
    return pd.DataFrame(grupos)

def estadisticas_descriptivas(df: pd.DataFrame) -> pd.DataFrame:
    columnas = ['playtime_forever', 'votes_up', 'longitud_texto', 'recommended_num']
    return df.groupby('cluster')[columnas].describe().round(2)

def centroides_escala_original(df: pd.DataFrame) -> pd.DataFrame:
    scaler = StandardScaler()
    scaler.fit(df[VARIABLES_NUM])
    medias_esc = df.groupby('cluster')[VARIABLES_ESC].mean()
    medias_original = scaler.inverse_transform(medias_esc)
    tabla = pd.DataFrame(medias_original, index=medias_esc.index, columns=VARIABLES_NUM)
    tabla.index.name = 'cluster'
    return tabla.round(2)

def describir_cluster(fila: pd.Series) -> str:
    c = int(fila['cluster'])
    if fila['pct_recomienda'] < 50:
        return 'Grupo crítico: no recomienda el juego'
    if fila['promedio_votes_up'] >= 2.0 and fila['promedio_longitud_texto'] >= 200:
        return 'Reseñas visibles y extensas'
    if fila['promedio_playtime_min'] >= 4000:
        return 'Jugadores veteranos, textos breves'
    return 'Perfil mayoritario: juego típico y valoración positiva'

def asignar_nombres(tabla: pd.DataFrame) -> dict[int, str]:
    nombres = {}
    for (_, fila) in tabla.iterrows():
        c = int(fila['cluster'])
        pct_neg = 100 - fila['pct_recomienda']
        if pct_neg > 50:
            nombres[c] = 'Críticos del remaster'
        elif fila['promedio_votes_up'] >= 2.0 and fila['promedio_longitud_texto'] >= 150:
            nombres[c] = 'Opiniones destacadas y detalladas'
        elif fila['promedio_playtime_min'] >= 4000:
            nombres[c] = 'Veteranos con poco texto'
        else:
            nombres[c] = 'Satisfechos habituales'
    return nombres

def interpretar_centroides(centroides: pd.DataFrame, nombres: dict[int, str]) -> None:
    print('\nInterpretación de centroides (variables en escala original):')
    for (cluster, fila) in centroides.iterrows():
        nombre = nombres.get(int(cluster), f'Clúster {cluster}')
        print(f'\n  Clúster {int(cluster)} — «{nombre}»')
        print(f"    recommended_num ~ {fila['recommended_num']:.2f} (1=recomienda)")
        print(f"    playtime_forever ~ {fila['playtime_forever']:.0f} min (~{fila['playtime_forever'] / 60:.0f} h)")
        print(f"    votes_up ~ {fila['votes_up']:.2f}")
        print(f"    longitud_texto ~ {fila['longitud_texto']:.0f} caracteres")

def hallazgos(tabla: pd.DataFrame, df: pd.DataFrame) -> None:
    print('\n' + '=' * 60)
    print('HALLAZGOS (respaldados por los datos)')
    print('=' * 60)
    mayor = tabla.loc[tabla['cantidad_reseñas'].idxmax()]
    criticos = tabla.loc[tabla['pct_recomienda'].idxmin()]
    global_pos = df['recommended_num'].mean() * 100
    h1 = f"1. El clúster {int(mayor['cluster'])} concentra {int(mayor['cantidad_reseñas'])} reseñas ({mayor['cantidad_reseñas'] / len(df) * 100:.1f}% del total): el segmento dominante recomienda el juego con tiempos de juego y textos cercanos al promedio general."
    h2 = f"2. Solo el clúster {int(criticos['cluster'])} tiene mayoría de valoraciones negativas ({criticos['pct_recomienda']:.1f}% positivas, {int(criticos['cantidad_reseñas'])} reseñas), lo que coincide con las críticas detectables sin analizar el texto palabra a palabra."
    pequeños = tabla[tabla['cantidad_reseñas'] < 10]
    if len(pequeños) > 0:
        ids = ', '.join((str(int(x)) for x in pequeños['cluster']))
        h3 = f"3. Los clústeres {ids} son muy pequeños ({pequeños['cantidad_reseñas'].tolist()} reseñas); representan perfiles atípicos (muchas horas o reseñas con muchos votos y texto largo), mientras el {global_pos:.1f}% global de reseñas sigue siendo positivo."
    else:
        h3 = f'3. El {global_pos:.1f}% de las 500 reseñas recomiendan el juego; el desbalance limita el peso del grupo negativo.'
    for texto in (h1, h2, h3):
        print(f'\n  {texto}')

def recomendaciones(nombres: dict[int, str], tabla: pd.DataFrame) -> None:
    print('\n' + '=' * 60)
    print('RECOMENDACIONES')
    print('=' * 60)
    critico = tabla.loc[tabla['pct_recomienda'].idxmin(), 'cluster']
    print(f"\n  1. Revisar motivos recurrentes en «{nombres[int(critico)]}» ({int(tabla.loc[tabla['cluster'] == critico, 'cantidad_reseñas'].iloc[0])} reseñas):\n     leer muestras de ese clúster ayuda a priorizar correcciones técnicas o de control citadas en Steam.\n  2. Potenciar la visibilidad de buenas experiencias en el clúster mayoritario «Satisfechos habituales»,\n     donde la mayoría recomienda pero casi no recibe votos útiles (votes_up bajo).\n  3. Estudiar aparte los pocos perfiles «Opiniones destacadas» y «Veteranos»: sus textos o tiempos\n     extremos pueden guiar parches de rendimiento o comunicación con jugadores muy dedicados.\n")

def limitaciones(df: pd.DataFrame, tabla: pd.DataFrame) -> None:
    print('=' * 60)
    print('LIMITACIONES')
    print('=' * 60)
    positivas = df['recommended_num'].sum()
    print(f"\n  - Solo 500 reseñas en español; no representan a toda la base de jugadores en Steam.\n  - Desbalance fuerte: {positivas} recomiendan ({positivas / len(df) * 100:.1f}%) frente a {len(df) - positivas} que no.\n  - Clústeres con pocos casos (p. ej. {tabla['cantidad_reseñas'].min()} reseñas) dificultan generalizar.\n  - K-Means usó recommended_num, playtime, votes_up y longitud; no el contenido semántico del texto.\n  - La longitud del texto no equivale a la opinión: sin NLP ni sentimiento, se pierde matices del mensaje.\n  - K=4 es fijo; otro K podría subdividir o fusionar grupos de forma distinta.\n")

def main() -> None:
    df = cargar_datos()
    print('=' * 60)
    print('ETAPA 5: ANÁLISIS E INTERPRETACIÓN (K = 4)')
    print('=' * 60)
    print(f'Total de reseñas: {len(df)}')
    tabla = resumen_por_cluster(df)
    nombres = asignar_nombres(tabla)
    print('\n' + '=' * 60)
    print('1. CARACTERÍSTICAS POR CLÚSTER')
    print('=' * 60)
    for (_, fila) in tabla.iterrows():
        c = int(fila['cluster'])
        print(f'\n--- Clúster {c}: «{nombres[c]}» ---')
        print(f"  Cantidad de reseñas: {int(fila['cantidad_reseñas'])}")
        print(f"  Promedio tiempo de juego: {fila['promedio_playtime_min']} min")
        print(f"  Promedio votos útiles: {fila['promedio_votes_up']}")
        print(f"  % recomendación positiva: {fila['pct_recomienda']}%")
        print(f"  Longitud media del texto: {fila['promedio_longitud_texto']} caracteres")
        print(f'  Rasgo principal: {describir_cluster(fila)}')
    print('\n' + '=' * 60)
    print('2. TABLA COMPARATIVA')
    print('=' * 60)
    tabla['nombre'] = tabla['cluster'].map(nombres)
    print(tabla.to_string(index=False))
    print('\n' + '=' * 60)
    print('2b. ESTADÍSTICAS DESCRIPTIVAS POR CLÚSTER')
    print('=' * 60)
    print(estadisticas_descriptivas(df))
    print('\n' + '=' * 60)
    print('3. CENTROIDES (escala original, a partir de medias escaladas)')
    print('=' * 60)
    centroides = centroides_escala_original(df)
    print(centroides)
    interpretar_centroides(centroides, nombres)
    print('\n' + '=' * 60)
    print('4. NOMBRES DESCRIPTIVOS ASIGNADOS')
    print('=' * 60)
    for (c, nombre) in sorted(nombres.items()):
        print(f'  Clúster {c}: {nombre}')
    hallazgos(tabla, df)
    recomendaciones(nombres, tabla)
    limitaciones(df, tabla)
    print('\n>>> Etapa 5 completada (sin dashboard ni cambios en los CSV).')
if __name__ == '__main__':
    main()
