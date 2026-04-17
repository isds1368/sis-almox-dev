"""
app.py — SFC Almoxarifado — Entrypoint principal
"""
import streamlit as st

st.set_page_config(
    page_title="SFC Almoxarifado",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

    # ── SEM LOGIN: primeiro acesso ───────────────────────────────
    if not usuario and primeiro_acesso():
        tela_primeiro_acesso()
        return

    # ── SEM LOGIN: tela home ou login ────────────────────────────
    if not usuario:
        if pagina == "home":
            tela_home()
        else:
            tela_login()
        return

    # ── COM LOGIN: forçar primeiro acesso explícito ──────────────
    if pagina == "primeiro_acesso":
        tela_primeiro_acesso()
        return

    # ── TOPBAR com navegação ─────────────────────────────────────
    topbar(pagina, usuario)

    # ── ROTEAMENTO PRINCIPAL ─────────────────────────────────────
    rotas = {
        "home":      tela_dashboard,   # home logado → dashboard
        "dashboard": tela_dashboard,
        "entrada":   tela_entrada,
        "saida":     tela_saida,
        "estoque":   tela_estoque,
        "notas":     tela_notas,
        "usuarios":  tela_usuarios,
    }

    rotas.get(pagina, tela_dashboard)()


if __name__ == "__main__":
    main()
