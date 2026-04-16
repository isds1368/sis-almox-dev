-- =============================================
-- SFC ALMOXARIFADO — SCHEMA SUPABASE
-- Execute este script no SQL Editor do Supabase
-- =============================================

-- ─── EXTENSÕES ──────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── TABELA: USUÁRIOS ────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    senha_hash  TEXT NOT NULL,
    nivel       TEXT NOT NULL DEFAULT 'usuario'
                  CHECK (nivel IN ('admin','almoxarife','usuario')),
    ativo       BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── TABELA: CATEGORIAS ──────────────────────
CREATE TABLE IF NOT EXISTS categorias (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome      TEXT UNIQUE NOT NULL,
    descricao TEXT
);

-- ─── TABELA: PRODUTOS ────────────────────────
CREATE TABLE IF NOT EXISTS produtos (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo_interno   TEXT UNIQUE NOT NULL,
    nome             TEXT NOT NULL,
    ean              TEXT UNIQUE,
    categoria_id     UUID REFERENCES categorias(id) ON DELETE SET NULL,
    unidade          TEXT NOT NULL DEFAULT 'UN'
                       CHECK (unidade IN ('UN','CX','KG','LT','MT','PC','RL','FR','GL','DZ','CT')),
    fator_conversao  NUMERIC(10,4) NOT NULL DEFAULT 1,
    estoque_atual    NUMERIC(10,4) NOT NULL DEFAULT 0,
    estoque_minimo   NUMERIC(10,4) NOT NULL DEFAULT 0,
    descricao        TEXT,
    ativo            BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── TABELA: NOTAS FISCAIS ───────────────────
CREATE TABLE IF NOT EXISTS notas_fiscais (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero          TEXT NOT NULL,
    fornecedor      TEXT NOT NULL,
    valor_total     NUMERIC(12,2),
    arquivo_nome    TEXT,
    arquivo_url     TEXT,
    status_envio    TEXT NOT NULL DEFAULT 'pendente'
                      CHECK (status_envio IN ('pendente','enviado')),
    enviado_por     UUID REFERENCES usuarios(id),
    enviado_em      TIMESTAMPTZ,
    criado_por      UUID REFERENCES usuarios(id),
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── TABELA: ENTRADAS ────────────────────────
CREATE TABLE IF NOT EXISTS entradas (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produto_id      UUID NOT NULL REFERENCES produtos(id),
    nota_fiscal_id  UUID REFERENCES notas_fiscais(id) ON DELETE SET NULL,
    quantidade      NUMERIC(10,4) NOT NULL,
    unidade         TEXT NOT NULL,
    quantidade_base NUMERIC(10,4) NOT NULL,
    observacao      TEXT,
    registrado_por  UUID NOT NULL REFERENCES usuarios(id),
    criado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── TABELA: SAÍDAS ──────────────────────────
CREATE TABLE IF NOT EXISTS saidas (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produto_id       UUID NOT NULL REFERENCES produtos(id),
    quantidade       NUMERIC(10,4) NOT NULL,
    unidade          TEXT NOT NULL,
    quantidade_base  NUMERIC(10,4) NOT NULL,
    setor_solicitante TEXT NOT NULL,
    nome_retirante   TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'pendente'
                       CHECK (status IN ('pendente','autorizado','executado','cancelado')),
    solicitado_por   UUID NOT NULL REFERENCES usuarios(id),
    autorizado_por   UUID REFERENCES usuarios(id),
    autorizado_em    TIMESTAMPTZ,
    executado_por    UUID REFERENCES usuarios(id),
    executado_em     TIMESTAMPTZ,
    observacao       TEXT,
    criado_em        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── TABELA: AJUSTES DE ESTOQUE ──────────────
CREATE TABLE IF NOT EXISTS ajustes_estoque (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produto_id     UUID NOT NULL REFERENCES produtos(id),
    quantidade_ant NUMERIC(10,4) NOT NULL,
    quantidade_nova NUMERIC(10,4) NOT NULL,
    motivo         TEXT NOT NULL,
    ajustado_por   UUID NOT NULL REFERENCES usuarios(id),
    criado_em      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── SEQUENCES para código interno ───────────
CREATE SEQUENCE IF NOT EXISTS seq_codigo_produto START 1000 INCREMENT 1;

-- ─── FUNÇÃO: gerar código interno ────────────
CREATE OR REPLACE FUNCTION gerar_codigo_interno()
RETURNS TEXT AS $$
BEGIN
    RETURN 'SFC-' || LPAD(nextval('seq_codigo_produto')::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;

-- ─── TRIGGER: código interno automático ──────
CREATE OR REPLACE FUNCTION trigger_codigo_interno()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.codigo_interno IS NULL OR NEW.codigo_interno = '' THEN
        NEW.codigo_interno := gerar_codigo_interno();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_codigo_interno
BEFORE INSERT ON produtos
FOR EACH ROW EXECUTE FUNCTION trigger_codigo_interno();

-- ─── TRIGGER: atualiza estoque em entradas ───
CREATE OR REPLACE FUNCTION trigger_entrada_estoque()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE produtos
    SET estoque_atual = estoque_atual + NEW.quantidade_base,
        atualizado_em = NOW()
    WHERE id = NEW.produto_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_entrada_insert
AFTER INSERT ON entradas
FOR EACH ROW EXECUTE FUNCTION trigger_entrada_estoque();

-- ─── TRIGGER: atualiza estoque em saídas executadas ──
CREATE OR REPLACE FUNCTION trigger_saida_estoque()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'executado' AND OLD.status != 'executado' THEN
        UPDATE produtos
        SET estoque_atual = estoque_atual - NEW.quantidade_base,
            atualizado_em = NOW()
        WHERE id = NEW.produto_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_saida_update
AFTER UPDATE ON saidas
FOR EACH ROW EXECUTE FUNCTION trigger_saida_estoque();

-- ─── TRIGGER: atualiza estoque em ajustes ────
CREATE OR REPLACE FUNCTION trigger_ajuste_estoque()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE produtos
    SET estoque_atual = NEW.quantidade_nova,
        atualizado_em = NOW()
    WHERE id = NEW.produto_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_ajuste_insert
AFTER INSERT ON ajustes_estoque
FOR EACH ROW EXECUTE FUNCTION trigger_ajuste_estoque();

-- ─── RLS (Row Level Security) ─────────────────
ALTER TABLE usuarios         ENABLE ROW LEVEL SECURITY;
ALTER TABLE produtos         ENABLE ROW LEVEL SECURITY;
ALTER TABLE categorias       ENABLE ROW LEVEL SECURITY;
ALTER TABLE notas_fiscais    ENABLE ROW LEVEL SECURITY;
ALTER TABLE entradas         ENABLE ROW LEVEL SECURITY;
ALTER TABLE saidas           ENABLE ROW LEVEL SECURITY;
ALTER TABLE ajustes_estoque  ENABLE ROW LEVEL SECURITY;

-- Permitir tudo via service_role (chave usada pelo backend)
CREATE POLICY "service_role_all" ON usuarios         FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON produtos         FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON categorias       FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON notas_fiscais    FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON entradas         FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON saidas           FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all" ON ajustes_estoque  FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ─── STORAGE BUCKET: notas fiscais ───────────
-- Execute no dashboard Storage ou via API:
-- INSERT INTO storage.buckets (id, name, public) VALUES ('notas-fiscais', 'notas-fiscais', false);

-- ─── CATEGORIAS PADRÃO ───────────────────────
INSERT INTO categorias (nome, descricao) VALUES
    ('Limpeza',       'Produtos de limpeza e higiene'),
    ('Escritório',    'Material de escritório e papelaria'),
    ('Informática',   'Equipamentos e suprimentos de TI'),
    ('Ferramentas',   'Ferramentas e utensílios'),
    ('EPI',           'Equipamentos de Proteção Individual'),
    ('Elétrico',      'Material elétrico e hidráulico'),
    ('Alimentício',   'Gêneros alimentícios'),
    ('Manutenção',    'Materiais de manutenção predial'),
    ('Outros',        'Itens diversos')
ON CONFLICT (nome) DO NOTHING;
