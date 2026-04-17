"""
utils/database.py — Conexão e helpers Supabase
"""
import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource(show_spinner=False)
def get_supabase() -> Client:
    """Retorna cliente Supabase singleton (service role para operações backend)."""
    url = os.getenv("SUPABASE_URL", st.secrets.get("SUPABASE_URL", ""))
    key = os.getenv("SUPABASE_SERVICE_KEY", st.secrets.get("SUPABASE_SERVICE_KEY", ""))
    if not url or not key:
        st.error("⚠️ Variáveis SUPABASE_URL e SUPABASE_SERVICE_KEY não configuradas.")
        st.stop()
    return create_client(url, key)


# ─── USUÁRIOS ──────────────────────────────────────────────────────────────

def contar_usuarios() -> int:
    sb = get_supabase()
    res = sb.table("usuarios").select("id", count="exact").execute()
    return res.count or 0


def buscar_usuario_por_email(email: str) -> dict | None:
    sb = get_supabase()
    try:
        res = sb.table("usuarios").select("*").eq("email", email).maybe_single().execute()
        return res.data
    except Exception:
        return None


def criar_usuario(nome: str, email: str, senha_hash: str, nivel: str = "admin") -> dict:
    sb = get_supabase()
    res = sb.table("usuarios").insert({
        "nome": nome, "email": email,
        "senha_hash": senha_hash, "nivel": nivel
    }).execute()
    return res.data[0]


def listar_usuarios() -> list:
    sb = get_supabase()
    res = sb.table("usuarios").select("*").order("nome").execute()
    return res.data or []


def atualizar_usuario(uid: str, dados: dict) -> dict:
    sb = get_supabase()
    res = sb.table("usuarios").update(dados).eq("id", uid).execute()
    return res.data[0]


# ─── PRODUTOS ──────────────────────────────────────────────────────────────

def listar_produtos(apenas_ativos: bool = True) -> list:
    sb = get_supabase()
    q = sb.table("produtos").select("*, categorias(nome)").order("nome")
    if apenas_ativos:
        q = q.eq("ativo", True)
    return q.execute().data or []


def buscar_produto_por_ean(ean: str) -> dict | None:
    sb = get_supabase()
    try:
        res = sb.table("produtos").select("*, categorias(nome)").eq("ean", ean).maybe_single().execute()
        return res.data
    except Exception:
        return None


def buscar_produto_por_id(pid: str) -> dict | None:
    sb = get_supabase()
    try:
        res = sb.table("produtos").select("*, categorias(nome)").eq("id", pid).maybe_single().execute()
        return res.data
    except Exception:
        return None


def criar_produto(dados: dict) -> dict:
    sb = get_supabase()
    res = sb.table("produtos").insert(dados).execute()
    return res.data[0]


def atualizar_produto(pid: str, dados: dict) -> dict:
    sb = get_supabase()
    res = sb.table("produtos").update(dados).eq("id", pid).execute()
    return res.data[0]


# ─── CATEGORIAS ────────────────────────────────────────────────────────────

def listar_categorias() -> list:
    sb = get_supabase()
    res = sb.table("categorias").select("*").order("nome").execute()
    return res.data or []


# ─── ENTRADAS ──────────────────────────────────────────────────────────────

def registrar_entrada(dados: dict) -> dict:
    sb = get_supabase()
    res = sb.table("entradas").insert(dados).execute()
    return res.data[0]


def listar_entradas(limite: int = 100) -> list:
    sb = get_supabase()
    res = (sb.table("entradas")
           .select("*, produtos(nome, codigo_interno), notas_fiscais(numero, fornecedor), usuarios!entradas_registrado_por_fkey(nome)")
           .order("criado_em", desc=True)
           .limit(limite)
           .execute())
    return res.data or []


# ─── SAÍDAS ────────────────────────────────────────────────────────────────

def registrar_saida(dados: dict) -> dict:
    sb = get_supabase()
    res = sb.table("saidas").insert(dados).execute()
    return res.data[0]


def listar_saidas(status: str | None = None, limite: int = 100) -> list:
    sb = get_supabase()
    q = (sb.table("saidas")
         .select("""
             *,
             produtos(nome, codigo_interno, estoque_atual, unidade),
             solicitado:usuarios!saidas_solicitado_por_fkey(nome),
             autorizado:usuarios!saidas_autorizado_por_fkey(nome),
             executado:usuarios!saidas_executado_por_fkey(nome)
         """)
         .order("criado_em", desc=True)
         .limit(limite))
    if status:
        q = q.eq("status", status)
    return q.execute().data or []


