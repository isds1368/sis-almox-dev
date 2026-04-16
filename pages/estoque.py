"""
pages/estoque.py — Controle de Estoque
"""
import streamlit as st
from utils.database import (
    listar_produtos, atualizar_produto, registrar_ajuste,
    listar_categorias, listar_ajustes
)
from utils.auth import sessao_usuario, is_admin
from utils.ui import status_estoque_badge, badge

UNIDADES = ["UN", "CX", "KG", "LT", "MT", "PC", "RL", "FR", "GL", "DZ", "CT"]


def tela_estoque():
    st.markdown('<div class="sfc-page">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-title">📦 Controle de Estoque</div>', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-sub">Visão completa do inventário com filtros e ajustes</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Inventário", "Ajuste Manual", "Histórico de Ajustes"])

    with tab1:
        _inventario()
    with tab2:
        if is_admin():
            _ajuste_manual()
        else:
            st.warning("🔒 Apenas administradores podem realizar ajustes manuais.")
    with tab3:
        _historico_ajustes()

    st.markdown("</div>", unsafe_allow_html=True)


def _inventario():
    produtos = listar_produtos()
    categorias = listar_categorias()
    cat_nomes = ["Todas"] + [c["nome"] for c in categorias]

    if not produtos:
        st.info("Nenhum produto cadastrado.")
        return

    # ── FILTROS ───────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    with col1:
        busca = st.text_input("🔍 Buscar", placeholder="Nome, código ou EAN")
    with col2:
        cat_filtro = st.selectbox("Categoria", cat_nomes)
    with col3:
        status_filtro = st.selectbox("Status", ["Todos", "OK", "Baixo", "Crítico"])
    with col4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("↺", help="Limpar filtros"):
            st.rerun()

    # ── MÉTRICAS RÁPIDAS ──────────────────────────────────────────
    total    = len(produtos)
    criticos = sum(1 for p in produtos if p["estoque_atual"] <= 0)
    baixos   = sum(1 for p in produtos if 0 < p["estoque_atual"] <= p["estoque_minimo"])
    ok       = total - criticos - baixos

    st.markdown(f"""
    <div class="sfc-metrics">
        {_mc("Total de Produtos", total, "", "#3d8ef0")}
        {_mc("OK", ok, "Estoque normal", "#34d399")}
        {_mc("Estoque Baixo", baixos, "Abaixo do mínimo", "#fbbf24")}
        {_mc("Crítico / Zerado", criticos, "Sem estoque", "#f87171")}
    </div>
    """, unsafe_allow_html=True)

    # ── FILTRAGEM ─────────────────────────────────────────────────
    def get_status(p):
        if p["estoque_atual"] <= 0:
            return "Crítico"
        if p["estoque_atual"] <= p["estoque_minimo"]:
            return "Baixo"
        return "OK"

    filtrados = produtos
    if busca.strip():
        b = busca.lower()
        filtrados = [p for p in filtrados if
                     b in p["nome"].lower()
                     or b in p["codigo_interno"].lower()
                     or (p.get("ean") and b in p["ean"].lower())]
    if cat_filtro != "Todas":
        filtrados = [p for p in filtrados
                     if p.get("categorias") and p["categorias"]["nome"] == cat_filtro]
    if status_filtro != "Todos":
        filtrados = [p for p in filtrados if get_status(p) == status_filtro]

    # ── TABELA ────────────────────────────────────────────────────
    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="sfc-card-header">Produtos ({len(filtrados)})</div>', unsafe_allow_html=True)

    rows = ""
    for p in filtrados:
        cat_nome  = (p.get("categorias") or {}).get("nome", "—")
        status_b  = status_estoque_badge(p["estoque_atual"], p["estoque_minimo"])
        est_color = "#f87171" if p["estoque_atual"] <= 0 else ("#fbbf24" if p["estoque_atual"] <= p["estoque_minimo"] else "#34d399")
        rows += f"""
        <tr>
            <td><strong>{p['nome']}</strong></td>
            <td style="color:#5c647a;font-size:0.8rem;">{p['codigo_interno']}</td>
            <td style="color:#5c647a;font-size:0.8rem;">{p.get('ean') or '—'}</td>
            <td style="color:#5c647a;font-size:0.8rem;">{cat_nome}</td>
            <td style="color:{est_color};font-weight:600;">{p['estoque_atual']} {p['unidade']}</td>
            <td style="color:#5c647a;">{p['estoque_minimo']} {p['unidade']}</td>
            <td>{status_b}</td>
        </tr>"""

    st.markdown(f"""
    <table class="sfc-table">
        <thead>
            <tr>
                <th>Produto</th><th>Código</th><th>EAN</th><th>Categoria</th>
                <th>Estoque Atual</th><th>Mín.</th><th>Status</th>
            </tr>
        </thead>
        <tbody>{rows if rows else '<tr><td colspan="7" style="text-align:center;color:#5c647a;padding:2rem;">Nenhum produto encontrado</td></tr>'}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── EDIÇÃO DE PRODUTO ──────────────────────────────────────────
    if is_admin() and filtrados:
        with st.expander("✏️ Editar produto"):
            categorias_db = listar_categorias()
            cat_map = {c["nome"]: c["id"] for c in categorias_db}
            prod_labels = {f"{p['nome']} ({p['codigo_interno']})": p for p in filtrados}
            sel = st.selectbox("Selecione o produto", list(prod_labels.keys()), key="edit_prod_sel")
            p = prod_labels[sel]

            with st.form("form_edit_prod"):
                col1, col2 = st.columns(2)
                with col1:
                    nome_e     = st.text_input("Nome", value=p["nome"])
                    cat_atual  = next((c["nome"] for c in categorias_db if c["id"] == p.get("categoria_id")), list(cat_map.keys())[0])
                    cat_e      = st.selectbox("Categoria", list(cat_map.keys()), index=list(cat_map.keys()).index(cat_atual) if cat_atual in cat_map else 0)
                    unidade_e  = st.selectbox("Unidade", UNIDADES, index=UNIDADES.index(p["unidade"]) if p["unidade"] in UNIDADES else 0)
                with col2:
                    fator_e    = st.number_input("Fator conversão", value=float(p.get("fator_conversao", 1)), min_value=0.001)
                    est_min_e  = st.number_input("Estoque mínimo", value=float(p["estoque_minimo"]), min_value=0.0)
                    ean_e      = st.text_input("EAN", value=p.get("ean") or "")
                    ativo_e    = st.checkbox("Ativo", value=p.get("ativo", True))
                desc_e = st.text_area("Descrição", value=p.get("descricao") or "")
                if st.form_submit_button("Salvar alterações →", type="primary"):
                    atualizar_produto(p["id"], {
                        "nome": nome_e.strip(),
                        "categoria_id": cat_map.get(cat_e),
                        "unidade": unidade_e,
                        "fator_conversao": fator_e,
                        "estoque_minimo": est_min_e,
                        "ean": ean_e.strip() or None,
                        "descricao": desc_e.strip() or None,
                        "ativo": ativo_e,
                    })
                    st.success("✅ Produto atualizado!")
                    st.rerun()


def _mc(label, valor, sub, accent):
    return f"""
    <div class="sfc-metric" style="--accent:{accent};">
        <div class="sfc-metric-label">{label}</div>
        <div class="sfc-metric-value">{valor}</div>
        {"<div class='sfc-metric-sub'>" + sub + "</div>" if sub else ""}
    </div>"""


def _ajuste_manual():
    usuario = sessao_usuario()
    produtos = listar_produtos()
    if not produtos:
        st.info("Nenhum produto cadastrado.")
        return

    prod_map = {f"{p['nome']} ({p['codigo_interno']})": p for p in produtos}

    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">⚙️ Ajuste Manual de Estoque</div>', unsafe_allow_html=True)
    st.warning("⚠️ O ajuste manual sobrescreve o estoque atual. Use apenas para correções de inventário.")

    with st.form("form_ajuste"):
        sel     = st.selectbox("Produto *", list(prod_map.keys()))
        produto = prod_map[sel]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Estoque Atual", f"{produto['estoque_atual']} {produto['unidade']}")
            nova_qtd = st.number_input("Nova quantidade *", min_value=0.0, value=float(produto["estoque_atual"]), step=1.0)
        with col2:
            motivo = st.text_area("Motivo do ajuste *", placeholder="Ex: Inventário físico realizado em 12/06/2025", height=100)

        if st.form_submit_button("Aplicar Ajuste ↓", type="primary", use_container_width=True):
            if not motivo.strip():
                st.error("Informe o motivo do ajuste.")
            else:
                registrar_ajuste({
                    "produto_id":      produto["id"],
                    "quantidade_ant":  produto["estoque_atual"],
                    "quantidade_nova": nova_qtd,
                    "motivo":          motivo.strip(),
                    "ajustado_por":    usuario["id"],
                })
                st.success(f"✅ Estoque de **{produto['nome']}** ajustado para **{nova_qtd} {produto['unidade']}**")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _historico_ajustes():
    ajustes = listar_ajustes(50)
    if not ajustes:
        st.info("Nenhum ajuste registrado.")
        return

    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">Histórico de Ajustes</div>', unsafe_allow_html=True)

    rows = ""
    for a in ajustes:
        prod   = a.get("produtos") or {}
        user   = a.get("usuarios") or {}
        data   = a["criado_em"][:16].replace("T", " ")
        diff   = float(a["quantidade_nova"]) - float(a["quantidade_ant"])
        cor    = "#34d399" if diff >= 0 else "#f87171"
        rows += f"""
        <tr>
            <td>{data}</td>
            <td><strong>{prod.get('nome','—')}</strong></td>
            <td>{a['quantidade_ant']}</td>
            <td style="color:{cor};font-weight:600;">{a['quantidade_nova']}</td>
            <td style="color:{cor}">{'+' if diff>=0 else ''}{diff:.3f}</td>
            <td style="color:#5c647a;font-size:0.8rem;">{a['motivo'][:60]}{'…' if len(a['motivo'])>60 else ''}</td>
            <td style="color:#5c647a;">{user.get('nome','—')}</td>
        </tr>"""

    st.markdown(f"""
    <table class="sfc-table">
        <thead>
            <tr>
                <th>Data</th><th>Produto</th><th>Qtd Anterior</th>
                <th>Qtd Nova</th><th>Variação</th><th>Motivo</th><th>Responsável</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
