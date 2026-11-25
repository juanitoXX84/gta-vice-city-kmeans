from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
RUTA_DATA = Path(__file__).resolve().parent / 'data'
TITULO = 'Análisis y segmentación de reseñas de GTA: Vice City – The Definitive Edition'
VC_NAVY = '#050d1a'
VC_NAVY_MID = '#0a1628'
VC_PANEL = '#0d1f3c'
VC_PINK = '#ff2d95'
VC_PINK_SOFT = '#ff5fbf'
VC_CYAN = '#00e5ff'
VC_TEAL = '#1de9b6'
VC_PURPLE = '#b24bf3'
VC_TEXT = '#e8f4ff'
VC_TEXT_DIM = '#8eb4d9'
PALETA_CLUSTER = {0: VC_CYAN, 1: VC_PINK, 2: VC_PURPLE, 3: VC_TEAL}
CLUSTERS_INFO = {0: {'nombre': 'Satisfechos habituales', 'descripcion': 'Mayoría de reseñas: recomiendan el juego con tiempo de juego y textos cercanos al promedio general.'}, 1: {'nombre': 'Críticos del remaster', 'descripcion': 'Único grupo con valoraciones negativas; textos algo más largos y críticas al remaster.'}, 2: {'nombre': 'Opiniones destacadas y detalladas', 'descripcion': 'Pocas reseñas muy extensas con muchos votos útiles; alta visibilidad en Steam.'}, 3: {'nombre': 'Veteranos con poco texto', 'descripcion': 'Jugadores con muchísimas horas registradas y comentarios breves.'}}
HALLAZGOS = ['El clúster 0 concentra 451 reseñas (90,2 % del total): segmento dominante con valoración positiva.', 'Solo el clúster 1 agrupa las 38 reseñas negativas (0 % positivas dentro del grupo).', 'Los clústeres 2 y 3 suman 11 reseñas atípicas; el 92,4 % global sigue recomendando el juego.']
RECOMENDACIONES = ['Analizar el clúster «Críticos del remaster» para detectar problemas recurrentes (bugs, controles).', 'Destacar reseñas útiles del clúster mayoritario, donde casi no hay votes_up pese a recomendar.', 'Revisar manualmente clústeres 2 y 3 por textos largos o tiempos de juego extremos.']

