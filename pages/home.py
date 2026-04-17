"""
pages/home.py — Tela inicial + Login + Primeiro Acesso
"""
import streamlit as st
from utils.auth import hash_senha, fazer_login, primeiro_acesso, sessao_usuario
from utils.database import criar_usuario, buscar_usuario_por_email
from utils.ui import navegar


# CSS extra para centralizar telas de auth sem scroll
_AUTH_CSS = """
<style>
/* Remove padding padrão do Streamlit nas telas de auth */
.auth-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    padding: 1rem;
}
/* Evita que o Streamlit empurre conteúdo para baixo */
[data-testid="stAppViewContainer"] > section > div:first-child {
    padding-top: 0 !important;
}
[data-testid="block-container"] {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
}
</style>
"""


def tela_home():
    """Tela de boas-vindas antes do login."""
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)

    # Espaço para centralizar verticalmente
    st.markdown("<div style='height:30vh'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;margin-bottom:1.5rem;">
            <div class="sfc-home-logo">SFC <span>·</span> ALM</div>
            <div class="sfc-home-sub">SISTEMA DE CONTROLE DE ALMOXARIFADO</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("ENTRAR →", type="primary", use_container_width=True):
            if primeiro_acesso():
                navegar("primeiro_acesso")
            else:
                navegar("login")


def tela_primeiro_acesso():
    """Cadastro do primeiro administrador."""
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:1.5rem 0 1rem;">
            <div style="font-size:2.2rem;margin-bottom:0.4rem;">🔑</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:700;color:#e8eaf0;">
                Primeiro Acesso
            </div>
            <div style="font-size:0.82rem;color:#5c647a;margin-top:0.3rem;">
                Bem-vindo ao SFC Almoxarifado.<br>Configure o administrador do sistema.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_primeiro_acesso", clear_on_submit=False):
            nome   = st.text_input("Nome completo *", placeholder="João Silva")
            email  = st.text_input("E-mail *", placeholder="joao@empresa.com.br")
            senha  = st.text_input("Senha *", type="password", placeholder="Mínimo 6 caracteres")
            senha2 = st.text_input("Confirmar senha *", type="password")

            submitted = st.form_submit_button(
                "Criar Administrador →", type="primary", use_container_width=True
            )

            if submitted:
                erros = []
                if not nome.strip():
                    erros.append("Nome é obrigatório.")
                if not email.strip() or "@" not in email:
                    erros.append("E-mail inválido.")
                if len(senha) < 6:
                    erros.append("Senha mínima de 6 caracteres.")
                if senha != senha2:
                    erros.append("As senhas não coincidem.")
                # Só valida e-mail duplicado se não houve outros erros
                if not erros and buscar_usuario_por_email(email.strip().lower()):
                    erros.append("E-mail já cadastrado.")

                if erros:
                    for e in erros:
                        st.error(e)
                else:
                    criar_usuario(
                        nome=nome.strip(),
                        email=email.strip().lower(),
                        senha_hash=hash_senha(senha),
                        nivel="admin"
                    )
                    st.success("✅ Administrador criado! Redirecionando para o login...")
                    navegar("login")


def tela_login():
    """Tela de login."""
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:1.5rem 0 1.5rem;">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#3d8ef0;">
                SFC <span style="color:#e8eaf0">·</span> ALM
            </div>
            <div style="font-size:0.78rem;color:#5c647a;margin-top:0.3rem;letter-spacing:0.08em;">
                ACESSO AO SISTEMA
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("form_login"):
            email = st.text_input("E-mail", placeholder="seu@email.com.br")
            senha = st.text_input("Senha", type="password", placeholder="••••••••")
            submitted = st.form_submit_button(
                "Entrar →", type="primary", use_container_width=True
            )

            if submitted:
                if not email or not senha:
                    st.error("Preencha e-mail e senha.")
                else:
                    usuario = fazer_login(email.strip().lower(), senha)
                    if usuario:
                        st.session_state["usuario"] = usuario
                        st.success(f"Bem-vindo, {usuario['nome'].split()[0]}!")
                        navegar("dashboard")
                    else:
                        st.error("E-mail ou senha incorretos, ou usuário inativo.")

        st.markdown("""
        <div style="text-align:center;margin-top:1rem;">
            <span style="font-size:0.75rem;color:#5c647a;">
                SFC Almoxarifado &copy; 2025
            </span>
        </div>
        """, unsafe_allow_html=True)
