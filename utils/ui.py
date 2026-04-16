"""
utils/ui.py — Componentes visuais e estilos globais
"""
import streamlit as st


# ─── PALETA & ESTILOS GLOBAIS ──────────────────────────────────────────────

CSS_GLOBAL = """
<style>
/* ── FONTS ──────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── RESET & BASE ───────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: #0d0f14;
    color: #e8eaf0;
}

/* ── SCROLLBAR ──────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #161921; }
::-webkit-scrollbar-thumb { background: #2e3347; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3d8ef0; }

/* ── HEADER OCULTO ──────────────────────── */
#MainMenu, footer, header { visibility: hidden; }

/* ── SIDEBAR OCULTA (usamos menu custom) ── */
[data-testid="stSidebar"] { display: none; }

/* ── CONTAINER PRINCIPAL ────────────────── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── TOPBAR ─────────────────────────────── */
.sfc-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #12151d;
    border-bottom: 1px solid #1e2230;
    padding: 0 2rem;
    height: 60px;
    position: sticky;
    top: 0;
    z-index: 999;
}
.sfc-topbar-brand {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: #3d8ef0;
    text-transform: uppercase;
    white-space: nowrap;
}
.sfc-topbar-brand span {
    color: #e8eaf0;
}
.sfc-nav {
    display: flex;
    gap: 0.2rem;
    align-items: center;
}
.sfc-nav-btn {
    background: transparent;
    border: none;
    color: #8891a8;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem;
    font-weight: 500;
    padding: 0.4rem 0.85rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
}
.sfc-nav-btn:hover { background: #1e2230; color: #e8eaf0; }
.sfc-nav-btn.active { background: #1a2a45; color: #3d8ef0; font-weight: 600; }
.sfc-user-chip {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: #1e2230;
    border-radius: 20px;
    padding: 0.3rem 0.9rem 0.3rem 0.5rem;
    font-size: 0.78rem;
    color: #8891a8;
}
.sfc-user-chip .avatar {
    width: 26px; height: 26px;
    background: #1a2a45;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; font-weight: 700; color: #3d8ef0;
}

/* ── PAGE WRAPPER ───────────────────────── */
.sfc-page {
    padding: 2rem 2.5rem;
    max-width: 1400px;
    margin: 0 auto;
}
.sfc-page-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #e8eaf0;
    margin-bottom: 0.2rem;
}
.sfc-page-sub {
    font-size: 0.85rem;
    color: #5c647a;
    margin-bottom: 2rem;
}

/* ── METRIC CARDS ───────────────────────── */
.sfc-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}
.sfc-metric {
    background: #12151d;
    border: 1px solid #1e2230;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.sfc-metric::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent, #3d8ef0);
    border-radius: 12px 12px 0 0;
}
.sfc-metric-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #5c647a;
    margin-bottom: 0.4rem;
}
.sfc-metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent, #3d8ef0);
    line-height: 1;
}
.sfc-metric-sub {
    font-size: 0.72rem;
    color: #5c647a;
    margin-top: 0.3rem;
}

/* ── STATUS BADGES ──────────────────────── */
.badge {
    display: inline-block;
    padding: 0.18rem 0.6rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-ok       { background: #0e2a1a; color: #34d399; border: 1px solid #1a4a30; }
.badge-baixo    { background: #2a1e0a; color: #fbbf24; border: 1px solid #4a3a10; }
.badge-critico  { background: #2a0e0e; color: #f87171; border: 1px solid #4a1e1e; }
.badge-pendente { background: #1e1a2a; color: #a78bfa; border: 1px solid #3a2a50; }
.badge-enviado  { background: #0e2a1a; color: #34d399; border: 1px solid #1a4a30; }
.badge-autorizado { background: #0a1e2a; color: #60d0f0; border: 1px solid #103040; }
.badge-executado  { background: #0e2a1a; color: #34d399; border: 1px solid #1a4a30; }
.badge-cancelado  { background: #2a0e0e; color: #f87171; border: 1px solid #4a1e1e; }

/* ── CARD GENÉRICO ──────────────────────── */
.sfc-card {
    background: #12151d;
    border: 1px solid #1e2230;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.sfc-card-header {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #e8eaf0;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #1e2230;
}

/* ── TABELA ─────────────────────────────── */
.sfc-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
}
.sfc-table th {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #5c647a;
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid #1e2230;
    text-align: left;
    white-space: nowrap;
}
.sfc-table td {
    padding: 0.65rem 0.8rem;
    border-bottom: 1px solid #161921;
    color: #c8cad8;
    vertical-align: middle;
}
.sfc-table tr:hover td { background: #14171f; }

/* ── INPUTS STREAMLIT ───────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] {
    background: #161921 !important;
    border-color: #1e2230 !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: #3d8ef0 !important;
    box-shadow: 0 0 0 2px rgba(61,142,240,0.15) !important;
}

/* ── BOTÕES STREAMLIT ───────────────────── */
[data-testid="stButton"] button {
    background: #1a2a45 !important;
    border: 1px solid #2a3a5a !important;
    color: #3d8ef0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
}
[data-testid="stButton"] button:hover {
    background: #1e3255 !important;
    border-color: #3d8ef0 !important;
}
[data-testid="stButton"] button[kind="primary"] {
    background: #3d8ef0 !important;
    border-color: #3d8ef0 !important;
    color: #fff !important;
}
[data-testid="stButton"] button[kind="primary"]:hover {
    background: #2d7de0 !important;
}

/* ── EXPANDER ───────────────────────────── */
[data-testid="stExpander"] {
    background: #12151d !important;
    border: 1px solid #1e2230 !important;
    border-radius: 10px !important;
}

/* ── ALERT / SUCCESS / ERROR ────────────── */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}

/* ── DIVIDER ────────────────────────────── */
.sfc-divider {
    border: none;
    border-top: 1px solid #1e2230;
    margin: 1.5rem 0;
}

/* ── HOME ───────────────────────────────── */
.sfc-home {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: calc(100vh - 60px);
    text-align: center;
    padding: 2rem;
}
.sfc-home-logo {
    font-family: 'Syne', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    color: #3d8ef0;
    letter-spacing: 0.06em;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.sfc-home-logo span { color: #e8eaf0; }
.sfc-home-sub {
    font-size: 1rem;
    color: #5c647a;
    margin-bottom: 2.5rem;
    letter-spacing: 0.05em;
}

/* ── FORM CARD ──────────────────────────── */
.sfc-form-card {
    background: #12151d;
    border: 1px solid #1e2230;
    border-radius: 16px;
    padding: 2.5rem;
    max-width: 420px;
    margin: 0 auto;
    box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}
.sfc-form-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #e8eaf0;
    margin-bottom: 0.3rem;
}
.sfc-form-sub {
    font-size: 0.82rem;
    color: #5c647a;
    margin-bottom: 1.5rem;
}
</style>
"""