def aplicar_estilos() -> None:
    st.markdown(f"""\n        <style>\n        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700&family=Rajdhani:wght@400;500;600;700&display=swap');\n        .stApp {{\n            background: linear-gradient(165deg, {VC_NAVY} 0%, {VC_NAVY_MID} 45%,\n        }}\n        [data-testid="stSidebar"] {{\n            background: linear-gradient(180deg, {VC_PANEL} 0%, {VC_NAVY_MID} 100%);\n            border-right: 1px solid rgba(0, 229, 255, 0.25);\n        }}\n        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,\n        [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label,\n        [data-testid="stSidebar"] .stMarkdown {{\n            color: {VC_TEXT} !important;\n        }}\n        [data-testid="stSidebar"] .stRadio label {{\n            background: rgba(13, 31, 60, 0.6);\n            border: 1px solid rgba(255, 45, 149, 0.2);\n            border-radius: 8px;\n            padding: 0.35rem 0.5rem;\n            margin-bottom: 0.25rem;\n        }}\n        [data-testid="stSidebar"] [data-baseweb="select"],\n        [data-testid="stSidebar"] .stMultiSelect {{\n            border-color: {VC_CYAN} !important;\n        }}\n        .block-container {{\n            padding-top: 1.5rem;\n            max-width: 1200px;\n        }}\n        .vc-header {{\n            text-align: center;\n            padding: 1.75rem 1rem 1.25rem;\n            margin-bottom: 1.5rem;\n            background: linear-gradient(135deg, rgba(13,31,60,0.95) 0%, rgba(18,8,42,0.9) 100%);\n            border: 1px solid rgba(0, 229, 255, 0.2);\n            border-radius: 16px;\n            box-shadow: 0 0 40px rgba(255, 45, 149, 0.08);\n        }}\n        .vc-header h1 {{\n            font-family: 'Orbitron', sans-serif;\n            font-size: clamp(1.1rem, 2.5vw, 1.65rem);\n            font-weight: 700;\n            color: {VC_TEXT};\n            margin: 0 0 0.75rem 0;\n            letter-spacing: 0.04em;\n            line-height: 1.35;\n            text-shadow: 0 0 20px rgba(255, 95, 191, 0.35);\n        }}\n        .vc-header .vc-sub {{\n            font-family: 'Rajdhani', sans-serif;\n            font-size: 1rem;\n            color: {VC_TEXT_DIM};\n            margin: 0;\n        }}\n        .vc-line {{\n            height: 3px;\n            margin: 1rem auto 0;\n            max-width: 420px;\n            border-radius: 2px;\n            background: linear-gradient(90deg, {VC_PINK}, {VC_CYAN}, {VC_PURPLE}, {VC_TEAL});\n            box-shadow: 0 0 12px {VC_PINK_SOFT};\n        }}\n        .vc-subheader {{\n            font-family: 'Orbitron', sans-serif;\n            font-size: 1.25rem;\n            color: {VC_PINK_SOFT};\n            border-left: 4px solid {VC_CYAN};\n            padding-left: 0.75rem;\n            margin: 1.5rem 0 1rem 0;\n        }}\n        .vc-metric {{\n            background: linear-gradient(145deg, rgba(13,31,60,0.9), rgba(5,13,26,0.95));\n            border: 1px solid rgba(0, 229, 255, 0.22);\n            border-radius: 12px;\n            padding: 1.1rem 1rem;\n            text-align: center;\n            min-height: 110px;\n            box-shadow: 0 4px 24px rgba(0,0,0,0.35);\n        }}\n        .vc-metric .vc-m-label {{\n            font-family: 'Rajdhani', sans-serif;\n            font-size: 0.95rem;\n            font-weight: 600;\n            color: {VC_TEXT_DIM};\n            text-transform: uppercase;\n            letter-spacing: 0.06em;\n        }}\n        .vc-metric .vc-m-value {{\n            font-family: 'Orbitron', sans-serif;\n            font-size: 1.85rem;\n            font-weight: 700;\n            color: {VC_TEAL};\n            margin-top: 0.35rem;\n            text-shadow: 0 0 16px rgba(29, 233, 182, 0.25);\n        }}\n        .vc-metric.accent-pink .vc-m-value {{ color: {VC_PINK_SOFT}; }}\n        .vc-metric.accent-cyan .vc-m-value {{ color: {VC_CYAN}; }}\n        .vc-metric.accent-purple .vc-m-value {{ color: {VC_PURPLE}; }}\n        .vc-section-title {{\n            font-family: 'Orbitron', sans-serif;\n            font-size: 1rem;\n            color: {VC_CYAN};\n            margin: 1.75rem 0 0.75rem 0;\n            padding-bottom: 0.35rem;\n            border-bottom: 1px solid rgba(255, 45, 149, 0.35);\n        }}\n        .vc-card {{\n            background: rgba(13, 31, 60, 0.65);\n            border: 1px solid rgba(178, 75, 243, 0.25);\n            border-left: 4px solid {VC_PINK};\n            border-radius: 10px;\n            padding: 1rem 1.15rem;\n            margin-bottom: 0.75rem;\n            font-family: 'Rajdhani', sans-serif;\n            color: {VC_TEXT};\n            font-size: 1.05rem;\n            line-height: 1.45;\n        }}\n        .vc-card strong {{\n            color: {VC_PINK_SOFT};\n            font-family: 'Orbitron', sans-serif;\n            font-size: 0.9rem;\n        }}\n        .vc-list-item {{\n            background: rgba(13, 31, 60, 0.55);\n            border: 1px solid rgba(0, 229, 255, 0.15);\n            border-radius: 8px;\n            padding: 0.85rem 1rem;\n            margin-bottom: 0.5rem;\n            font-family: 'Rajdhani', sans-serif;\n            color: {VC_TEXT};\n            font-size: 1.02rem;\n        }}\n        .vc-list-item span {{\n            color: {VC_CYAN};\n            font-weight: 700;\n            margin-right: 0.35rem;\n        }}\n        .vc-table-wrap {{\n            border: 1px solid rgba(0, 229, 255, 0.2);\n            border-radius: 10px;\n            padding: 0.25rem;\n            background: rgba(5, 13, 26, 0.5);\n            margin-bottom: 1rem;\n        }}\n        [data-testid="stExpander"] {{\n            background: rgba(13, 31, 60, 0.5);\n            border: 1px solid rgba(0, 229, 255, 0.15);\n            border-radius: 8px;\n        }}\n        div[data-testid="stMetric"] {{\n            background: rgba(13, 31, 60, 0.7);\n            border: 1px solid rgba(255, 45, 149, 0.25);\n            border-radius: 10px;\n            padding: 0.5rem;\n        }}\n        </style>\n        """, unsafe_allow_html=True)

def mostrar_encabezado() -> None:
    st.markdown(f'\n        <div class="vc-header">\n            <h1>{TITULO}</h1>\n            <p class="vc-sub">Minería de datos · K-Means · Reseñas Steam en español</p>\n            <div class="vc-line"></div>\n        </div>\n        ', unsafe_allow_html=True)

def estilo_plotly(fig):
    fig.update_layout(template='plotly_dark', paper_bgcolor=VC_NAVY_MID, plot_bgcolor=VC_PANEL, font=dict(family='Rajdhani, Segoe UI, sans-serif', color=VC_TEXT, size=13), title=dict(font=dict(family='Orbitron, sans-serif', size=17, color=VC_PINK_SOFT)), margin=dict(l=52, r=28, t=64, b=52), legend=dict(bgcolor='rgba(13,31,60,0.92)', bordercolor=VC_CYAN, borderwidth=1, font=dict(color=VC_TEXT)))
    fig.update_xaxes(gridcolor='rgba(0,229,255,0.12)', zerolinecolor='rgba(255,45,149,0.25)', linecolor='rgba(142,180,217,0.4)', title_font=dict(color=VC_CYAN))
    fig.update_yaxes(gridcolor='rgba(0,229,255,0.12)', zerolinecolor='rgba(255,45,149,0.25)', linecolor='rgba(142,180,217,0.4)', title_font=dict(color=VC_CYAN))
    return fig

def mapa_colores_cluster(df: pd.DataFrame, col: str) -> dict:
    return {str(val): PALETA_CLUSTER.get(int(val), VC_TEXT_DIM) for val in df[col].unique()}

def mapa_colores_etiqueta(df: pd.DataFrame) -> dict:
    salida = {}
    for etiqueta in df['etiqueta'].unique():
        try:
            cid = int(str(etiqueta).split('–')[0].strip())
        except ValueError:
            cid = 0
        salida[etiqueta] = PALETA_CLUSTER.get(cid, VC_TEXT_DIM)
    return salida

def tarjeta_metrica(etiqueta: str, valor, clase: str='') -> str:
    return f'\n    <div class="vc-metric {clase}">\n        <div class="vc-m-label">{etiqueta}</div>\n        <div class="vc-m-value">{valor}</div>\n    </div>\n    '

def titulo_seccion(texto: str, nivel: int=2) -> None:
    tag = 'h2' if nivel == 2 else 'h3'
    st.markdown(f'<{tag} class="vc-subheader">{texto}</{tag}>', unsafe_allow_html=True)

def titulo_tabla(texto: str) -> None:
    st.markdown(f'<p class="vc-section-title">{texto}</p>', unsafe_allow_html=True)

@st.cache_data
def cargar_datos() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    original = pd.read_csv(RUTA_DATA / 'reseñas_gta_vice_city.csv')
    procesado = pd.read_csv(RUTA_DATA / 'dataset_procesado.csv')
    segmentado = pd.read_csv(RUTA_DATA / 'dataset_segmentado.csv')
    return (original, procesado, segmentado)

def filtrar_datos(df: pd.DataFrame, clusters: list[int], recomendacion: str, anios: list[int]) -> pd.DataFrame:
    salida = df[df['cluster'].isin(clusters)]
    if recomendacion == 'Solo positivas':
        salida = salida[salida['recommended_num'] == 1]
    elif recomendacion == 'Solo negativas':
        salida = salida[salida['recommended_num'] == 0]
    if anios:
        salida = salida[salida['anio_publicacion'].isin(anios)]
    return salida

