import datetime
import os
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Controlo de Stock e Vendas", page_icon="📊", layout="wide"
)

# Estilo CSS: Fundo rosa com padrão de flores coloridas e adaptação de texto
st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffb6c1;
        background-image: radial-gradient(#ff69b4 15%, transparent 16%), 
                            radial-gradient(#ff1493 15%, transparent 16%);
        background-size: 60px 60px;
        background-position: 0 0, 30px 30px;
        color: #2b2b2b;
    }
    /* Estilizar blocos e caixas para legibilidade sobre o fundo */
    div.stForm, .css-1dp5vir, .css-12oz5g7 {
        background-color: rgba(255, 255, 255, 0.88);
        padding: 20px;
        border-radius: 10px;
    }
    h1, h2, h3, h4, h5, h6, label, p {
        color: #1a1a1a !important;
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


# Carregar dados
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
st.title("📊 Sistema de Controlo de Stock e Vendas")

# Criação das Abas Principais (Tabs)
aba_venda, aba_stock, aba_historico = st.tabs(
    ["🛒 Registar / Refazer Venda", "📦 Gerir Stock", "📋 Histórico de Vendas"]
)

# ---------------------------------------------------------
# 1. ABA: REGISTAR / REFAZER VENDA
# ---------------------------------------------------------
with aba_venda:
  st.subheader("Registo e Edição de Vendas")

  modo = st.radio(
      "Selecione a ação:", ["Nova Venda", "Refazer / Editar Registo Anterior"],
      horizontal=True,
  )

  if df_stock.empty:
    st.warning("Cadastre primeiro os produtos na aba 'Gerir Stock'.")
  else:
    if modo == "Nova Venda":
      with st.form("form_venda_novo"):
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

        # Preços padrão do produto
        dados_prod = df_stock[df_stock["Produto"] == produto_selecionado].iloc[
            0
        ]
        p_compra_padrao = float(dados_prod["Preço de Compra"])
        p_venda_padrao = float(dados_prod["Preço de Venda"])

        with col2:
          preco_compra = st.number_input(
              "Preço de Compra (Unitário)",
              value=p_compra_padrao,
              format="%.2f",
          )
          custo_embalagem = st.number_input(
              "Custo de Embalagem (Total)", value=0.0, format="%.2f"
          )
          preco_venda = st.number_input(
              "Preço de Venda (Unitário)", value=p_venda_padrao, format="%.2f"
          )

        submit = st.form_submit_button("Salvar Nova Venda")

        if submit:
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

    else:  # Modo Refazer / Editar Venda
      if df_vendas.empty:
        st.info("Nenhuma venda registada para editar.")
      else:
        st.write(
            "Selecione uma venda abaixo para atualizar os dados (Refazer Registo):"
        )
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
          col1, col2 = st.columns(2)
          with col1:
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
          with col2:
            pc_edit = st.number_input(
                "Preço de Compra",
                value=float(row_atual["Preço de Compra"]),
                format="%.2f",
            )
            ce_edit = st.number_input(
                "Custo de Embalagem",
                value=float(row_atual["Custo de Embalagem"]),
                format="%.2f",
            )
            pv_edit = st.number_input(
                "Preço de Venda",
                value=float(row_atual["Preço de Venda"]),
                format="%.2f",
            )

          btn_atualizar = st.form_submit_button("Atualizar / Refazer Registo")

          if btn_atualizar:
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
# 2. ABA: GERIR STOCK (Com Código automático e Edição de Nome)
# ---------------------------------------------------------
with aba_stock:
  st.subheader("📦 Gestão de Produtos e Stock")

  acao_produto = st.radio(
      "Selecione a ação:",
      ["Adicionar Novo Produto", "Refazer / Editar Produto Existente"],
      horizontal=True,
  )

  if acao_produto == "Adicionar Novo Produto":
    with st.form("form_novo_produto"):
      st.write("Adicionar Novo Produto")
      c1, c2, c3, c4 = st.columns(4)
      with c1:
        n_prod = st.text_input("Nome do Produto")
      with c2:
        s_inic = st.number_input("Stock Inicial", min_value=0, step=1)
      with c3:
        p_comp = st.number_input(
            "Preço de Compra Padrão", min_value=0.0, format="%.2f"
        )
      with c4:
        p_vend = st.number_input(
            "Preço de Venda Padrão", min_value=0.0, format="%.2f"
        )

      btn_prod = st.form_submit_button("Salvar Produto")
      if btn_prod and n_prod:
        # Gerar código automático com base na quantidade de linhas (001, 002, etc.)
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
        st.success(
            f"Produto '{n_prod}' adicionado com o código {codigo_formatado}!"
        )
        st.rerun()

  else:  # Editar / Refazer Produto Existente
    if df_stock.empty:
      st.info("Nenhum produto cadastrado para editar.")
    else:
      produto_a_editar = st.selectbox(
          "Selecione o produto que deseja alterar:", df_stock["Produto"]
      )
      idx_prod = df_stock[df_stock["Produto"] == produto_a_editar].index[0]
      row_prod_atual = df_stock.loc[idx_prod]

      with st.form("form_editar_produto"):
        st.write(
            f"A editar o produto com Código: **{row_prod_atual['Código']}**"
        )
        ep1, ep2, ep3, ep4 = st.columns(4)
        with ep1:
          novo_nome_prod = st.text_input(
              "Novo Nome do Produto", value=str(row_prod_atual["Produto"])
          )
        with ep2:
          novo_stock = st.number_input(
              "Stock Inicial",
              min_value=0,
              step=1,
              value=int(row_prod_atual["Stock Inicial"]),
          )
        with ep3:
          novo_pc_padrao = st.number_input(
              "Preço de Compra",
              min_value=0.0,
              format="%.2f",
              value=float(row_prod_atual["Preço de Compra"]),
          )
        with ep4:
          novo_pv_padrao = st.number_input(
              "Preço de Venda",
              min_value=0.0,
              format="%.2f",
              value=float(row_prod_atual["Preço de Venda"]),
          )

        btn_atualizar_prod = st.form_submit_button("Atualizar Cadastro")

        if btn_atualizar_prod:
          df_stock.at[idx_prod, "Produto"] = novo_nome_prod
          df_stock.at[idx_prod, "Stock Inicial"] = novo_stock
          df_stock.at[idx_prod, "Preço de Compra"] = novo_pc_padrao
          df_stock.at[idx_prod, "Preço de Venda"] = novo_pv_padrao

          df_stock.to_csv(STOCK_FILE, index=False)
          st.success("Cadastro do produto atualizado com sucesso!")
          st.rerun()

  st.markdown("---")
  st.write("### Produtos Cadastrados")
  if not df_stock.empty:
    st.dataframe(df_stock, use_container_width=True)
  else:
    st.info("Nenhum produto cadastrado.")

# ---------------------------------------------------------
# 3. ABA: HISTÓRICO DE VENDAS
# ---------------------------------------------------------
with aba_historico:
  st.subheader("📋 Histórico Geral de Vendas e Lucros")

  if df_vendas.empty:
    st.info("Ainda não existem vendas registadas.")
  else:
    if "Descricao_Edit" in df_vendas.columns:
      df_vendas = df_vendas.drop(columns=["Descricao_Edit"])

    st.dataframe(df_vendas, use_container_width=True)

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Facturação Total", f"{df_vendas['Facturação'].sum():,.2f}")
    m2.metric("Lucro Total", f"{df_vendas['Lucro'].sum():,.2f}")
    m3.metric("Total de Vendas", len(df_vendas))

    with st.expander("Apagar um registo de venda"):
      venda_apagar = st.selectbox(
          "Selecione o registo para excluir:", df_vendas.index
      )
      if st.button("Eliminar Registo Selecionado"):
        df_vendas = df_vendas.drop(venda_apagar).reset_index(drop=True)
        df_vendas.to_csv(VENDAS_FILE, index=False)
        st.success("Registo eliminado com sucesso!")
        st.rerun()