def inject_css():
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


def topbar(pagina_atual: str, usuario: dict):
    """Renderiza a barra superior com navegação."""
    from utils.auth import is_admin

    PAGINAS = [
        ("🏠 Início",        "home"),
        ("📥 Entrada",       "entrada"),
        ("📤 Saída",         "saida"),
        ("📦 Estoque",       "estoque"),
        ("📎 Notas Fiscais", "notas"),
        ("📊 Dashboard",     "dashboard"),
    ]
    if is_admin():
        PAGINAS.append(("👥 Usuários", "usuarios"))

    nav_html = "".join(
        f'<button class="sfc-nav-btn {"active" if p == pagina_atual else ""}" '
        f'onclick="window.location.href=\'?page={p}\'">{label}</button>'
        for label, p in PAGINAS
    )

    iniciais = "".join(w[0].upper() for w in usuario["nome"].split()[:2])
    nivel_map = {"admin": "Admin", "almoxarife": "Almoxarife", "usuario": "Usuário"}
    nivel_label = nivel_map.get(usuario["nivel"], usuario["nivel"])

    st.markdown(f"""
    <div class="sfc-topbar">
        <div class="sfc-topbar-brand">SFC <span>ALMOXARIFADO</span></div>
        <nav class="sfc-nav">{nav_html}</nav>
        <div class="sfc-user-chip">
            <div class="avatar">{iniciais}</div>
            <div>
                <div style="color:#e8eaf0;font-weight:500;font-size:0.8rem;">{usuario["nome"].split()[0]}</div>
                <div style="font-size:0.68rem;color:#3d8ef0;">{nivel_label}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def badge(texto: str, tipo: str) -> str:
    return f'<span class="badge badge-{tipo}">{texto}</span>'


def status_estoque_badge(estoque_atual: float, estoque_minimo: float) -> str:
    if estoque_atual <= 0:
        return badge("Crítico", "critico")
    if estoque_atual <= estoque_minimo:
        return badge("Baixo", "baixo")
    return badge("OK", "ok")


def metric_card(label: str, valor, sub: str = "", accent: str = "#3d8ef0") -> str:
    return f"""
    <div class="sfc-metric" style="--accent:{accent};">
        <div class="sfc-metric-label">{label}</div>
        <div class="sfc-metric-value">{valor}</div>
        {"<div class='sfc-metric-sub'>" + sub + "</div>" if sub else ""}
    </div>"""


def navegar(pagina: str):
    st.session_state["pagina"] = pagina
    st.rerun()


def pagina_atual() -> str:
    params = st.query_params
    if "page" in params:
        pg = params["page"]
        st.session_state["pagina"] = pg
        st.query_params.clear()
    return st.session_state.get("pagina", "home")
