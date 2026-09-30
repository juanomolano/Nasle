import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA (UI/UX)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Encuesta Muñecos de Navidad",
    page_icon="🎄",
    layout="wide"
)

st.title("🎄 Control de Pedidos: Muñecos de Navidad")

# ---------------------------------------------------------
# GESTIÓN DE DATOS EN MEMORIA / CACHÉ
# ---------------------------------------------------------
if "modelos_munecos" not in st.session_state:
    st.session_state["modelos_munecos"] = [
        "Papá Noel patas largas",
        "Mamá Noel",
        "Muñeco de Nieve",
        "Reno Navideño",
        "Duende Navideño"
    ]

if "df_pedidos" not in st.session_state:
    st.session_state["df_pedidos"] = pd.DataFrame(columns=[
        "Fecha", "Familiar", "Muñeco", "Cantidad", "Observaciones"
    ])

# ---------------------------------------------------------
# PESTAÑAS PRINCIPALES DEL DASHBOARD
# ---------------------------------------------------------
tab_registro, tab_dashboard, tab_datos = st.tabs([
    "📝 Registrar Pedido", 
    "📊 Gráficos y Análisis", 
    "📁 Tabla y Exportación Excel"
])

# =========================================================
# PESTAÑA 1: REGISTRO DE ENCUESTA
# =========================================================
with tab_registro:
    st.subheader("Registrar nuevo pedido")
    
    col_form, col_nuevo_modelo = st.columns([2, 1], gap="large")
    
    with col_form:
        with st.form("form_pedido", clear_on_submit=True):
            familiar = st.radio(
                "¿Quién realiza el registro?",
                ["Nasle", "Adriana", "Marina"]
            )
            
            st.divider()
            
            # Opción cambiada a st.radio para ver todos los muñecos de una vez
            muneco_seleccionado = st.radio(
                "Selecciona el muñeco de Navidad:",
                st.session_state["modelos_munecos"]
            )
            
            st.divider()
            
            cantidad = st.number_input("Cantidad solicitada:", min_value=1, value=1, step=1)
            
            observaciones = st.text_area(
                "Observaciones o detalles del pedido:",
                placeholder="Ejemplo: Cliente pide sombrero rojo brillante y entrega el 15 de dic."
            )
            
            btn_guardar = st.form_submit_button("💾 Guardar Pedido", use_container_width=True)
            
            if btn_guardar:
                nuevo_registro = {
                    "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Familiar": familiar,
                    "Muñeco": muneco_seleccionado,
                    "Cantidad": int(cantidad),
                    "Observaciones": observaciones
                }
                
                st.session_state["df_pedidos"] = pd.concat([
                    st.session_state["df_pedidos"],
                    pd.DataFrame([nuevo_registro])
                ], ignore_index=True)
                
                st.success(f"¡Pedido guardado exitosamente por {familiar}!")

    with col_nuevo_modelo:
        st.subheader("➕ Agregar nuevo modelo")
        st.info("Si tu familia elabora un diseño nuevo, agrégalo aquí para que aparezca en la lista automáticamente.")
        
        nuevo_modelo = st.text_input("Nombre del nuevo muñeco:")
        if st.button("Agregar a las opciones", use_container_width=True):
            if nuevo_modelo and nuevo_modelo not in st.session_state["modelos_munecos"]:
                st.session_state["modelos_munecos"].append(nuevo_modelo)
                st.success(f"'{nuevo_modelo}' se agregó a la lista.")
                st.rerun()
            elif nuevo_modelo in st.session_state["modelos_munecos"]:
                st.warning("Ese modelo ya existe en la lista.")

# =========================================================
# PESTAÑA 2: GRÁFICOS Y ANÁLISIS
# =========================================================
with tab_dashboard:
    st.subheader("Resumen General de Pedidos")
    df = st.session_state["df_pedidos"]
    
    if df.empty:
        st.info("Aún no hay pedidos registrados. Ve a la pestaña 'Registrar Pedido' para ingresar el primero.")
    else:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Registro Pedidos", len(df))
        col_m2.metric("Total Muñecos Solicitados", df["Cantidad"].sum())
        col_m3.metric("Modelo Más Pedido", df.groupby("Muñeco")["Cantidad"].sum().idxmax())
        
        st.divider()
        
        df_agrupado = df.groupby("Muñeco")["Cantidad"].sum().reset_index()
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("### 🥧 Distribución de Pedidos (Gráfica de Torta)")
            fig_pie = px.pie(
                df_agrupado,
                names="Muñeco",
                values="Cantidad",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_chart2:
            st.markdown("### 📊 Pedidos por Familiar")
            df_fam = df.groupby(["Familiar", "Muñeco"])["Cantidad"].sum().reset_index()
            fig_bar = px.bar(
                df_fam,
                x="Familiar",
                y="Cantidad",
                color="Muñeco",
                barmode="stack",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_bar, use_container_width=True)

# =========================================================
# PESTAÑA 3: TABLA DE DATOS Y DESCARGA DE EXCEL FILTRADO
# =========================================================
with tab_datos:
    st.subheader("Listado Detallado y Exportación")
    df = st.session_state["df_pedidos"]
    
    if df.empty:
        st.info("No hay datos cargados.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_familiar = st.multiselect(
                "Filtrar por Familiar:",
                options=df["Familiar"].unique(),
                default=df["Familiar"].unique()
            )
        with col_f2:
            filtro_muneco = st.multiselect(
                "Filtrar por Muñeco:",
                options=df["Muñeco"].unique(),
                default=df["Muñeco"].unique()
            )
            
        df_filtrado = df[
            (df["Familiar"].isin(filtro_familiar)) &
            (df["Muñeco"].isin(filtro_muneco))
        ]
        
        st.dataframe(df_filtrado, use_container_width=True)
        
        import io
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Pedidos_Navidad')
            
        st.download_button(
            label="📥 Descargar Excel Filtrado (.xlsx)",
            data=buffer.getvalue(),
            file_name=f"pedidos_navidad_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )