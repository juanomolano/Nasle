import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA (UI/UX)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pedidos Muñecos Navidad",
    page_icon="🎄",
    layout="centered"
)

# Estilo CSS personalizado para botones grandes en móvil
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3em;
        font-size: 18px !important;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎄 Pedidos de Navidad")

# -----------------------------------------------------------------------------
# GESTIÓN DE DATOS EN MEMORIA (SESSION STATE)
# -----------------------------------------------------------------------------
if "modelos_munecos" not in st.session_state:
    st.session_state["modelos_munecos"] = [
        "Papá Noel patas largas",
        "Mamá Noel",
        "Muñeco de Nieve",
        "Reno Navideño",
        "Elfo de la Navidad"
    ]

if "pedidos" not in st.session_state:
    st.session_state["pedidos"] = []

# -----------------------------------------------------------------------------
# NAVEGACIÓN POR PESTAÑAS (MÓVIL FRIENDLY)
# -----------------------------------------------------------------------------
tab_registro, tab_resumen, tab_exportar = st.tabs(["📝 Registrar", "📊 Ver Totales", "📥 Exportar"])

# --- PESTAÑA 1: REGISTRAR PEDIDO ---
with tab_registro:
    st.subheader("Ingresar nuevo pedido")
    
    with st.form("form_pedido", clear_on_submit=True):
        persona = st.selectbox(
            "👤 ¿Quién realiza el pedido?",
            ["Nasle", "Adriana", "Marina"]
        )
        
        modelo = st.radio(
            "🧸 Selecciona el modelo de muñeco:",
            st.session_state["modelos_munecos"]
        )
        
        cantidad = st.number_input(
            "🔢 Cantidad:",
            min_value=1,
            max_value=20,
            value=1,
            step=1
        )
        
        # Campo de Observaciones
        observaciones = st.text_area(
            "📝 Observaciones / Notas adicionales:",
            placeholder="Ej: Color del sombrero, empaque de regalo, fecha especial..."
        )
        
        submit = st.form_submit_button("✅ Guardar Pedido", use_container_width=True)
        
        if submit:
            st.session_state["pedidos"].append({
                "Persona": persona,
                "Modelo": modelo,
                "Cantidad": cantidad,
                "Observaciones": observaciones if observaciones else "Sin observaciones"
            })
            st.success(f"¡Guardado! {cantidad}x {modelo} para {persona}.")

# --- PESTAÑA 2: GRÁFICOS Y MÉTRICAS ---
with tab_resumen:
    st.subheader("Resumen de pedidos")
    
    if st.session_state["pedidos"]:
        df = pd.DataFrame(st.session_state["pedidos"])
        
        total_muñecos = df["Cantidad"].sum()
        total_pedidos = len(df)
        
        col1, col2 = st.columns(2)
        col1.metric("Total Muñecos", total_muñecos)
        col2.metric("Nº Registros", total_pedidos)
        
        st.divider()
        
        df_grouped = df.groupby("Modelo")["Cantidad"].sum().reset_index()
        fig = px.pie(
            df_grouped,
            values="Cantidad",
            names="Modelo",
            hole=0.4,
            title="Distribución por Modelo"
        )
        
        fig.update_layout(
            margin=dict(t=30, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.subheader("Detalle del registro")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no hay pedidos registrados. Usa la pestaña 'Registrar'.")

# --- PESTAÑA 3: EXPORTAR ---
with tab_exportar:
    st.subheader("Descargar reporte")
    
    if st.session_state["pedidos"]:
        df = pd.DataFrame(st.session_state["pedidos"])
        
        csv = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📄 Descargar en Excel / CSV",
            data=csv,
            file_name="pedidos_navidad.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.warning("No hay datos para exportar todavía.")