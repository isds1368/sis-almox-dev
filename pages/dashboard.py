"""
pages/dashboard.py — Dashboard com KPIs e gráficos
"""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from utils.database import stats_dashboard, listar_produtos
from utils.ui import badge

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#8891a8", size=12),
    margin=dict(l=0, r=0, t=30, b=0),
    showlegend=True,
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8891a8"),
    ),
    xaxis=dict(gridcolor="#1e2230", zerolinecolor="#1e2230"),
    yaxis=dict(gridcolor="#1e2230", zerolinecolor="#1e2230"),
)


def tela_dashboard():
    st.markdown('<div class="sfc-page">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-title">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-sub">Visão gerencial do almoxarifado em tempo real</div>', unsafe_allow_html=True)

    stats = stats_dashboard()

    # ── KPIs PRINCIPAIS ────────────────────────────────────────────
    st.markdown(f"""
    <div class="sfc-metrics">
        <div class="sfc-metric" style="--accent:#3d8ef0;">
            <div class="sfc-metric-label">Total de Produtos</div>
            <div class="sfc-metric-value">{stats['total_produtos']}</div>
            <div class="sfc-metric-sub">Itens ativos no estoque</div>
        </div>
        <div class="sfc-metric" style="--accent:#f87171;">
            <div class="sfc-metric-label">Críticos</div>
            <div class="sfc-metric-value">{stats['criticos']}</div>
            <div class="sfc-metric-sub">Estoque zerado</div>
        </div>
        <div class="sfc-metric" style="--accent:#fbbf24;">
            <div class="sfc-metric-label">Estoque Baixo</div>
            <div class="sfc-metric-value">{stats['baixos']}</div>
            <div class="sfc-metric-sub">Abaixo do mínimo</div>
        </div>
        <div class="sfc-metric" style="--accent:#34d399;">
            <div class="sfc-metric-label">Entradas</div>
            <div class="sfc-metric-value">{stats['entradas_count']}</div>
            <div class="sfc-metric-sub">Total registradas</div>
        </div>
        <div class="sfc-metric" style="--accent:#60d0f0;">
            <div class="sfc-metric-label">Saídas</div>
            <div class="sfc-metric-value">{stats['saidas_count']}</div>
            <div class="sfc-metric-sub">Total registradas</div>
        </div>
        <div class="sfc-metric" style="--accent:#a78bfa;">
            <div class="sfc-metric-label">Saídas Pendentes</div>
            <div class="sfc-metric-value">{stats['pendentes_saida']}</div>
            <div class="sfc-metric-sub">Aguardando autorização</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ALERTAS ────────────────────────────────────────────────────
    if stats["criticos"] > 0 or stats["baixos"] > 0 or stats["pendentes_notas"] > 0:
        st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
        st.markdown('<div class="sfc-card-header">🚨 Alertas</div>', unsafe_allow_html=True)

        if stats["criticos"] > 0:
            st.error(f"🔴 **{stats['criticos']} produto(s)** com estoque zerado — verifique o inventário.")
        if stats["baixos"] > 0:
            st.warning(f"🟡 **{stats['baixos']} produto(s)** com estoque abaixo do mínimo.")
        if stats["pendentes_notas"] > 0:
            st.info(f"📎 **{stats['pendentes_notas']} nota(s) fiscal(is)** pendente(s) de envio ao financeiro.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── GRÁFICOS ───────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        _grafico_consumo_setor(stats["consumo_setor"])

    with col2:
        _grafico_status_estoque(stats)

    col3, col4 = st.columns(2)

    with col3:
        _movimentacoes_recentes(stats)

    with col4:
        _produtos_criticos()

    st.markdown("</div>", unsafe_allow_html=True)


def _grafico_consumo_setor(consumo: dict):
    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">🏢 Consumo por Setor</div>', unsafe_allow_html=True)

    if not consumo:
        st.markdown('<p style="color:#5c647a;font-size:0.85rem;text-align:center;padding:1rem;">Nenhuma saída executada ainda.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    setores = list(consumo.keys())
    valores = list(consumo.values())
    cores   = ["#3d8ef0", "#34d399", "#fbbf24", "#a78bfa", "#60d0f0", "#f87171", "#fb923c"]

    fig = go.Figure(go.Bar(
        x=setores, y=valores,
        marker_color=cores[:len(setores)],
        hovertemplate="<b>%{x}</b><br>Qtd: %{y:.1f}<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, title="Quantidade consumida por setor")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _grafico_status_estoque(stats: dict):
    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">📦 Status do Inventário</div>', unsafe_allow_html=True)

    ok      = max(0, stats["total_produtos"] - stats["criticos"] - stats["baixos"])
    labels  = ["OK", "Baixo", "Crítico"]
    values  = [ok, stats["baixos"], stats["criticos"]]
    colors  = ["#34d399", "#fbbf24", "#f87171"]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.6,
        marker=dict(colors=colors, line=dict(color="#0d0f14", width=3)),
        hovertemplate="<b>%{label}</b>: %{value} produtos<extra></extra>",
        textfont=dict(color="#e8eaf0"),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        annotations=[dict(
            text=f"<b>{stats['total_produtos']}</b>",
            x=0.5, y=0.5, font_size=24, font_color="#e8eaf0",
            showarrow=False
        )]
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _movimentacoes_recentes(stats: dict):
    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">🔄 Movimentações Recentes</div>', unsafe_allow_html=True)

    ent  = stats["recentes_entradas"]
    said = stats["recentes_saidas"]

    if ent:
        st.markdown("**Entradas**")
        rows = ""
        for e in ent:
            prod = (e.get("produtos") or {}).get("nome", "—")
            data = e["criado_em"][:10]
            rows += f"""
            <tr>
                <td>{data}</td>
                <td>{prod[:30]}{'…' if len(prod)>30 else ''}</td>
                <td style="color:#34d399">+{e['quantidade']} {e['unidade']}</td>
            </tr>"""
        st.markdown(f"""
        <table class="sfc-table">
            <thead><tr><th>Data</th><th>Produto</th><th>Qtd</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>""", unsafe_allow_html=True)

    if said:
        st.markdown("**Saídas**")
        rows = ""
        for s in said:
            prod = (s.get("produtos") or {}).get("nome", "—")
            data = s["criado_em"][:10]
            status_b = badge(s["status"].capitalize(), s["status"])
            rows += f"""
            <tr>
                <td>{data}</td>
                <td>{prod[:25]}{'…' if len(prod)>25 else ''}</td>
                <td style="color:#f87171">-{s['quantidade']} {s['unidade']}</td>
                <td>{status_b}</td>
            </tr>"""
        st.markdown(f"""
        <table class="sfc-table">
            <thead><tr><th>Data</th><th>Produto</th><th>Qtd</th><th>Status</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>""", unsafe_allow_html=True)

    if not ent and not said:
        st.markdown('<p style="color:#5c647a;font-size:0.85rem;">Nenhuma movimentação registrada.</p>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _produtos_criticos():
    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">🔴 Produtos em Atenção</div>', unsafe_allow_html=True)

    produtos = listar_produtos()
    atencao = [p for p in produtos if p["estoque_atual"] <= p["estoque_minimo"]]

    if not atencao:
        st.markdown('<p style="color:#5c647a;font-size:0.85rem;">✅ Todos os produtos com estoque adequado.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    rows = ""
    for p in sorted(atencao, key=lambda x: x["estoque_atual"])[:10]:
        cor      = "#f87171" if p["estoque_atual"] <= 0 else "#fbbf24"
        tipo     = "Crítico" if p["estoque_atual"] <= 0 else "Baixo"
        tipo_cls = "critico" if p["estoque_atual"] <= 0 else "baixo"
        rows += f"""
        <tr>
            <td>{p['nome'][:35]}{'…' if len(p['nome'])>35 else ''}</td>
            <td style="color:{cor};font-weight:600;">{p['estoque_atual']}</td>
            <td style="color:#5c647a;">{p['estoque_minimo']}</td>
            <td><span class="badge badge-{tipo_cls}">{tipo}</span></td>
        </tr>"""

    st.markdown(f"""
    <table class="sfc-table">
        <thead><tr><th>Produto</th><th>Atual</th><th>Mínimo</th><th>Status</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
