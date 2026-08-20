import datetime
import os
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Controlo de Stock e Vendas", page_icon="📊", layout="wide"
)

# Caminhos dos arquivos de dados locais (simulando a nuvem no GitHub/Streamlit Community Cloud)
STOCK_FILE = "stock_produtos.csv"
VENDAS_FILE = "historico_vendas.csv"


# Inicializar dados padrão se os arquivos não existirem
def carregar_dados():
  if not os.path.exists(STOCK_FILE):
    df_stock = pd.DataFrame(
        columns=["Produto", "Stock Inicial", "Preço de Compra", "Preço de Venda"]
    )
    df_stock.to_csv(STOCK_FILE, index=False)
  else:
    df_stock = pd.read_csv(STOCK_FILE)

  if not os.path.exists(VENDAS_FILE):
    df_vendas = pd.DataFrame(columns=[
        "Quantidade",
        "Data da Venda",
        "Produto",
        "Preço de Compra",
        "Custo de Embalagem",
        "Preço de Venda",
        "Facturação",
        "Lucro",
        "Margem de Lucro (%)",
    ])
    df_vendas.to_csv(VENDAS_FILE, index=False)
  else:
    df_vendas = pd.read_csv(VENDAS_FILE)

  return df_stock, df_vendas


df_stock, df_vendas = carregar_dados()

# Menu lateral para navegação
menu = st.sidebar.selectbox(
    "Navegação", ["Registar Venda", "Gerir Stock / Produtos", "Histórico de Vendas"]
)

# ---------------------------------------------------------
# 1. REGISTAR VENDA
# ---------------------------------------------------------
if menu == "Registar Venda":
  st.subheader("🛒 Registar Nova Venda")

  if df_stock.empty:
    st.warning(
        "Cadastre produtos primeiro na aba 'Gerir Stock / Produtos' antes de"
        " fazer vendas."
    )
  else:
    with st.form("form_venda"):
      col1, col2 = st.columns(2)

      with col1:
        produto_selecionado = st.selectbox(
            "Produto", df_stock["Produto"].unique()
        )
        quantidade = st.number_input(
            "Quantidade Vendida", min_value=1, step=1, value=1
        )
        data_venda = st.date_input(
            "Data da Venda", value=datetime.date.today()
        )

      # Obter preços padrão do produto selecionado
      dados_prod = df_stock[df_stock["Produto"] == produto_selecionado].iloc[0]
      preco_compra_padrao = float(dados_prod["Preço de Compra"])
      preco_venda_padrao = float(dados_prod["Preço de Venda"])

      with col2:
        preco_compra = st.number_input(
            "Preço de Compra (Unitário)",
            value=preco_compra_padrao,
            format="%.2f",
        )
        custo_embalagem = st.number_input(
            "Custo de Embalagem (Total)", value=0.0, format="%.2f"
        )
        preco_venda = st.number_input(
            "Preço de Venda (Unitário)",
            value=preco_venda_padrao,
            format="%.2f",
        )

      submit_venda = st.form_submit_button("Concluir e Registar Venda")

      if submit_venda:
        # Cálculos automáticos baseados na sua tabela
        facturacao = quantidade * preco_venda
        custo_total = (quantidade * preco_compra) + custo_embalagem
        lucro = facturacao - custo_total
        margem_lucro = (
            (lucro / facturacao) * 100 if facturacao > 0 else 0
        )  # Margem em %

        nova_venda = pd.DataFrame([{
            "Quantidade": quantidade,
            "Data da Venda": str(data_venda),
            "Produto": produto_selecionado,
            "Preço de Compra": preco_compra,
            "Custo de Embalagem": custo_embalagem,
            "Preço de Venda": preco_venda,
            "Facturação": facturacao,
            "Lucro": lucro,
            "Margem de Lucro (%)": round(margem_lucro, 2),
        }])

        df_vendas = pd.concat([df_vendas, nova_venda], ignore_index=True)
        df_vendas.to_csv(VENDAS_FILE, index=False)

        st.success(
            f"Venda de '{produto_selecionado}' registada com sucesso! Lucro"
            f" obtido: {lucro:,.2f}"
        )

# ---------------------------------------------------------
# 2. GERIR STOCK / PRODUTOS
# ---------------------------------------------------------
elif menu == "Gerir Stock / Produtos":
  st.subheader("📦 Gestão de Stock e Produtos")

  with st.form("form_produto"):
    st.write("Adicionar Novo Produto ao Stock")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
      novo_produto = st.text_input("Nome do Produto")
    with col2:
      stock_inicial = st.number_input(
          "Quantidade em Stock", min_value=0, step=1
      )
    with col3:
      p_compra = st.number_input(
          "Preço de Compra Padrão", min_value=0.0, format="%.2f"
      )
    with col4:
      p_venda = st.number_input(
          "Preço de Venda Padrão", min_value=0.0, format="%.2f"
      )

    salvar_prod = st.form_submit_button("Salvar Produto")
    if salvar_prod and novo_produto:
      novo_df = pd.DataFrame([{
          "Produto": novo_produto,
          "Stock Inicial": stock_inicial,
          "Preço de Compra": p_compra,
          "Preço de Venda": p_venda,
      }])
      df_stock = pd.concat([df_stock, novo_df], ignore_index=True)
      df_stock.to_csv(STOCK_FILE, index=False)
      st.success(f"Produto '{novo_produto}' adicionado com sucesso!")

  st.markdown("---")
  st.subheader("Tabela de Stock Atual")
  st.dataframe(df_stock, use_container_width=True)

# ---------------------------------------------------------
# 3. HISTÓRICO DE VENDAS (A Tabela da sua 1ª imagem)
# ---------------------------------------------------------
elif menu == "Histórico de Vendas":
  st.subheader("📋 Histórico de Vendas e Lucros")

  if df_vendas.empty:
    st.info("Ainda não existem vendas registadas.")
  else:
    st.dataframe(df_vendas, use_container_width=True)

    # Métricas gerais de resumo
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Facturação Total", f"{df_vendas['Facturação'].sum():,.2f}")
    col2.metric("Lucro Total", f"{df_vendas['Lucro'].sum():,.2f}")
    col3.metric("Total de Vendas", len(df_vendas))
