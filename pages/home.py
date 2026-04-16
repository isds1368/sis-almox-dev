"""
pages/home.py — Tela inicial + Login + Primeiro Acesso
"""
import streamlit as st
from utils.auth import hash_senha, fazer_login, primeiro_acesso, sessao_usuario
from utils.database import criar_usuario, buscar_usuario_por_email
from utils.ui import navegar


def tela_home():
    """Tela de boas-vindas antes do login."""
    st.markdown("""
    <div class="sfc-home">
        <div class="sfc-home-logo">SFC <span>·</span> ALM</div>
        <div class="sfc-home-sub">SISTEMA DE CONTROLE DE ALMOXARIFADO</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 0.6, 1])
    with col2:
        if st.button("ENTRAR →", type="primary", use_container_width=True):
            if primeiro_acesso():
                navegar("primeiro_acesso")
            else:
                navegar("login")


def tela_primeiro_acesso():
    """Cadastro do primeiro administrador."""
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;min-height:calc(100vh - 60px);padding:2rem;">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sfc-form-card">
        <div style="text-align:center;margin-bottom:1.5rem;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">🔑</div>
            <div class="sfc-form-title">Primeiro Acesso</div>
            <div class="sfc-form-sub">Bem-vindo ao SFC Almoxarifado.<br>Configure o administrador do sistema.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        col1, col2, col3 = st.columns([1, 1.4, 1])
        with col2:
            with st.form("form_primeiro_acesso", clear_on_submit=False):
                st.markdown("**Dados do Administrador**")
                nome   = st.text_input("Nome completo", placeholder="João Silva")
                email  = st.text_input("E-mail", placeholder="joao@empresa.com.br")
                senha  = st.text_input("Senha", type="password", placeholder="Mínimo 6 caracteres")
                senha2 = st.text_input("Confirmar senha", type="password")

                submitted = st.form_submit_button("Criar Administrador", type="primary", use_container_width=True)

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
                    if buscar_usuario_por_email(email):
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
                        st.success("✅ Administrador criado com sucesso!")
                        st.info("Agora faça login com suas credenciais.")
                        navegar("login")

    st.markdown("</div>", unsafe_allow_html=True)


def tela_login():
    """Tela de login."""
    with st.container():
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style="text-align:center;margin-bottom:2rem;">
                <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:#3d8ef0;">
                    SFC <span style="color:#e8eaf0">·</span> ALM
                </div>
                <div style="font-size:0.8rem;color:#5c647a;margin-top:0.3rem;letter-spacing:0.08em;">
                    ACESSO AO SISTEMA
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("form_login"):
                email = st.text_input("E-mail", placeholder="seu@email.com.br")
                senha = st.text_input("Senha", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Entrar →", type="primary", use_container_width=True)

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
