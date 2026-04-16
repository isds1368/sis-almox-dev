"""
pages/saida.py — Saída de produtos com fluxo de autorização
"""
import datetime
import streamlit as st
from utils.database import (
    listar_produtos, registrar_saida, listar_saidas, atualizar_saida
)
from utils.auth import sessao_usuario, is_admin, is_almoxarife
from utils.ui import badge

UNIDADES = ["UN", "CX", "KG", "LT", "MT", "PC", "RL", "FR", "GL", "DZ", "CT"]

SETORES = [
    "Administrativo", "Financeiro", "RH", "TI", "Manutenção",
    "Operações", "Logística", "Marketing", "Comercial", "Diretoria", "Outro"
]


def tela_saida():
    st.markdown('<div class="sfc-page">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-title">📤 Saída de Produtos</div>', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-sub">Solicite, autorize e execute baixas de estoque</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Nova Solicitação", "Pendentes / Autorização", "Histórico"])

    with tab1:
        _form_nova_saida()
    with tab2:
        _pendentes()
    with tab3:
        _historico_saidas()

    st.markdown("</div>", unsafe_allow_html=True)


def _form_nova_saida():
    usuario = sessao_usuario()
    produtos = listar_produtos()

    if not produtos:
        st.warning("Nenhum produto cadastrado.")
        return

    prod_map = {f"{p['nome']} ({p['codigo_interno']})": p for p in produtos}

    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">📋 Solicitar Saída</div>', unsafe_allow_html=True)

    with st.form("form_saida"):
        col1, col2 = st.columns(2)
        with col1:
            prod_label  = st.selectbox("Produto *", list(prod_map.keys()))
            produto     = prod_map[prod_label]
            qtd         = st.number_input("Quantidade *", min_value=0.001, value=1.0, step=1.0)
            unidade_s   = st.selectbox("Unidade", UNIDADES,
                                        index=UNIDADES.index(produto["unidade"]))
        with col2:
            setor       = st.selectbox("Setor solicitante *", SETORES)
            retirante   = st.text_input("Nome do retirante *", placeholder="Quem vai retirar o item")
            obs         = st.text_area("Observação", height=80)

        # Exibe saldo disponível
        st.markdown(f"""
        <div style="padding:0.8rem;background:#0d0f14;border-radius:8px;border:1px solid #1e2230;margin:0.5rem 0;">
            <span style="font-size:0.78rem;color:#5c647a;">SALDO DISPONÍVEL: </span>
            <strong style="color:#3d8ef0;">{produto['estoque_atual']} {produto['unidade']}</strong>
            {'<span style="color:#f87171;margin-left:0.5rem;font-size:0.78rem;">⚠️ Estoque insuficiente</span>' if produto['estoque_atual'] <= 0 else ''}
        </div>
        """, unsafe_allow_html=True)

        fator_c    = float(produto.get("fator_conversao", 1))
        qtd_base   = qtd * fator_c

        submitted = st.form_submit_button("Registrar Solicitação →", type="primary", use_container_width=True)

        if submitted:
            erros = []
            if not retirante.strip():
                erros.append("Nome do retirante é obrigatório.")
            if produto["estoque_atual"] < qtd_base:
                erros.append(
                    f"Estoque insuficiente. Disponível: {produto['estoque_atual']} {produto['unidade']}."
                )

            if erros:
                for e in erros:
                    st.error(e)
            else:
                registrar_saida({
                    "produto_id":        produto["id"],
                    "quantidade":        qtd,
                    "unidade":           unidade_s,
                    "quantidade_base":   qtd_base,
                    "setor_solicitante": setor,
                    "nome_retirante":    retirante.strip(),
                    "status":            "pendente",
                    "solicitado_por":    usuario["id"],
                    "observacao":        obs.strip() or None,
                })
                st.success(f"✅ Solicitação registrada para **{prod_label}** — aguardando autorização.")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _pendentes():
    usuario   = sessao_usuario()
    pendentes = listar_saidas("pendente")
    autorizados = listar_saidas("autorizado")

    # ── PENDENTES (aguardando autorização de admin) ────────────────
    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">🔐 Aguardando Autorização</div>', unsafe_allow_html=True)

    if not pendentes:
        st.markdown('<p style="color:#5c647a;font-size:0.85rem;">Nenhuma solicitação pendente.</p>', unsafe_allow_html=True)
    else:
        for s in pendentes:
            prod     = s.get("produtos") or {}
            solicit  = s.get("solicitado") or {}
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            with col1:
                st.markdown(f"**{prod.get('nome','—')}** `{prod.get('codigo_interno','')}`")
                st.caption(f"Solicitado por: {solicit.get('nome','—')} | {s['criado_em'][:16].replace('T',' ')}")
            with col2:
                st.markdown(f"**{s['quantidade']} {s['unidade']}**")
                st.caption(f"Setor: {s['setor_solicitante']}")
            with col3:
                st.caption(f"Retirante: {s['nome_retirante']}")
                st.markdown(badge("Pendente", "pendente"), unsafe_allow_html=True)
            with col4:
                if is_admin():
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅", key=f"aut_{s['id']}", help="Autorizar"):
                            atualizar_saida(s["id"], {
                                "status": "autorizado",
                                "autorizado_por": usuario["id"],
                                "autorizado_em": datetime.datetime.utcnow().isoformat(),
                            })
                            st.rerun()
                    with c2:
                        if st.button("❌", key=f"can_{s['id']}", help="Cancelar"):
                            atualizar_saida(s["id"], {"status": "cancelado"})
                            st.rerun()
                else:
                    st.caption("Aguardando admin")
            st.markdown('<hr class="sfc-divider">', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ── AUTORIZADOS (aguardando execução pelo almoxarife) ─────────
    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">✅ Autorizados — Aguardando Baixa</div>', unsafe_allow_html=True)

    if not autorizados:
        st.markdown('<p style="color:#5c647a;font-size:0.85rem;">Nenhuma saída autorizada pendente de execução.</p>', unsafe_allow_html=True)
    else:
        for s in autorizados:
            prod  = s.get("produtos") or {}
            autor = s.get("autorizado") or {}
            col1, col2, col3 = st.columns([3, 3, 2])
            with col1:
                st.markdown(f"**{prod.get('nome','—')}** — {s['quantidade']} {s['unidade']}")
                st.caption(f"Setor: {s['setor_solicitante']} | Retirante: {s['nome_retirante']}")
            with col2:
                st.caption(f"Autorizado por: {autor.get('nome','—')}")
                st.markdown(badge("Autorizado", "autorizado"), unsafe_allow_html=True)
            with col3:
                if is_almoxarife():
                    if st.button("Executar Baixa ↓", key=f"exec_{s['id']}", type="primary"):
                        # Verifica saldo novamente antes de executar
                        from utils.database import buscar_produto_por_id
                        p = buscar_produto_por_id(prod.get("id", ""))
                        if p and p["estoque_atual"] >= s["quantidade_base"]:
                            atualizar_saida(s["id"], {
                                "status": "executado",
                                "executado_por": usuario["id"],
                                "executado_em": datetime.datetime.utcnow().isoformat(),
                            })
                            st.success("Baixa executada com sucesso!")
                            st.rerun()
                        else:
                            st.error("Estoque insuficiente para executar a baixa.")
            st.markdown('<hr class="sfc-divider">', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _historico_saidas():
    saidas = listar_saidas(limite=150)

    if not saidas:
        st.info("Nenhuma saída registrada.")
        return

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_status = st.selectbox(
            "Filtrar por status",
            ["Todos", "pendente", "autorizado", "executado", "cancelado"]
        )
    with col2:
        filtro_setor = st.text_input("Filtrar por setor", placeholder="Ex: TI")

    if filtro_status != "Todos":
        saidas = [s for s in saidas if s["status"] == filtro_status]
    if filtro_setor.strip():
        saidas = [s for s in saidas if filtro_setor.lower() in s["setor_solicitante"].lower()]

    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)

    rows = ""
    for s in saidas:
        prod      = s.get("produtos") or {}
        solicit   = s.get("solicitado") or {}
        data      = s["criado_em"][:16].replace("T", " ")
        status_b  = badge(s["status"].capitalize(), s["status"])
        rows += f"""
        <tr>
            <td>{data}</td>
            <td><strong>{prod.get('nome','—')}</strong></td>
            <td>{s['quantidade']} {s['unidade']}</td>
            <td>{s['setor_solicitante']}</td>
            <td>{s['nome_retirante']}</td>
            <td>{solicit.get('nome','—')}</td>
            <td>{status_b}</td>
        </tr>"""

    st.markdown(f"""
    <table class="sfc-table">
        <thead>
            <tr>
                <th>Data</th><th>Produto</th><th>Qtd</th>
                <th>Setor</th><th>Retirante</th><th>Solicitado por</th><th>Status</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
