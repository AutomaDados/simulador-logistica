import streamlit as st
import plotly.express as px
import logica
import numpy as np

st.set_page_config(
    page_title="Simulador de Slotting | Automadados",
    page_icon="🏭",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        margin-top: -1rem;
    }
    [data-testid="stHeader"] {
        background-color: rgba(0,0,0,0);
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.image("assets/banner_topo.png", use_container_width=True)

# Sidebar
st.sidebar.header("⚙️ 1. Configure sua Operação")
st.sidebar.info("Defina o tamanho do armazém abaixo e clique no botão para rodar a IA.")

n_pedidos = st.sidebar.slider("📦 Volume de Pedidos (Mês)", 10000, 500000, 100000, step=10000)
n_skus = st.sidebar.slider("🏷️ Quantidade de SKUs", 100, 2000, 500, step=50)

st.sidebar.markdown("---")
botao_calcular = st.sidebar.button("🚀 2. RODAR SIMULAÇÃO", type="primary")

# Área Principal
if botao_calcular:
    with st.spinner("A IA está reorganizando seu estoque..."):
        custo_atual, custo_novo, df_antes, df_depois = logica.gerar_cenario_completo(n_skus, n_pedidos)
        
        economia = custo_atual - custo_novo
        pct_economia = (economia / custo_atual) * 100
        
        st.success("✅ Otimização Concluída!")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Movimentação Atual", f"{custo_atual:,.0f} km")
        col2.metric("Movimentação Otimizada", f"{custo_novo:,.0f} km")
        col3.metric("Economia Real", f"{economia:,.0f} km", f"▼ {pct_economia:.1f}%")
            
        st.divider()
        
        st.subheader("🗺️ Visualização do Armazém")
        g_col1, g_col2 = st.columns(2)
        color_map = {'A': '#ff4b4b', 'B': '#ffa421', 'C': '#1c83e1'}
        
        with g_col1:
            st.markdown("**❌ ANTES: Caos Operacional**")
            df_antes['Corredor'] = np.random.randint(1, 20, size=len(df_antes))
            fig1 = px.scatter(df_antes, x='Distancia_Atual', y='Corredor', color='ABC',
                             color_discrete_map=color_map, height=350)
            fig1.add_vline(x=0, annotation_text="Saída")
            fig1.update_layout(margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Distância (m)", yaxis_visible=False)
            st.plotly_chart(fig1, use_container_width=True)
            
        with g_col2:
            st.markdown("**✅ DEPOIS: Slotting Inteligente**")
            df_depois['Corredor'] = np.random.randint(1, 20, size=len(df_depois))
            fig2 = px.scatter(df_depois, x='Distancia_Nova', y='Corredor', color='ABC',
                             color_discrete_map=color_map, height=350)
            fig2.add_vline(x=0, annotation_text="Saída")
            fig2.update_layout(margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Distância (m)", yaxis_visible=False)
            st.plotly_chart(fig2, use_container_width=True)

else:

    st.info("👈 Siga a seta na imagem: configure os parâmetros na barra lateral para iniciar.")