def sidebar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header('Filtros')
    opciones_cluster = {c: f"{c} – {CLUSTERS_INFO[c]['nombre']}" for c in sorted(df['cluster'].unique())}
    elegidos = st.sidebar.multiselect('Clúster', options=list(opciones_cluster.keys()), default=list(opciones_cluster.keys()), format_func=lambda c: opciones_cluster[c])
    recomendacion = st.sidebar.radio('Recomendación', ['Todas', 'Solo positivas', 'Solo negativas'])
    anios_disp = sorted(df['anio_publicacion'].dropna().unique().astype(int))
    anios = st.sidebar.multiselect('Año de publicación', anios_disp, default=anios_disp)
    if not elegidos:
        st.sidebar.warning('Selecciona al menos un clúster.')
    return filtrar_datos(df, elegidos, recomendacion, anios)

def metricas_generales(df: pd.DataFrame) -> None:
    total = len(df)
    pct_pos = (df['recommended_num'] == 1).mean() * 100 if total else 0
    pct_neg = (df['recommended_num'] == 0).mean() * 100 if total else 0
    horas = df['playtime_forever'].mean() / 60 if total else 0
    (c1, c2, c3, c4) = st.columns(4)
    with c1:
        st.markdown(tarjeta_metrica('Total de reseñas', total, 'accent-cyan'), unsafe_allow_html=True)
    with c2:
        st.markdown(tarjeta_metrica('% positivas', f'{pct_pos:.1f} %', 'accent-cyan'), unsafe_allow_html=True)
    with c3:
        st.markdown(tarjeta_metrica('% negativas', f'{pct_neg:.1f} %', 'accent-pink'), unsafe_allow_html=True)
    with c4:
        st.markdown(tarjeta_metrica('Promedio horas jugadas', f'{horas:.1f} h', 'accent-purple'), unsafe_allow_html=True)

def pagina_general(df: pd.DataFrame) -> None:
    titulo_seccion('Análisis general')
    metricas_generales(df)
    if df.empty:
        st.info('No hay datos con los filtros actuales.')
        return
    etiqueta = df['recommended_num'].map({1: 'Positiva', 0: 'Negativa'})
    conteo = etiqueta.value_counts().reset_index()
    conteo.columns = ['Recomendación', 'Cantidad']
    fig1 = px.bar(conteo, x='Recomendación', y='Cantidad', title='Distribución de recomendaciones', color='Recomendación', color_discrete_map={'Positiva': VC_TEAL, 'Negativa': VC_PINK})
    fig1.update_layout(showlegend=False)
    estilo_plotly(fig1)
    st.plotly_chart(fig1, use_container_width=True)
    df_plot = df.copy()
    df_plot['horas_juego'] = df_plot['playtime_forever'] / 60
    fig2 = px.histogram(df_plot, x='horas_juego', nbins=30, title='Distribución del tiempo de juego (horas)', labels={'horas_juego': 'Horas totales jugadas', 'count': 'Frecuencia'}, color_discrete_sequence=[VC_CYAN])
    estilo_plotly(fig2)
    st.plotly_chart(fig2, use_container_width=True)
    fig3 = px.histogram(df, x='votes_up', title='Distribución de votos útiles', labels={'votes_up': 'Votos útiles', 'count': 'Frecuencia'}, color_discrete_sequence=[VC_PURPLE])
    estilo_plotly(fig3)
    st.plotly_chart(fig3, use_container_width=True)

