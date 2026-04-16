"""
app.py — SFC Almoxarifado — Entrypoint principal
"""
import streamlit as st

# ── CONFIGURAÇÃO DA PÁGINA (DEVE SER PRIMEIRO) ─────────────────────────────
st.set_page_config(
    page_title="SFC Almoxarifado",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── IMPORTS INTERNOS ────────────────────────────────────────────────────────
from utils.ui import inject_css, topbar, pagina_atual
from utils.auth import sessao_usuario, primeiro_acesso

from pages.home      import tela_home, tela_login, tela_primeiro_acesso
from pages.entrada   import tela_entrada
from pages.saida     import tela_saida
from pages.estoque   import tela_estoque
from pages.notas     import tela_notas
from pages.dashboard import tela_dashboard
from pages.usuarios  import tela_usuarios


def main():
    inject_css()

    usuario = sessao_usuario()
    pagina  = pagina_atual()

    # ── ROTAS SEM LOGIN ──────────────────────────────────────────────────────
    if pagina == "primeiro_acesso" or (not usuario and primeiro_acesso()):
        tela_primeiro_acesso()
        return

    if pagina == "login" or not usuario:
        if pagina == "home" and not usuario:
            tela_home()
        else:
            tela_login()
        return

    # ── ROTA HOME (sem login ainda) ───────────────────────────────────────────
    if pagina == "home":
        tela_home()
        return

    # ── TOPBAR (apenas quando logado e não na home) ───────────────────────────
    topbar(pagina, usuario)

    # ── ROTEAMENTO PRINCIPAL ──────────────────────────────────────────────────
    rotas = {
        "dashboard": tela_dashboard,
        "entrada":   tela_entrada,
        "saida":     tela_saida,
        "estoque":   tela_estoque,
        "notas":     tela_notas,
        "usuarios":  tela_usuarios,
    }

    if pagina in rotas:
        rotas[pagina]()
    else:
        # Padrão: dashboard
        tela_dashboard()

    # ── BOTÃO DE LOGOUT (canto inferior) ────────────────────────────────────
    st.markdown("<div style='height:3rem'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.3, 1])
    with col2:
        if st.button("Sair", help="Encerrar sessão"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


if __name__ == "__main__":
    main()
