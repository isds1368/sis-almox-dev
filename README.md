# 📦 SFC Almoxarifado

Sistema de Controle de Almoxarifado — desenvolvido com **Streamlit + Supabase**.

---

## 🚀 Estrutura do Projeto

```
sfc_almoxarifado/
├── app.py                          # Entrypoint principal
├── requirements.txt                # Dependências Python
├── schema.sql                      # Schema completo do banco de dados
├── .env.example                    # Variáveis de ambiente
├── .streamlit/
│   ├── config.toml                 # Tema visual e configurações
│   └── secrets.toml.example        # Secrets para Streamlit Cloud
├── pages/
│   ├── home.py                     # Home + Login + Primeiro Acesso
│   ├── entrada.py                  # Entrada de produtos
│   ├── saida.py                    # Saída com fluxo de autorização
│   ├── estoque.py                  # Inventário + Ajuste manual
│   ├── notas.py                    # Notas fiscais + Envio Outlook
│   ├── dashboard.py                # Dashboard com gráficos Plotly
│   └── usuarios.py                 # Gestão de usuários
└── utils/
    ├── auth.py                     # bcrypt + controle de sessão
    ├── database.py                 # Todas as operações Supabase
    └── ui.py                       # CSS global + componentes visuais
```

---

## ⚙️ Configuração

### 1. Clone e instale dependências

```bash
git clone <repo>
cd sfc_almoxarifado
pip install -r requirements.txt
```

### 2. Configure o Supabase

1. Crie um projeto em [supabase.com](https://supabase.com)
2. Acesse **SQL Editor** e execute todo o conteúdo de `schema.sql`
3. Acesse **Storage** e crie um bucket chamado `notas-fiscais` (privado)

### 3. Configure as variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas credenciais do Supabase
```

**Para uso local:**
```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...  # service_role key (não a anon key!)
```

**Para Streamlit Cloud:**
```toml
# .streamlit/secrets.toml
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGci..."
```

### 4. Execute

```bash
streamlit run app.py
```

---

## 🔐 Primeiro Acesso

1. Abra o sistema no navegador
2. Clique em **ENTRAR**
3. O sistema detecta que não há usuários e abre a tela de **Primeiro Acesso**
4. Cadastre o primeiro administrador
5. Faça login

---

## 👥 Níveis de Acesso

| Nível       | Permissões |
|-------------|------------|
| Admin       | Acesso total: entrada, saída (autorização + execução), estoque (ajuste), notas, dashboard, usuários |
| Almoxarife  | Entrada, saída (executar baixa), estoque (visualizar), notas, dashboard |
| Usuário     | Solicitar saída, visualizar estoque e dashboard |

---

## 📋 Funcionalidades

- **Entrada:** Leitura de EAN, cadastro automático de produto, upload de PDF, vinculação de NF
- **Saída:** Fluxo em 3 etapas (solicitação → autorização → execução), bloqueio de estoque negativo
- **Estoque:** Tabela com filtros, status automático (OK/Baixo/Crítico), ajuste manual auditado
- **Notas Fiscais:** Listagem, visualização de PDF, envio via Outlook (mailto), marcação de enviado
- **Dashboard:** KPIs, gráficos Plotly (consumo por setor, status inventário), alertas críticos
- **Usuários:** CRUD completo, controle de nível e ativo/inativo

---

## 🗄️ Banco de Dados

As tabelas são criadas automaticamente pelo `schema.sql`:

- `usuarios` — Autenticação própria com bcrypt
- `produtos` — Cadastro com código interno automático (SFC-00001)
- `categorias` — 9 categorias padrão inseridas automaticamente
- `entradas` — Trigger atualiza `estoque_atual` automaticamente
- `saidas` — Trigger atualiza estoque ao executar baixa
- `notas_fiscais` — PDFs no Storage do Supabase
- `ajustes_estoque` — Auditoria completa de ajustes manuais

---

## 🔒 Segurança

- Senhas com **bcrypt** (nunca armazenadas em texto puro)
- **RLS habilitado** em todas as tabelas (acesso via service_role no backend)
- Sessão por `st.session_state` (sem JWT exposto no frontend)
- Validação de nível em todas as rotas sensíveis

---

## 📦 Deploy no Streamlit Cloud

1. Suba o projeto para um repositório GitHub (privado recomendado)
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositório e aponte para `app.py`
4. Configure os secrets em **Settings → Secrets**:
   ```toml
   SUPABASE_URL = "..."
   SUPABASE_SERVICE_KEY = "..."
   ```

---

*SFC Almoxarifado — versão 1.0*
