import datetime
import os
import pandas as pd
import streamlit as st

# Configuração da página (otimizada para telemóveis e computadores)
st.set_page_config(
    page_title="Controlo de Stock e Vendas", page_icon="📊", layout="centered"
)

# Estilo CSS personalizado: Esconde o cabeçalho/menu do Streamlit e aplica o design rosa
st.markdown(
    """
    <style>
    /* Ocultar o cabeçalho padrão do Streamlit */
    header {visibility: hidden !important;}
    
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

# Dicionário de Utilizadores e Perfis
UTILIZADORES = {
    "admin": {"senha": "123123", "perfil": "Admin", "nome": "Administrador"},
    "Sandra Francisco": {
        "senha": "2404",
        "perfil": "Utilizador",
        "nome": "Sandra Francisco",
    },
}


# Função de Autenticação com verificação de utilizadores
def verificar_autenticacao():
  if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["utilizador_atual"] = None
    st.session_state["perfil_atual"] = None

  if not st.session_state["autenticado"]:
    st.subheader("🔐 Acesso Restrito - Faça Login")

    nome_utilizador = st.selectbox(
        "Selecione o Utilizador:", list(UTILIZADORES.keys())
    )
    senha_digitada = st.text_input(
        "Digite a palavra-passe (password):", type="password"
    )

    if st.button("Entrar"):
      if senha_digitada == UTILIZADORES[nome_utilizador]["senha"]:
        st.session_state["autenticado"] = True
        st.session_state["utilizador_atual"] = UTILIZADORES[nome_utilizador][
            "nome"
        ]
        st.session_state["perfil_atual"] = UTILIZADORES[nome_utilizador][
            "perfil"
        ]
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

# Barra lateral com dados da sessão e Terminar Sessão
with st.sidebar:
  st.write(f"Utilizador: **{st.session_state['utilizador_atual']}**")
  st.write(f"Perfil: **{st.session_state['perfil_atual']}**")
  if st.button("Sair (Logout)"):
    st.session_state["autenticado"] = False
    st.session_state["utilizador_atual"] = None
    st.session_state["perfil_atual"] = None
    st.rerun()
  st.markdown("---")

# Título Principal do App
st.title("📊 Controlo de Stock e Vendas")

# Definição de Abas Conforme o Perfil (Utilizador comum não vê a aba Stock)
if st.session_state["perfil_atual"] == "Admin":
  aba_venda, aba_stock, aba_historico = st.tabs(
      ["🛒 Vendas", "📦 Stock", "📋 Histórico"]
  )
else:
  aba_venda, aba_historico = st.tabs(["🛒 Vendas", "📋 Histórico"])

# ---------------------------------------------------------
# 1. ABA: REGISTAR VENDA
# ---------------------------------------------------------
with aba_venda:
  st.subheader("Registo de Vendas")

  if df_stock.empty:
    st.warning("Cadastre primeiro os produtos na aba 'Stock' (Acesso Admin necessário).")
  else:
    with st.form("form_venda_novo", clear_on_submit=True):
      produto_selecionado = st.selectbox(
          "Produto", df_stock["Produto"].unique()
      )
      quantidade = st.number_input(
          "Quantidade Vendida", min_value=1, step=1, value=1
      )
      data_venda = st.date_input("Data da Venda", value=datetime.date.today())

      submit = st.form_submit_button("Salvar Nova Venda")

      if submit:
        dados_prod = df_stock[df_stock["Produto"] == produto_selecionado].iloc[0]
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
        st.session_state["sucesso_venda"] = True

    if st.session_state.get("sucesso_venda", False):
      st.success("Seu pedido foi salvo com sucesso!")
      st.session_state["sucesso_venda"] = False

# ---------------------------------------------------------
# 2. ABA: GERIR STOCK (Exclusiva para Admin)
# ---------------------------------------------------------
if st.session_state["perfil_atual"] == "Admin":
  with aba_stock:
    st.subheader("📦 Gestão de Produtos")

    acao_produto = st.radio(
        "Operação:", ["Novo", "Nova Entrada", "Editar", "Eliminar"],
        horizontal=True,
    )

    if acao_produto == "Novo":
      with st.form("form_novo_produto", clear_on_submit=True):
        n_prod = st.text_input("Nome do Produto")
        s_inic = st.number_input("Stock Inicial", min_value=0, step=1)
        p_comp = st.number_input(
            "Preço Compra Padrão", min_value=0.0, format="%.2f"
        )
        p_vend = st.number_input(
            "Preço Venda Padrão", min_value=0.0, format="%.2f"
        )

        if st.form_submit_button("Guardar Produto"):
          if n_prod:
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
          else:
            st.warning("Insira o nome do produto.")

    elif acao_produto == "Nova Entrada":
      if df_stock.empty:
        st.info("Nenhum produto cadastrado.")
      else:
        with st.form("form_nova_entrada", clear_on_submit=True):
          prod_entrada = st.selectbox(
              "Selecione o Produto para adicionar stock:", df_stock["Produto"]
          )
          qtd_adicionar = st.number_input(
              "Quantidade a Adicionar", min_value=1, step=1, value=1
          )

          if st.form_submit_button("Atualizar Stock"):
            idx_e = df_stock[df_stock["Produto"] == prod_entrada].index[0]
            stock_atual = int(df_stock.at[idx_e, "Stock Inicial"])
            df_stock.at[idx_e, "Stock Inicial"] = stock_atual + qtd_adicionar
            df_stock.to_csv(STOCK_FILE, index=False)
            st.success(
                f"Adicionado {qtd_adicionar} unidades ao produto"
                f" '{prod_entrada}' com sucesso!"
            )
            st.rerun()

    elif acao_produto == "Editar":
      if df_stock.empty:
        st.info("Nenhum produto cadastrado.")
      else:
        produto_a_editar = st.selectbox(
            "Selecione o produto para editar:", df_stock["Produto"]
        )
        idx_prod = df_stock[df_stock["Produto"] == produto_a_editar].index[0]
        row_prod_atual = df_stock.loc[idx_prod]

        with st.form("form_editar_produto"):
          st.write(f"Código: {row_prod_atual['Código']}")
          novo_nome_prod = st.text_input(
              "Nome do Produto", value=str(row_prod_atual["Produto"])
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

    # A opção de apagar vendas só aparece se for Admin
    if st.session_state["perfil_atual"] == "Admin":
      with st.expander("Apagar registo de venda"):
        venda_apagar = st.selectbox(
            "Selecione a venda a excluir:", df_vendas.index
        )
        if st.button("Eliminar Venda"):
          df_vendas = df_vendas.drop(venda_apagar).reset_index(drop=True)
          df_vendas.to_csv(VENDAS_FILE, index=False)
          st.success("Venda eliminada!")
          st.rerun()
