"""
pages/notas.py — Notas Fiscais e envio ao financeiro
"""
import datetime
import urllib.parse
import streamlit as st
from utils.database import listar_notas_fiscais, atualizar_nota_fiscal
from utils.auth import sessao_usuario
from utils.ui import badge


# Texto padrão do e-mail ao financeiro
EMAIL_TEMPLATE = """Olá,

Segue em anexo a(s) nota(s) fiscal(is) para processamento:

{notas}

Atenciosamente,
{remetente}
SFC — Almoxarifado
"""


def tela_notas():
    st.markdown('<div class="sfc-page">', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-title">📎 Notas Fiscais</div>', unsafe_allow_html=True)
    st.markdown('<div class="sfc-page-sub">Gerencie e envie documentos fiscais ao financeiro</div>', unsafe_allow_html=True)

    notas = listar_notas_fiscais()

    if not notas:
        st.info("Nenhuma nota fiscal registrada. Elas aparecem automaticamente ao registrar uma entrada com NF.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    usuario = sessao_usuario()

    pendentes = [n for n in notas if n["status_envio"] == "pendente"]
    enviadas  = [n for n in notas if n["status_envio"] == "enviado"]

    # ── MÉTRICAS ──────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sfc-metrics">
        <div class="sfc-metric" style="--accent:#3d8ef0;">
            <div class="sfc-metric-label">Total de Notas</div>
            <div class="sfc-metric-value">{len(notas)}</div>
        </div>
        <div class="sfc-metric" style="--accent:#a78bfa;">
            <div class="sfc-metric-label">Pendentes de Envio</div>
            <div class="sfc-metric-value">{len(pendentes)}</div>
            <div class="sfc-metric-sub">Aguardando envio ao financeiro</div>
        </div>
        <div class="sfc-metric" style="--accent:#34d399;">
            <div class="sfc-metric-label">Enviadas</div>
            <div class="sfc-metric-value">{len(enviadas)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs([f"Pendentes ({len(pendentes)})", f"Enviadas ({len(enviadas)})"])

    with tab1:
        _lista_notas(pendentes, usuario, pendente=True)

    with tab2:
        _lista_notas(enviadas, usuario, pendente=False)

    # ── CONFIGURAÇÃO DO TEMPLATE DE E-MAIL ────────────────────────
    with st.expander("⚙️ Configurar Template de E-mail"):
        st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
        destinatario = st.text_input(
            "E-mail do financeiro",
            value=st.session_state.get("email_financeiro", "financeiro@empresa.com.br"),
            key="email_financeiro_input"
        )
        if st.button("Salvar e-mail"):
            st.session_state["email_financeiro"] = destinatario
            st.success("E-mail salvo na sessão.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _lista_notas(notas: list, usuario: dict, pendente: bool):
    if not notas:
        st.markdown('<p style="color:#5c647a;font-size:0.85rem;padding:1rem 0;">Nenhuma nota aqui.</p>', unsafe_allow_html=True)
        return

    for n in notas:
        criado_por = (n.get("criado_por_usuario") or {}).get("nome", "—")
        data = n["criado_em"][:16].replace("T", " ")
        status_b = badge("Pendente", "pendente") if n["status_envio"] == "pendente" else badge("Enviado", "enviado")

        st.markdown('<div class="sfc-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([4, 3, 3])

        with col1:
            st.markdown(f"**NF {n['numero']}** — {n['fornecedor']}")
            st.caption(f"Registrada em {data} por {criado_por}")
            if n.get("valor_total"):
                st.caption(f"Valor: R$ {float(n['valor_total']):,.2f}")
            st.markdown(status_b, unsafe_allow_html=True)

        with col2:
            # Visualizar PDF
            if n.get("arquivo_url"):
                st.link_button("📄 Visualizar PDF", n["arquivo_url"])
            else:
                st.caption("📄 Sem arquivo anexo")

        with col3:
            if pendente:
                # Botão abrir Outlook
                _botao_outlook(n, usuario)
                if st.button("✅ Marcar como Enviado", key=f"sent_{n['id']}"):
                    atualizar_nota_fiscal(n["id"], {
                        "status_envio": "enviado",
                        "enviado_por": usuario["id"],
                        "enviado_em": datetime.datetime.utcnow().isoformat(),
                    })
                    st.success("Nota marcada como enviada!")
                    st.rerun()
            else:
                if n.get("enviado_em"):
                    st.caption(f"Enviado em: {n['enviado_em'][:16].replace('T', ' ')}")

        st.markdown("</div>", unsafe_allow_html=True)


def _botao_outlook(nota: dict, usuario: dict):
    """Gera link mailto para abrir o Outlook com dados da nota."""
    destinatario = st.session_state.get("email_financeiro", "financeiro@empresa.com.br")
    assunto = f"Nota Fiscal {nota['numero']} — {nota['fornecedor']}"

    corpo_notas = f"NF {nota['numero']} | {nota['fornecedor']}"
    if nota.get("valor_total"):
        corpo_notas += f" | R$ {float(nota['valor_total']):,.2f}"

    corpo = EMAIL_TEMPLATE.format(
        notas=corpo_notas,
        remetente=usuario["nome"]
    )

    mailto = (
        f"mailto:{destinatario}"
        f"?subject={urllib.parse.quote(assunto)}"
        f"&body={urllib.parse.quote(corpo)}"
    )

    st.link_button("📧 Enviar via Outlook", mailto)
