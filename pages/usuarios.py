"""
pages/usuarios.py — Gestão de usuários (apenas Admin)
"""
import streamlit as st
from utils.database import listar_usuarios, criar_usuario, atualizar_usuario, buscar_usuario_por_email
from utils.auth import hash_senha, sessao_usuario, exigir_nivel
from utils.ui import badge

NIVEIS = ["admin", "almoxarife", "usuario"]
NIVEL_LABELS = {"admin": "Administrador", "almoxarife": "Almoxarife", "usuario": "Usuário"}


def tela_usuarios():
    exigir_nivel("admin")

    st.markdown('<div class="sfc-page">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-title">👥 Gestão de Usuários</div>', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-sub">Cadastre, edite e gerencie acessos ao sistema</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Usuários Cadastrados", "Novo Usuário"])

    with tab1:
        _listar_usuarios()
    with tab2:
        _cadastrar_usuario()

    st.markdown("</div>", unsafe_allow_html=True)


def _listar_usuarios():
    usuario_logado = sessao_usuario()
    usuarios = listar_usuarios()

    if not usuarios:
        st.info("Nenhum usuário cadastrado.")
        return

    st.markdown(f"""
    <div class="sfc-metrics">
        <div class="sfc-metric" style="--accent:#3d8ef0;">
            <div class="sfc-metric-label">Total</div>
            <div class="sfc-metric-value">{len(usuarios)}</div>
        </div>
        <div class="sfc-metric" style="--accent:#34d399;">
            <div class="sfc-metric-label">Ativos</div>
            <div class="sfc-metric-value">{sum(1 for u in usuarios if u['ativo'])}</div>
        </div>
        <div class="sfc-metric" style="--accent:#f87171;">
            <div class="sfc-metric-label">Inativos</div>
            <div class="sfc-metric-value">{sum(1 for u in usuarios if not u['ativo'])}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">Lista de Usuários</div>', unsafe_allow_html=True)

    nivel_cores = {
        "admin":      "#f87171",
        "almoxarife": "#fbbf24",
        "usuario":    "#60d0f0",
    }

    rows = ""
    for u in usuarios:
        ativo_b = badge("Ativo", "ok") if u["ativo"] else badge("Inativo", "critico")
        nivel_cor = nivel_cores.get(u["nivel"], "#8891a8")
        criado = u["criado_em"][:10]
        rows += f"""
        <tr>
            <td><strong>{u['nome']}</strong></td>
            <td style="color:#5c647a;">{u['email']}</td>
            <td><span style="color:{nivel_cor};font-weight:600;font-size:0.8rem;">{NIVEL_LABELS.get(u['nivel'], u['nivel'])}</span></td>
            <td>{ativo_b}</td>
            <td style="color:#5c647a;">{criado}</td>
        </tr>"""

    st.markdown(f"""
    <table class="sfc-table">
        <thead>
            <tr><th>Nome</th><th>E-mail</th><th>Nível</th><th>Status</th><th>Cadastrado</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── EDIÇÃO ────────────────────────────────────────────────────
    with st.expander("✏️ Editar usuário"):
        outros = [u for u in usuarios if u["id"] != usuario_logado["id"]]
        if not outros:
            st.info("Você é o único usuário.")
        else:
            u_map = {f"{u['nome']} ({u['email']})": u for u in outros}
            sel   = st.selectbox("Selecione o usuário", list(u_map.keys()), key="sel_edit_user")
            u_sel = u_map[sel]

            with st.form("form_edit_user"):
                col1, col2 = st.columns(2)
                with col1:
                    nome_e  = st.text_input("Nome", value=u_sel["nome"])
                    email_e = st.text_input("E-mail", value=u_sel["email"])
                with col2:
                    nivel_e = st.selectbox("Nível", NIVEIS,
                                           index=NIVEIS.index(u_sel["nivel"]) if u_sel["nivel"] in NIVEIS else 2)
                    ativo_e = st.checkbox("Ativo", value=u_sel["ativo"])
                nova_senha = st.text_input("Nova senha (deixe em branco para manter)", type="password")

                if st.form_submit_button("Salvar alterações →", type="primary"):
                    dados = {
                        "nome": nome_e.strip(),
                        "email": email_e.strip().lower(),
                        "nivel": nivel_e,
                        "ativo": ativo_e,
                    }
                    if nova_senha.strip():
                        if len(nova_senha) < 6:
                            st.error("Senha mínima de 6 caracteres.")
                            st.stop()
                        dados["senha_hash"] = hash_senha(nova_senha)

                    atualizar_usuario(u_sel["id"], dados)
                    st.success(f"✅ Usuário **{nome_e}** atualizado.")
                    st.rerun()


def _cadastrar_usuario():
    st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-card-header">➕ Cadastrar Novo Usuário</div>', unsafe_allow_html=True)

    with st.form("form_novo_user"):
        col1, col2 = st.columns(2)
        with col1:
            nome   = st.text_input("Nome completo *")
            email  = st.text_input("E-mail *")
        with col2:
            nivel  = st.selectbox("Nível de acesso", NIVEIS, format_func=lambda x: NIVEL_LABELS[x])
            senha  = st.text_input("Senha *", type="password")
            senha2 = st.text_input("Confirmar senha *", type="password")

        submitted = st.form_submit_button("Criar Usuário →", type="primary", use_container_width=True)

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
            if buscar_usuario_por_email(email.strip().lower()):
                erros.append("E-mail já cadastrado.")

            if erros:
                for e in erros:
                    st.error(e)
            else:
                criar_usuario(
                    nome=nome.strip(),
                    email=email.strip().lower(),
                    senha_hash=hash_senha(senha),
                    nivel=nivel,
                )
                st.success(f"✅ Usuário **{nome}** criado com nível **{NIVEL_LABELS[nivel]}**.")
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
