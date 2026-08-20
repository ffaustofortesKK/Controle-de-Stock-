import datetime
import os
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(page_title="Gestão FF", page_icon="📊", layout="wide")

# Estilo para fundo escuro
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    </style>
    """, unsafe_allow_html=True)

STOCK_FILE = "stock_produtos.csv"
VENDAS_FILE = "historico_vendas.csv"
SENHA_SISTEMA = "1234"

# --- [Funções auxiliares omitidas para brevidade, mantenha as anteriores] ---
# (Autenticação, carregamento, etc. permanecem iguais)

if "autenticado" not in st.session_state: st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("🔐 Acesso Restrito")
    senha = st.text_input("Password:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_SISTEMA: st.session_state["autenticado"] = True; st.rerun()
    st.stop()

def carregar_dados():
    if not os.path.exists(STOCK_FILE):
        df_stock = pd.DataFrame(columns=["Código", "Produto", "Stock", "P. Compra", "P. Venda"])
        df_stock.to_csv(STOCK_FILE, index=False)
    else: df_stock = pd.read_csv(STOCK_FILE)
    # ... (carregar vendas igual ao anterior)
    return df_stock

df_stock = carregar_dados()

# --- ABAS ---
aba_venda, aba_stock, aba_historico = st.tabs(["🛒 Vendas", "📦 Gestão de Produtos", "📋 Histórico"])

with aba_stock:
    st.subheader("📦 Gestão e Edição de Produtos")
    
    # OPÇÃO: Novo Produto ou Editar Produto
    acao_prod = st.radio("Ação:", ["Novo Produto", "Editar Produto Existente"], horizontal=True)
    
    if acao_prod == "Novo Produto":
        with st.form("form_novo"):
            nome = st.text_input("Nome do Produto")
            qnt = st.number_input("Stock", min_value=0)
            pc = st.number_input("Preço Compra", format="%.2f")
            pv = st.number_input("Preço Venda", format="%.2f")
            if st.form_submit_button("Guardar"):
                novo_cod = f"{len(df_stock)+1:03}"
                novo = pd.DataFrame([{"Código": novo_cod, "Produto": nome, "Stock": qnt, "P. Compra": pc, "P. Venda": pv}])
                df_stock = pd.concat([df_stock, novo], ignore_index=True)
                df_stock.to_csv(STOCK_FILE, index=False)
                st.success("Produto criado!")
                st.rerun()
    
    else: # EDITAR PRODUTO
        if not df_stock.empty:
            sel_prod = st.selectbox("Selecione o produto para editar:", df_stock["Produto"].tolist())
            idx = df_stock[df_stock["Produto"] == sel_prod].index[0]
            
            with st.form("form_edit"):
                novo_nome = st.text_input("Novo Nome", value=df_stock.at[idx, "Produto"])
                novo_stk = st.number_input("Stock", value=int(df_stock.at[idx, "Stock"]))
                novo_pc = st.number_input("P. Compra", value=float(df_stock.at[idx, "P. Compra"]))
                novo_pv = st.number_input("P. Venda", value=float(df_stock.at[idx, "P. Venda"]))
                
                if st.form_submit_button("Atualizar Dados"):
                    df_stock.at[idx, ["Produto", "Stock", "P. Compra", "P. Venda"]] = [novo_nome, novo_stk, novo_pc, novo_pv]
                    df_stock.to_csv(STOCK_FILE, index=False)
                    st.success("Dados atualizados!")
                    st.rerun()

    st.write("---")
    st.dataframe(df_stock, use_container_width=True)

# ... (restante do código das outras abas segue a mesma lógica)
