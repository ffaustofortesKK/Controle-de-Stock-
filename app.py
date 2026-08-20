import datetime
import os
import pandas as pd
import streamlit as st

# Configuração da página (otimizada para telemóveis e computadores)
st.set_page_config(
    page_title="Controlo de Stock e Vendas", page_icon="📊", layout="centered"
)

# Estilo CSS personalizado: Fundo rosa, abas pretas, texto em negrito e design responsivo para telemóvel
st.markdown(
    """
    <style>
    /* Fundo geral da página cor-de-rosa liso */
    .stApp {
        background-color: #ffb6c1 !important;
    }
    
    /* Forçar todo o texto em negrito */
    html, body, [class*="css"], label, p, span, div, h1, h2, h3, h4, h5, h6 {
        font-weight: bold !important;
    }

    /* Estilo das abas (Tabs) com fundo preto e texto destacado */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #000000;
        padding: 8px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e1e !important;
        border-radius: 5px;
        color: #ffffff !important;
        padding: 8px 12px;
        font-size: 13px !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #ff1493 !important;
        color: #ffffff !important;
    }

    /* Otimização para telemóveis (botões e campos adaptados) */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold !important;
    }
    
    h1, h2, h3 {
        color: #000000 !important;
        font-size: 1.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Caminhos dos arquivos de dados
STOCK_FILE = "stock_produtos.csv"
VENDAS_FILE = "historico_vendas.csv"

# Senha de acesso ao sistema
SENHA_SISTEMA = "1234"


# Função de Autenticação
def verificar_autenticacao():
  if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

  if not st.session_state["autenticado"]:
    st.subheader("🔐 Acesso Restrito - Faça Login")
    senha_digitada = st.text_input(
        "Digite a palavra-passe (password):", type="password"
    )
    if st.button("Entrar"):
      if senha_digitada == SENHA_SISTEMA:
        st.session_state["autenticado"] = True
        st.rerun()
      else:
        st.error("Palavra-passe incorreta!")
    return False
  return True


if not verificar_autenticacao():
  st.stop()


# Carregar dados com segurança para colunas em falta
@st.cache_data(ttl=1)
def carregar_dados():
  if not os.path.exists(STOCK_FILE):
    df_stock = pd.DataFrame(columns=[
        "Código",
        "Produto",
        "Stock Inicial",
        "Preço de Compra",
        "Preço de Venda",
    ])
    df_stock.to_csv(STOCK_FILE, index=False)
  else:
    df_stock = pd.read_csv(STOCK_FILE)
    if "Código" not in df_stock.columns:
      df_stock.insert(
          0,
          "Código",
          [f"{i+1:03d}" for i in range(len(df_stock))],
      )
      df_stock.to_csv(STOCK_FILE, index=False)

  if not os.path.exists(VENDAS_FILE):
    df_vendas = pd.DataFrame(columns=[
        "ID_Venda",
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

# Botão de Terminar Sessão na barra lateral
with st.sidebar:
  st.write("Sessão Ativa")
  if st.button("Sair (Logout)"):
    st.session_state["autenticado"] = False
    st.rerun()
  st.markdown("---")

# Título Principal do App
st.title("📊 Controlo de Stock e Vendas")

# Criação das Abas Principais (Tabs)
aba_venda, aba_stock, aba_historico = st.tabs(
    ["🛒 Vendas", "📦 Stock", "📋 Histórico"]
)

# ---------------------------------------------------------
# 1. ABA: REGISTAR / REFAZER VENDA
# ---------------------------------------------------------
with aba_venda:
  st.subheader("Registo e Edição de Vendas")

  modo = st.radio(
      "Ação:", ["Nova Venda", "Refazer / Editar Registo Anterior"],
      horizontal=True,
  )

  if df_stock.empty:
    st.warning("Cadastre primeiro os produtos na aba 'Stock'.")
  else:
    if modo == "Nova Venda":
      with st.form("form_venda_novo"):
        produto_selecionado = st.selectbox(
            "Produto", df_stock["Produto"].unique()
        )
        quantidade = st.number_input(
            "Quantidade Vendida", min_value=1, step=1, value=1
        )
        data_venda = st.date_input("Data da Venda", value=datetime.date.today())

        submit = st.form_submit_button("Salvar Nova Venda")

        if submit:
          # Puxa automaticamente os preços cadastrados no stock
          dados_prod = df_stock[df_stock["Produto"] == produto_selecionado].iloc[
              0
          ]
          preco_compra = float(dados_prod["Preço de Compra"])
          preco_venda = float(dados_prod["Preço de Venda"])
          custo_embalagem = 0.0

          facturacao = quantidade * preco_venda
          custo_total = (quantidade * preco_compra) + custo_embalagem
          lucro = facturacao - custo_total
          margem = (lucro / facturacao) * 100 if facturacao > 0 else 0
          id_unico = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

          nova_linha = pd.DataFrame([{
              "ID_Venda": id_unico,
              "Quantidade": quantidade,
              "Data da Venda": str(data_venda),
              "Produto": produto_selecionado,
              "Preço de Compra": preco_compra,
              "Custo de Embalagem": custo_embalagem,
              "Preço de Venda": preco_venda,
              "Facturação": facturacao,
              "Lucro": lucro,
              "Margem de Lucro (%)": round(margem, 2),
          }])

          df_vendas = pd.concat([df_vendas, nova_linha], ignore_index=True)
          df_vendas.to_csv(VENDAS_FILE, index=False)
          st.success("Venda registada com sucesso!")
          st.rerun()

    else:
      if df_vendas.empty:
        st.info("Nenhuma venda registada para editar.")
      else:
        df_vendas["Descricao_Edit"] = (
            df_vendas.index.astype(str)
            + " - "
            + df_vendas["Data da Venda"]
            + " | "
            + df_vendas["Produto"]
            + " (Qtd: "
            + df_vendas["Quantidade"].astype(str)
            + ")"
        )
        venda_escolhida = st.selectbox(
            "Escolha o registo:", df_vendas["Descricao_Edit"]
        )
        idx_selecionado = int(venda_escolhida.split(" - ")[0])
        row_atual = df_vendas.loc[idx_selecionado]

        with st.form("form_editar_venda"):
          q_edit = st.number_input(
              "Quantidade Vendida",
              min_value=1,
              value=int(row_atual["Quantidade"]),
          )
          prod_edit = st.selectbox(
              "Produto",
              df_stock["Produto"].unique(),
              index=list(df_stock["Produto"].unique()).index(
                  row_atual["Produto"]
              )
              if row_atual["Produto"] in df_stock["Produto"].values
              else 0,
          )
          data_edit = st.date_input(
              "Data da Venda",
              value=datetime.datetime.strptime(
                  str(row_atual["Data da Venda"]), "%Y-%m-%d"
              ).date(),
          )

          btn_atualizar = st.form_submit_button("Atualizar Registo")

          if btn_atualizar:
            # Puxa os preços atuais atualizados do produto selecionado
            dados_prod_edit = df_stock[df_stock["Produto"] == prod_edit].iloc[0]
            pc_edit = float(dados_prod_edit["Preço de Compra"])
            pv_edit = float(dados_prod_edit["Preço de Venda"])
            ce_edit = 0.0

            fact_new = q_edit * pv_edit
            custo_new = (q_edit * pc_edit) + ce_edit
            lucro_new = fact_new - custo_new
            margem_new = (lucro_new / fact_new) * 100 if fact_new > 0 else 0

            df_vendas.at[idx_selecionado, "Quantidade"] = q_edit
            df_vendas.at[idx_selecionado, "Data da Venda"] = str(data_edit)
            df_vendas.at[idx_selecionado, "Produto"] = prod_edit
            df_vendas.at[idx_selecionado, "Preço de Compra"] = pc_edit
            df_vendas.at[idx_selecionado, "Custo de Embalagem"] = ce_edit
            df_vendas.at[idx_selecionado, "Preço de Venda"] = pv_edit
            df_vendas.at[idx_selecionado, "Facturação"] = fact_new
            df_vendas.at[idx_selecionado, "Lucro"] = lucro_new
            df_vendas.at[idx_selecionado, "Margem de Lucro (%)"] = round(
                margem_new, 2
            )

            if "Descricao_Edit" in df_vendas.columns:
              df_vendas = df_vendas.drop(columns=["Descricao_Edit"])

            df_vendas.to_csv(VENDAS_FILE, index=False)
            st.success("Registo atualizado com sucesso!")
            st.rerun()

# ---------------------------------------------------------
# 2. ABA: GERIR STOCK (Adicionar, Editar e Eliminar)
# ---------------------------------------------------------
with aba_stock:
  st.subheader("📦 Gestão de Produtos")

  acao_produto = st.radio(
      "Operação:", ["Novo", "Editar", "Eliminar"], horizontal=True
  )

  if acao_produto == "Novo":
    with st.form("form_novo_produto"):
      n_prod = st.text_input("Nome do Produto")
      s_inic = st.number_input("Stock Inicial", min_value=0, step=1)
      p_comp = st.number_input(
          "Preço Compra Padrão", min_value=0.0, format="%.2f"
      )
      p_vend = st.number_input(
          "Preço Venda Padrão", min_value=0.0, format="%.2f"
      )

      if st.form_submit_button("Guardar Produto") and n_prod:
        proximo_id = len(df_stock) + 1
        codigo_formatado = f"{proximo_id:03d}"

        novo_p = pd.DataFrame([{
            "Código": codigo_formatado,
            "Produto": n_prod,
            "Stock Inicial": s_inic,
            "Preço de Compra": p_comp,
            "Preço de Venda": p_vend,
        }])
        df_stock = pd.concat([df_stock, novo_p], ignore_index=True)
        df_stock.to_csv(STOCK_FILE, index=False)
        st.success(f"Produto '{n_prod}' criado com sucesso!")
        st.rerun()

  elif acao_produto == "Editar":
    if df_stock.empty:
      st.info("Nenhum produto cadastrado.")
    else:
      produto_a_editar = st.selectbox(
          "Selecione o produto:", df_stock["Produto"]
      )
      idx_prod = df_stock[df_stock["Produto"] == produto_a_editar].index[0]
      row_prod_atual = df_stock.loc[idx_prod]

      with st.form("form_editar_produto"):
        st.write(f"Código: {row_prod_atual['Código']}")
        novo_nome_prod = st.text_input(
            "Nome do Produto", value=str(row_prod_atual["Produto"])
        )
        novo_stock = st.number_input(
            "Stock Inicial",
            min_value=0,
            step=1,
            value=int(row_prod_atual["Stock Inicial"]),
        )
        novo_pc_padrao = st.number_input(
            "Preço de Compra",
            min_value=0.0,
            format="%.2f",
            value=float(row_prod_atual["Preço de Compra"]),
        )
        novo_pv_padrao = st.number_input(
            "Preço de Venda",
            min_value=0.0,
            format="%.2f",
            value=float(row_prod_atual["Preço de Venda"]),
        )

        if st.form_submit_button("Atualizar Produto"):
          df_stock.at[idx_prod, "Produto"] = novo_nome_prod
          df_stock.at[idx_prod, "Stock Inicial"] = novo_stock
          df_stock.at[idx_prod, "Preço de Compra"] = novo_pc_padrao
          df_stock.at[idx_prod, "Preço de Venda"] = novo_pv_padrao

          df_stock.to_csv(STOCK_FILE, index=False)
          st.success("Produto atualizado com sucesso!")
          st.rerun()

  else:  # Eliminar Produto
    if df_stock.empty:
      st.info("Nenhum produto cadastrado.")
    else:
      produto_a_apagar = st.selectbox(
          "Selecione o produto para eliminar:", df_stock["Produto"]
      )
      if st.button("Eliminar Produto Definitivamente"):
        idx_apagar = df_stock[df_stock["Produto"] == produto_a_apagar].index[0]
        df_stock = df_stock.drop(idx_apagar).reset_index(drop=True)
        df_stock.to_csv(STOCK_FILE, index=False)
        st.success("Produto eliminado com sucesso!")
        st.rerun()

  st.markdown("---")
  st.write("### Lista de Stock")
  if not df_stock.empty:
    st.dataframe(df_stock, use_container_width=True)

# ---------------------------------------------------------
# 3. ABA: HISTÓRICO DE VENDAS
# ---------------------------------------------------------
with aba_historico:
  st.subheader("📋 Histórico")

  if df_vendas.empty:
    st.info("Sem vendas registadas.")
  else:
    if "Descricao_Edit" in df_vendas.columns:
      df_vendas = df_vendas.drop(columns=["Descricao_Edit"])

    st.dataframe(df_vendas, use_container_width=True)

    st.markdown("---")
    st.metric("Facturação Total", f"{df_vendas['Facturação'].sum():,.2f}")
    st.metric("Lucro Total", f"{df_vendas['Lucro'].sum():,.2f}")

    with st.expander("Apagar registo de venda"):
      venda_apagar = st.selectbox(
          "Selecione a venda a excluir:", df_vendas.index
      )
      if st.button("Eliminar Venda"):
        df_vendas = df_vendas.drop(venda_apagar).reset_index(drop=True)
        df_vendas.to_csv(VENDAS_FILE, index=False)
        st.success("Venda eliminada!")
        st.rerun()
