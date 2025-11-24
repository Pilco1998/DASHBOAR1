import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import unicodedata
from datetime import datetime

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="BANJAE S.A.", 
    page_icon="🌿", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. ESTILOS CSS ---
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {background-color: #f3f4f6;}

    .header-container {
        background-color: #064e3b;
        padding: 2rem;
        border-radius: 0px 0px 15px 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .header-title {
        font-family: 'Arial', sans-serif;
        font-size: 28px;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .header-subtitle {
        color: #a7f3d0;
        font-size: 14px;
        font-weight: 500;
        margin-top: 5px;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e5e7eb;
        text-align: center;
    }
    
    /* Colores específicos para las tarjetas de categorías */
    .category-card {
        border-left: 5px solid #10b981;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. MEMORIA DE DATOS ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        'FECHA', 'CATEGORIA', 'NUM. APLICACION', 'FRECUENCIA (DIAS)', 
        'HAS', 'PRODUCTO 1', 'PRODUCTO 2'
    ])

# --- 4. FUNCIONES DE LIMPIEZA ---
def normalize_text(text):
    if isinstance(text, str):
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        return text.strip().upper()
    return str(text)

def parse_hectares(value):
    val_str = str(value)
    try:
        return float(val_str)
    except:
        clean_str = val_str.replace('(', '').replace(')', '').replace('=', '').strip()
        if '+' in clean_str:
            try:
                parts = clean_str.split('+')
                return sum(float(p.strip()) for p in parts if p.strip())
            except:
                return 0
        try:
            return float(clean_str)
        except:
            return 0

# --- 5. CARGA DE ARCHIVO ---
def load_data_from_file(uploaded_file):
    if uploaded_file:
        try:
            df_preview = pd.read_excel(uploaded_file, header=None, nrows=10)
            header_row_idx = 0
            for i, row in df_preview.iterrows():
                row_text = " ".join([str(x).upper() for x in row.values])
                if "FECHA" in row_text or "CATEGORIA" in row_text:
                    header_row_idx = i
                    break
            
            df = pd.read_excel(uploaded_file, header=header_row_idx)
            df.columns = [normalize_text(col) for col in df.columns]
            
            col_map = {}
            for col in df.columns:
                if "HAS" in col or "HECT" in col: col_map[col] = "HAS"
                elif "FREC" in col or "DIAS" in col: col_map[col] = "FRECUENCIA (DIAS)"
                elif "NUM" in col or "APP" in col: col_map[col] = "NUM. APLICACION"
                elif "FECHA" in col: col_map[col] = "FECHA"
                elif "CATEGORIA" in col: col_map[col] = "CATEGORIA"
                elif "PRODUCTO 1" in col: col_map[col] = "PRODUCTO 1"
                elif "PRODUCTO 2" in col: col_map[col] = "PRODUCTO 2"
            
            df = df.rename(columns=col_map)
            
            if "HAS" in df.columns:
                df["HAS"] = df["HAS"].apply(parse_hectares)
            
            if "FECHA" in df.columns:
                df["FECHA"] = pd.to_datetime(df["FECHA"], dayfirst=True, errors='coerce')

            return df
        except Exception as e:
            st.error(f"Error al leer archivo: {e}")
            return None
    return None

# --- 6. ENCABEZADO ---
st.markdown("""
<div class="header-container">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <div class="header-title">BANJAE S.A.</div>
            <div class="header-subtitle">🚜 Dashboard Operativo - Control Agrícola</div>
        </div>
        <div style="background-color: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 20px; font-size: 13px; font-weight: bold;">
            🟢 En Línea
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 7. BARRA LATERAL + CARGA ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/188/188333.png", width=60)
    st.markdown("### ⚙️ Configuración")
    st.info("👇 **CARGA TU ARCHIVO AQUÍ**")
    uploaded_file = st.file_uploader("Subir Excel", type=["xlsx", "xls"], label_visibility="collapsed")
    
    if uploaded_file:
        df_loaded = load_data_from_file(uploaded_file)
        if df_loaded is not None:
            if st.session_state.data.empty or st.sidebar.button("🔄 Forzar Recarga"):
                st.session_state.data = df_loaded
                st.success("✅ Datos cargados")

# --- 8. CUERPO PRINCIPAL ---
df = st.session_state.data
required_cols = ["FECHA", "CATEGORIA", "HAS"]
has_data = not df.empty and all(col in df.columns for col in required_cols)

tab1, tab2, tab3 = st.tabs(["📊 Resumen Ejecutivo", "🧪 Análisis Insumos", "📝 Gestión de Datos"])

if has_data:
    # --- PESTAÑA 1: RESUMEN ---
    with tab1:
        # 1. TOTALES GENERALES
        st.markdown("##### 📌 Indicadores Globales")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Aplicaciones", f"{len(df)}", "Registros totales")
        with col2:
            st.metric("Hectáreas Tratadas", f"{df['HAS'].sum():,.1f} ha", "Acumulado Total")
        with col3:
            avg_freq = 0
            if "FRECUENCIA (DIAS)" in df.columns:
                df["FRECUENCIA (DIAS)"] = pd.to_numeric(df["FRECUENCIA (DIAS)"], errors='coerce').fillna(0)
                freqs = df[df["FRECUENCIA (DIAS)"] > 0]["FRECUENCIA (DIAS)"]
                if not freqs.empty:
                    avg_freq = freqs.mean()
            st.metric("Frecuencia Promedio", f"{avg_freq:.1f} días", "Entre aplicaciones")

        st.markdown("---")
        
        # 2. DESGLOSE POR TIPO (NUEVA SECCIÓN SOLICITADA)
        st.markdown("##### 🔍 Desglose por Tipo de Aplicación")
        
        # Función auxiliar para contar (flexible con mayúsculas/plurales)
        def count_cat(keyword):
            if "CATEGORIA" in df.columns:
                return df["CATEGORIA"].astype(str).str.upper().str.contains(keyword).sum()
            return 0

        k1, k2, k3, k4 = st.columns(4)
        
        with k1:
            st.metric("🌱 CICLOS", f"{count_cat('CICLO')}", "Aplicaciones")
        with k2:
            st.metric("🍂 FOLIARES", f"{count_cat('FOLIAR')}", "Aplicaciones")
        with k3:
            st.metric("🔄 INTERCICLOS", f"{count_cat('INTER')}", "Aplicaciones")
        with k4:
            st.metric("🛡️ CONTROL", f"{count_cat('CONTROL')}", "Aplicaciones")

        st.markdown("---")

        # 3. GRÁFICOS
        c_left, c_right = st.columns([2, 1])
        with c_left:
            st.markdown("##### 📈 Evolución de Frecuencia")
            if "FRECUENCIA (DIAS)" in df.columns:
                df_chart = df[df["FRECUENCIA (DIAS)"] > 0].sort_values("FECHA")
                if not df_chart.empty:
                    fig_bar = px.bar(
                        df_chart, x="FECHA", y="FRECUENCIA (DIAS)",
                        color_discrete_sequence=["#10b981"],
                        text="FRECUENCIA (DIAS)"
                    )
                    fig_bar.update_layout(
                        plot_bgcolor="white",
                        yaxis=dict(showgrid=True, gridcolor="#f3f4f6"),
                        height=350
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

        with c_right:
            st.markdown("##### 🍃 Distribución Visual")
            fig_pie = px.pie(
                df, names="CATEGORIA", color="CATEGORIA",
                color_discrete_map={
                    "CICLO": "#15803d", 
                    "FOLIAR": "#fbbf24", 
                    "INTERCICLO": "#f59e0b",
                    "CONTROL": "#3b82f6"
                },
                hole=0.6
            )
            fig_pie.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig_pie, use_container_width=True)

        # 4. GRÁFICO COMBINADO
        st.markdown("##### 🚜 Cronograma de Hectáreas (vs Frecuencia)")
        df_sorted = df.sort_values("FECHA")
        fig_combo = go.Figure()

        # Área Verde (Hectáreas)
        fig_combo.add_trace(go.Scatter(
            x=df_sorted['FECHA'], y=df_sorted['HAS'], name='Hectáreas',
            mode='lines', fill='tozeroy',
            line=dict(width=0.5, color='#10b981'),
            fillcolor='rgba(16, 185, 129, 0.2)'
        ))

        # Línea Amarilla (Frecuencia)
        if "FRECUENCIA (DIAS)" in df.columns:
            fig_combo.add_trace(go.Scatter(
                x=df_sorted['FECHA'], y=df_sorted['FRECUENCIA (DIAS)'], name='Frecuencia',
                mode='lines+markers',
                line=dict(color='#f59e0b', width=3),
                marker=dict(size=6, color='white', line=dict(width=2, color='#f59e0b'))
            ))

        fig_combo.update_layout(
            plot_bgcolor="white", height=350, hovermode="x unified",
            yaxis=dict(showgrid=True, gridcolor="#f3f4f6"), xaxis=dict(showgrid=False),
            margin=dict(t=20, l=10, r=10, b=10), legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig_combo, use_container_width=True)


    # --- PESTAÑA 2: INSUMOS ---
    with tab2:
        st.markdown("### 🧪 Uso de Productos Químicos")
        col_prod1 = next((c for c in df.columns if "PRODUCTO 1" in c), None)
        col_prod2 = next((c for c in df.columns if "PRODUCTO 2" in c), None)
        
        if col_prod1:
            prods = pd.concat([df[col_prod1], df.get(col_prod2, pd.Series())]).dropna()
            if not prods.empty:
                top_prods = prods.value_counts().reset_index()
                top_prods.columns = ['Producto', 'Aplicaciones']
                fig_prod = px.bar(
                    top_prods.head(12), x='Aplicaciones', y='Producto', orientation='h',
                    color='Aplicaciones', color_continuous_scale='Teal'
                )
                fig_prod.update_layout(plot_bgcolor="white", yaxis=dict(autorange="reversed"), height=600)
                st.plotly_chart(fig_prod, use_container_width=True)

    # --- PESTAÑA 3: GESTIÓN DE DATOS ---
    with tab3:
        col_view, col_add = st.columns([2, 1])
        with col_view:
            st.markdown("### 📋 Base de Datos Actual")
            st.dataframe(df.style.format({"HAS": "{:.2f}"}), use_container_width=True, height=500)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Descargar CSV", csv, "Reporte_Completo.csv", "text/csv")

        with col_add:
            st.markdown("### ➕ Agregar Registro Manual")
            with st.container(border=True):
                with st.form("add_form", clear_on_submit=True):
                    st.info("Estos datos se sumarán a los gráficos al instante.")
                    new_date = st.date_input("Fecha", datetime.today())
                    new_cat = st.selectbox("Categoría", ["CICLO", "FOLIAR", "INTERCICLO", "CONTROL"])
                    new_app = st.number_input("Num. Aplicación", min_value=1, step=1)
                    new_frec = st.number_input("Frecuencia (Días)", min_value=0, step=1)
                    new_has = st.number_input("Hectáreas (Has)", min_value=0.0, step=0.1)
                    new_prod1 = st.text_input("Producto 1")
                    new_prod2 = st.text_input("Producto 2")
                    submitted = st.form_submit_button("✅ Guardar y Actualizar")
                    if submitted:
                        new_row = {
                            'FECHA': pd.Timestamp(new_date),
                            'CATEGORIA': new_cat,
                            'NUM. APLICACION': new_app,
                            'FRECUENCIA (DIAS)': new_frec,
                            'HAS': new_has,
                            'PRODUCTO 1': new_prod1,
                            'PRODUCTO 2': new_prod2
                        }
                        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
                        st.success("¡Registro agregado!")
                        st.rerun()

else:
    st.info("👈 **¡MIRA A LA IZQUIERDA!** El menú de carga ya está abierto.")
    st.markdown("---")
    st.markdown("### 📂 ¿No ves el menú? Carga tu archivo aquí:")
    uploaded_center = st.file_uploader("Cargar Excel (Respaldo)", type=["xlsx", "xls"], key="center_uploader")
    if uploaded_center:
        df_loaded = load_data_from_file(uploaded_center)
        if df_loaded is not None:
             st.session_state.data = df_loaded
             st.rerun()