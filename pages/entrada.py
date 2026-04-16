"""
pages/entrada.py — Entrada de produtos
"""
import uuid
import datetime
import streamlit as st
from utils.database import (
    buscar_produto_por_ean, criar_produto, registrar_entrada,
    criar_nota_fiscal, upload_nota_pdf, listar_categorias, listar_entradas
)
from utils.auth import sessao_usuario
from utils.ui import badge

UNIDADES = ["UN", "CX", "KG", "LT", "MT", "PC", "RL", "FR", "GL", "DZ", "CT"]


def tela_entrada():
    st.markdown('<div class="sfc-page">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-title">📥 Entrada de Produtos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-sub">Registre entradas por EAN/código ou de forma avulsa</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Nova Entrada", "Histórico"])

    with tab1:
        _form_entrada()

    with tab2:
        _historico_entradas()

    st.markdown("</div>", unsafe_allow_html=True)


def _form_entrada():
    usuario = sessao_usuario()
    categorias = listar_categorias()
    cat_map = {c["nome"]: c["id"] for c in categorias}

    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">🔍 Identificar Produto</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        ean_input = st.text_input("EAN / Código de Barras", placeholder="Bipe ou digite o código", key="ean_busca")
    with col2:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        buscar = st.button("Buscar →", use_container_width=True)

    produto_encontrado = None
    produto_novo = False

    if buscar and ean_input.strip():
        produto_encontrado = buscar_produto_por_ean(ean_input.strip())
        if produto_encontrado:
            st.success(f"✅ Produto encontrado: **{produto_encontrado['nome']}** — {produto_encontrado['codigo_interno']}")
            st.session_state["produto_entrada"] = produto_encontrado
        else:
            st.warning("⚠️ Produto não encontrado. Preencha o cadastro abaixo.")
            st.session_state["produto_entrada"] = None
            st.session_state["ean_novo"] = ean_input.strip()
            produto_novo = True

    if "produto_entrada" in st.session_state and st.session_state["produto_entrada"]:
        produto_encontrado = st.session_state["produto_entrada"]

    st.markdown("</div>", unsafe_allow_html=True)

    # ── CADASTRO NOVO PRODUTO ────────────────────────────────────
    if produto_novo or ("ean_novo" in st.session_state and not produto_encontrado):
        st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
        st.markdown('<div class="sfc-card-header">📋 Cadastrar Novo Produto</div>', unsafe_allow_html=True)

        with st.form("form_novo_produto"):
            col1, col2 = st.columns(2)
            with col1:
                nome_p     = st.text_input("Nome do produto *", placeholder="Ex: Papel A4 75g")
                ean_p      = st.text_input("EAN", value=st.session_state.get("ean_novo", ""))
                categoria_p = st.selectbox("Categoria", list(cat_map.keys()))
            with col2:
                unidade_p  = st.selectbox("Unidade padrão", UNIDADES)
                fator_p    = st.number_input("Fator de conversão", value=1.0, min_value=0.001, step=0.001,
                                              help="Ex: 1 CX = 500 UN → fator=500")
                est_min_p  = st.number_input("Estoque mínimo", value=0.0, min_value=0.0, step=1.0)
            descricao_p = st.text_area("Descrição", height=80)

            salvar_produto = st.form_submit_button("Cadastrar Produto →", type="primary")
            if salvar_produto:
                if not nome_p.strip():
                    st.error("Nome do produto é obrigatório.")
                else:
                    novo = criar_produto({
                        "nome": nome_p.strip(),
                        "ean": ean_p.strip() or None,
                        "categoria_id": cat_map.get(categoria_p),
                        "unidade": unidade_p,
                        "fator_conversao": fator_p,
                        "estoque_minimo": est_min_p,
                        "descricao": descricao_p.strip() or None,
                    })
                    st.success(f"✅ Produto **{novo['nome']}** cadastrado com código **{novo['codigo_interno']}**")
                    st.session_state["produto_entrada"] = novo
                    if "ean_novo" in st.session_state:
                        del st.session_state["ean_novo"]
                    produto_encontrado = novo
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── ENTRADA AVULSA (sem EAN) ──────────────────────────────────
    if not produto_encontrado and "ean_novo" not in st.session_state:
        with st.expander("➕ Entrada Avulsa (sem EAN)"):
            with st.form("form_avulso"):
                col1, col2 = st.columns(2)
                with col1:
                    nome_av = st.text_input("Nome do produto *")
                    cat_av  = st.selectbox("Categoria", list(cat_map.keys()))
                with col2:
                    unidade_av = st.selectbox("Unidade", UNIDADES, key="un_av")
                    est_min_av = st.number_input("Estoque mínimo", value=0.0, min_value=0.0)
                if st.form_submit_button("Criar Produto Avulso →"):
                    if nome_av.strip():
                        novo = criar_produto({
                            "nome": nome_av.strip(),
                            "categoria_id": cat_map.get(cat_av),
                            "unidade": unidade_av,
                            "estoque_minimo": est_min_av,
                        })
                        st.session_state["produto_entrada"] = novo
                        st.rerun()

    # ── FORMULÁRIO DE ENTRADA ─────────────────────────────────────
    if produto_encontrado:
        st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
        st.markdown('<div class="sfc-card-header">📥 Registrar Entrada</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Produto", produto_encontrado["nome"])
        with col2:
            st.metric("Código", produto_encontrado["codigo_interno"])
        with col3:
            st.metric("Estoque Atual", f"{produto_encontrado['estoque_atual']} {produto_encontrado['unidade']}")

        st.markdown('<hr class="sfc-divider">', unsafe_allow_html=True)

        with st.form("form_entrada_registro"):
            col1, col2 = st.columns(2)
            with col1:
                qtd        = st.number_input("Quantidade *", min_value=0.001, value=1.0, step=1.0)
                unidade_e  = st.selectbox("Unidade", UNIDADES,
                                           index=UNIDADES.index(produto_encontrado["unidade"]))
            with col2:
                fator_c    = st.number_input("Fator conversão p/ unidade base",
                                              value=float(produto_encontrado.get("fator_conversao", 1)),
                                              min_value=0.001, step=0.001,
                                              help="Qtd × fator = quantidade na unidade padrão")
                qtd_base_preview = qtd * fator_c
                st.metric("Qtd base (calculada)", f"{qtd_base_preview:.3f} {produto_encontrado['unidade']}")

            st.markdown("**Nota Fiscal**")
            col1, col2, col3 = st.columns(3)
            with col1:
                nf_numero     = st.text_input("Número NF", placeholder="Ex: 00123456")
            with col2:
                nf_fornecedor = st.text_input("Fornecedor", placeholder="Nome da empresa")
            with col3:
                nf_valor      = st.number_input("Valor total R$", min_value=0.0, step=0.01)
            nf_pdf = st.file_uploader("PDF da Nota Fiscal", type=["pdf"])
            obs    = st.text_area("Observação", height=70)

            registrar = st.form_submit_button("✅ Registrar Entrada", type="primary", use_container_width=True)

            if registrar:
                nf_id  = None
                nf_url = None

                if nf_numero.strip():
                    # Upload PDF se enviado
                    if nf_pdf:
                        ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                        nome_arq = f"{ts}_{nf_numero.strip()}.pdf"
                        nf_url = upload_nota_pdf(nf_pdf.read(), nome_arq)

                    nf = criar_nota_fiscal({
                        "numero": nf_numero.strip(),
                        "fornecedor": nf_fornecedor.strip() or "Não informado",
                        "valor_total": nf_valor or None,
                        "arquivo_nome": nf_pdf.name if nf_pdf else None,
                        "arquivo_url": nf_url,
                        "criado_por": usuario["id"],
                    })
                    nf_id = nf["id"]

                registrar_entrada({
                    "produto_id":      produto_encontrado["id"],
                    "nota_fiscal_id":  nf_id,
                    "quantidade":      qtd,
                    "unidade":         unidade_e,
                    "quantidade_base": qtd_base_preview,
                    "observacao":      obs.strip() or None,
                    "registrado_por":  usuario["id"],
                })
                st.success(f"✅ Entrada de **{qtd} {unidade_e}** de **{produto_encontrado['nome']}** registrada!")
                if nf_id:
                    st.info("📎 Nota fiscal vinculada. Acesse 'Notas Fiscais' para enviar ao financeiro.")

                # Limpa estado
                for k in ["produto_entrada", "ean_novo", "ean_busca"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        if st.button("🔄 Limpar / Nova entrada"):
            for k in ["produto_entrada", "ean_novo"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def _historico_entradas():
    entradas = listar_entradas(100)

    if not entradas:
        st.info("Nenhuma entrada registrada.")
        return

    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="sfc-card-header">Últimas {len(entradas)} entradas</div>', unsafe_allow_html=True)

    rows = ""
    for e in entradas:
        produto_nome = (e.get("produtos") or {}).get("nome", "—")
        codigo       = (e.get("produtos") or {}).get("codigo_interno", "—")
        nf_num       = (e.get("notas_fiscais") or {}).get("numero", "—") if e.get("notas_fiscais") else "—"
        usuario_nome = (e.get("usuarios") or {}).get("nome", "—") if e.get("usuarios") else "—"
        data         = e["criado_em"][:16].replace("T", " ")

        rows += f"""
        <tr>
            <td>{data}</td>
            <td><strong>{produto_nome}</strong></td>
            <td style="color:#5c647a">{codigo}</td>
            <td>{e['quantidade']} {e['unidade']}</td>
            <td style="color:#5c647a">{nf_num}</td>
            <td style="color:#5c647a">{usuario_nome}</td>
        </tr>"""

    st.markdown(f"""
    <table class="sfc-table">
        <thead>
            <tr>
                <th>Data/Hora</th><th>Produto</th><th>Código</th>
                <th>Quantidade</th><th>NF</th><th>Registrado por</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
