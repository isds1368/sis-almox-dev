"""
utils/auth.py — Autenticação com bcrypt
"""
import bcrypt
import streamlit as st
from utils.database import buscar_usuario_por_email, contar_usuarios


def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, hash_str: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), hash_str.encode())
    except Exception:
        return False


def fazer_login(email: str, senha: str) -> dict | None:
    usuario = buscar_usuario_por_email(email)
    if not usuario:
        return None
    if not usuario.get("ativo"):
        return None
    if not verificar_senha(senha, usuario["senha_hash"]):
        return None
    return usuario


def sessao_usuario() -> dict | None:
    return st.session_state.get("usuario")


def exigir_login():
    if not sessao_usuario():
        st.stop()


def exigir_nivel(*niveis):
    u = sessao_usuario()
    if not u or u["nivel"] not in niveis:
        st.error("🔒 Acesso não autorizado.")
        st.stop()


def is_admin() -> bool:
    u = sessao_usuario()
    return u is not None and u["nivel"] == "admin"


def is_almoxarife() -> bool:
    u = sessao_usuario()
    return u is not None and u["nivel"] in ("admin", "almoxarife")


def primeiro_acesso() -> bool:
    return contar_usuarios() == 0