def tabla_resumen_cluster(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for cluster in sorted(df['cluster'].unique()):
        sub = df[df['cluster'] == cluster]
        filas.append({'cluster': cluster, 'nombre': CLUSTERS_INFO.get(int(cluster), {}).get('nombre', ''), 'n': len(sub), 'promedio_horas': round(sub['playtime_forever'].mean() / 60, 1), 'promedio_votes_up': round(sub['votes_up'].mean(), 2), 'pct_positivas': round(sub['recommended_num'].mean() * 100, 1), 'promedio_longitud': round(sub['longitud_texto'].mean(), 1)})
    return pd.DataFrame(filas)

def pagina_segmentacion(df: pd.DataFrame, df_completo: pd.DataFrame) -> None:
    titulo_seccion('Segmentación mediante K-Means')
    k_total = df_completo['cluster'].nunique()
    st.markdown(tarjeta_metrica('Total de clústeres (modelo K=4)', k_total, 'accent-pink'), unsafe_allow_html=True)
    if df.empty:
        st.info('No hay datos con los filtros actuales.')
        return
    conteo = df['cluster'].value_counts().sort_index().reset_index()
    conteo.columns = ['cluster', 'reseñas']
    conteo['nombre'] = conteo['cluster'].map(lambda c: CLUSTERS_INFO[int(c)]['nombre'])
    fig_dist = px.bar(conteo, x='nombre', y='reseñas', title='Distribución de reseñas por clúster (filtros aplicados)', labels={'nombre': 'Clúster', 'reseñas': 'Cantidad'}, color='cluster', color_discrete_map=mapa_colores_cluster(conteo, 'cluster'))
    estilo_plotly(fig_dist)
    st.plotly_chart(fig_dist, use_container_width=True)
    df_sc = df.copy()
    df_sc['etiqueta'] = df_sc['cluster'].map(lambda c: f"{c} – {CLUSTERS_INFO[int(c)]['nombre']}")
    fig_sc = px.scatter(df_sc, x='playtime_forever', y='votes_up', color='etiqueta', title='Clústeres: tiempo de juego vs. votos útiles', labels={'playtime_forever': 'Minutos jugados', 'votes_up': 'Votos útiles'}, opacity=0.75, color_discrete_map=mapa_colores_etiqueta(df_sc))
    estilo_plotly(fig_sc)
    st.plotly_chart(fig_sc, use_container_width=True)
    resumen = tabla_resumen_cluster(df)
    fig_h = px.bar(resumen, x='nombre', y='promedio_horas', title='Tiempo promedio de juego por clúster (horas)', labels={'nombre': 'Clúster', 'promedio_horas': 'Horas promedio'}, color='cluster', color_discrete_map=mapa_colores_cluster(resumen, 'cluster'))
    fig_pct = px.bar(resumen, x='nombre', y='pct_positivas', title='Porcentaje de recomendaciones positivas por clúster', labels={'nombre': 'Clúster', 'pct_positivas': '% positivas'}, color='cluster', color_discrete_map=mapa_colores_cluster(resumen, 'cluster'))
    estilo_plotly(fig_h)
    estilo_plotly(fig_pct)
    (col_a, col_b) = st.columns(2)
    with col_a:
        st.plotly_chart(fig_h, use_container_width=True)
    with col_b:
        st.plotly_chart(fig_pct, use_container_width=True)
    titulo_tabla('Estadísticas descriptivas por clúster')
    desc = df.groupby('cluster')[['playtime_forever', 'votes_up', 'longitud_texto', 'recommended_num']].describe().round(2)
    st.markdown('<div class="vc-table-wrap">', unsafe_allow_html=True)
    st.dataframe(desc, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    titulo_tabla('Tabla comparativa')
    st.markdown('<div class="vc-table-wrap">', unsafe_allow_html=True)
    st.dataframe(resumen, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    titulo_tabla('Perfiles de clúster')
    for (cid, info) in CLUSTERS_INFO.items():
        if cid in df['cluster'].values or cid in df_completo['cluster'].values:
            st.markdown(f"""<div class="vc-card"><strong>Clúster {cid}: {info['nombre']}</strong> — {info['descripcion']}</div>""", unsafe_allow_html=True)
    titulo_tabla('Hallazgos (Etapa 5)')
    for (i, h) in enumerate(HALLAZGOS, 1):
        st.markdown(f'<div class="vc-list-item"><span>{i}.</span>{h}</div>', unsafe_allow_html=True)
    titulo_tabla('Recomendaciones (Etapa 5)')
    for (i, r) in enumerate(RECOMENDACIONES, 1):
        st.markdown(f'<div class="vc-list-item"><span>{i}.</span>{r}</div>', unsafe_allow_html=True)

def main() -> None:
    st.set_page_config(page_title='GTA Vice City – Reseñas', layout='wide')
    aplicar_estilos()
    mostrar_encabezado()
    (original, procesado, segmentado) = cargar_datos()
    with st.expander('Fuentes de datos'):
        st.write(f'- Original: {len(original)} filas | Procesado: {len(procesado)} filas | Segmentado (principal): {len(segmentado)} filas')
    df_filtrado = sidebar_filtros(segmentado)
    pagina = st.sidebar.radio('Sección', ['Análisis general', 'Segmentación K-Means'])
    if pagina == 'Análisis general':
        pagina_general(df_filtrado)
    else:
        pagina_segmentacion(df_filtrado, segmentado)
if __name__ == '__main__':
    main()