def atualizar_saida(sid: str, dados: dict) -> dict:
    sb = get_supabase()
    res = sb.table("saidas").update(dados).eq("id", sid).execute()
    return res.data[0]


# ─── NOTAS FISCAIS ─────────────────────────────────────────────────────────

def criar_nota_fiscal(dados: dict) -> dict:
    sb = get_supabase()
    res = sb.table("notas_fiscais").insert(dados).execute()
    return res.data[0]


def listar_notas_fiscais() -> list:
    sb = get_supabase()
    res = (sb.table("notas_fiscais")
           .select("*, criado_por_usuario:usuarios!notas_fiscais_criado_por_fkey(nome)")
           .order("criado_em", desc=True)
           .execute())
    return res.data or []


def atualizar_nota_fiscal(nid: str, dados: dict) -> dict:
    sb = get_supabase()
    res = sb.table("notas_fiscais").update(dados).eq("id", nid).execute()
    return res.data[0]


def upload_nota_pdf(arquivo_bytes: bytes, nome_arquivo: str) -> str | None:
    """Faz upload do PDF no bucket 'notas-fiscais' e retorna URL pública."""
    sb = get_supabase()
    try:
        path = f"notas/{nome_arquivo}"
        sb.storage.from_("notas-fiscais").upload(
            path, arquivo_bytes,
            file_options={"content-type": "application/pdf", "upsert": "true"}
        )
        url = sb.storage.from_("notas-fiscais").create_signed_url(path, 60 * 60 * 24 * 365)
        return url.get("signedURL")
    except Exception as e:
        st.warning(f"Upload do PDF falhou: {e}")
        return None


# ─── AJUSTES ───────────────────────────────────────────────────────────────

def registrar_ajuste(dados: dict) -> dict:
    sb = get_supabase()
    res = sb.table("ajustes_estoque").insert(dados).execute()
    return res.data[0]


def listar_ajustes(limite: int = 50) -> list:
    sb = get_supabase()
    res = (sb.table("ajustes_estoque")
           .select("*, produtos(nome), usuarios!ajustes_estoque_ajustado_por_fkey(nome)")
           .order("criado_em", desc=True)
           .limit(limite)
           .execute())
    return res.data or []


# ─── DASHBOARD ─────────────────────────────────────────────────────────────

def stats_dashboard() -> dict:
    sb = get_supabase()

    produtos = sb.table("produtos").select("estoque_atual, estoque_minimo, ativo").eq("ativo", True).execute().data or []
    total_produtos = len(produtos)
    criticos  = sum(1 for p in produtos if p["estoque_atual"] <= 0)
    baixos    = sum(1 for p in produtos if 0 < p["estoque_atual"] <= p["estoque_minimo"])
    parados   = sum(1 for p in produtos if p["estoque_atual"] > 0)

    entradas_count = sb.table("entradas").select("id", count="exact").execute().count or 0
    saidas_count   = sb.table("saidas").select("id", count="exact").execute().count or 0

    saidas_setor = (sb.table("saidas")
                    .select("setor_solicitante, quantidade")
                    .eq("status", "executado")
                    .execute().data or [])

    consumo: dict[str, float] = {}
    for s in saidas_setor:
        consumo[s["setor_solicitante"]] = consumo.get(s["setor_solicitante"], 0) + float(s["quantidade"])

    recentes_entradas = (sb.table("entradas")
                         .select("criado_em, produtos(nome), quantidade, unidade")
                         .order("criado_em", desc=True).limit(5).execute().data or [])

    recentes_saidas = (sb.table("saidas")
                       .select("criado_em, produtos(nome), quantidade, unidade, setor_solicitante, status")
                       .order("criado_em", desc=True).limit(5).execute().data or [])

    pendentes_saida  = sb.table("saidas").select("id", count="exact").eq("status", "pendente").execute().count or 0
    pendentes_notas  = sb.table("notas_fiscais").select("id", count="exact").eq("status_envio", "pendente").execute().count or 0

    return {
        "total_produtos": total_produtos,
        "criticos": criticos,
        "baixos": baixos,
        "parados": parados,
        "entradas_count": entradas_count,
        "saidas_count": saidas_count,
        "consumo_setor": consumo,
        "recentes_entradas": recentes_entradas,
        "recentes_saidas": recentes_saidas,
        "pendentes_saida": pendentes_saida,
        "pendentes_notas": pendentes_notas,
    }
