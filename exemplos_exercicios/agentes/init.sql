CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    ticket_id INT NOT NULL,
    conversation_id INT NOT NULL,
    user_id INT NOT NULL,
    speaker VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    ticket_status VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_configs (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL UNIQUE,
    agent_type VARCHAR(100) NOT NULL,
    objective TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    model_name VARCHAR(100) DEFAULT 'gpt-4.1-mini',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    ticket_id INT,
    input_text TEXT,
    output_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedbacks (
    feedback_id INT PRIMARY KEY,
    feedback_text TEXT,
    created_at TIMESTAMP,
    channel VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS ticket_memory (
    ticket_id INT PRIMARY KEY,
    problem TEXT,
    attempted_solutions TEXT,
    current_status TEXT,
    last_client_message TEXT,
    resolved BOOLEAN,
    signals TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sensitive_items (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL,
    risk TEXT NOT NULL,
    category TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS internal_notes (
    id SERIAL PRIMARY KEY,
    ticket_id INT,
    note_text TEXT NOT NULL,
    note_status TEXT NOT NULL,
    blocked_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    cliente VARCHAR(100),
    mensagem TEXT,
    categoria VARCHAR(50),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS backlog (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    responsavel VARCHAR(100),
    status VARCHAR(50) NOT NULL,
    prioridade VARCHAR(20) NOT NULL,
    story_points INTEGER,
    dias_em_aberto INTEGER DEFAULT 0,
    bugs_relacionados INTEGER DEFAULT 0,
    sprint VARCHAR(50),
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS knowledge_bases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kb_documents (
    id SERIAL PRIMARY KEY,
    kb_id INT NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kb_chunks (
    id SERIAL PRIMARY KEY,
    document_id INT NOT NULL REFERENCES kb_documents(id) ON DELETE CASCADE,
    chunk_order INT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO tickets (cliente, mensagem, categoria)
SELECT * FROM (
    VALUES
    ('Maria', 'App travou ao tentar pagar', 'bug'),
    ('João', 'Gostei muito da nova interface', 'elogio'),
    ('Ana', 'Não consigo fazer login', 'bug'),
    ('Carlos', 'Pagamento foi cobrado duas vezes', 'pagamento'),
    ('Fernanda', 'Sistema está muito lento', 'performance')
) AS v(cliente, mensagem, categoria)
WHERE NOT EXISTS (SELECT 1 FROM tickets);

INSERT INTO knowledge_bases (name, description)
VALUES
('support_kb', 'Problemas comuns de suporte'),
('policy_kb', 'Políticas internas'),
('product_faq', 'FAQ do produto')
ON CONFLICT (name) DO NOTHING;

INSERT INTO kb_documents (kb_id, title, source)
SELECT kb.id, v.title, v.source
FROM (
    VALUES
    ('support_kb', 'Erros de pagamento', 'manual'),
    ('support_kb', 'Problemas de login', 'manual'),
    ('support_kb', 'Lentidão no sistema', 'manual'),
    ('support_kb', 'Falhas no app mobile', 'manual'),
    ('policy_kb', 'Política de reembolso', 'manual'),
    ('policy_kb', 'Política de segurança', 'manual'),
    ('policy_kb', 'Privacidade de dados', 'manual'),
    ('product_faq', 'FAQ App Mobile', 'manual'),
    ('product_faq', 'FAQ Conta e Cadastro', 'manual')
) AS v(kb_name, title, source)
JOIN knowledge_bases kb ON kb.name = v.kb_name
WHERE NOT EXISTS (
    SELECT 1
    FROM kb_documents d
    WHERE d.kb_id = kb.id AND d.title = v.title
);

INSERT INTO kb_chunks (document_id, chunk_order, content, metadata)
SELECT d.id, v.chunk_order, v.content, v.metadata::jsonb
FROM (
    VALUES
    ('Erros de pagamento', 1, 'Cobrança duplicada pode ocorrer por falha na confirmação da transação.', '{"categoria":"pagamento"}'),
    ('Erros de pagamento', 2, 'Sempre verificar o histórico antes de solicitar estorno.', '{"categoria":"pagamento"}'),
    ('Erros de pagamento', 3, 'Falhas podem ocorrer por timeout ou recusa da operadora.', '{"categoria":"pagamento"}'),
    ('Problemas de login', 1, 'Usuários devem verificar e-mail e senha antes de redefinir acesso.', '{"categoria":"login"}'),
    ('Problemas de login', 2, 'Bloqueios temporários ocorrem após múltiplas tentativas inválidas.', '{"categoria":"login"}'),
    ('Problemas de login', 3, 'Recuperação de senha deve ser feita via e-mail cadastrado.', '{"categoria":"login"}'),
    ('Lentidão no sistema', 1, 'Sistema pode ficar lento em horários de pico.', '{"categoria":"performance"}'),
    ('Lentidão no sistema', 2, 'Recomenda-se verificar conexão do usuário.', '{"categoria":"performance"}'),
    ('Lentidão no sistema', 3, 'Cache local pode impactar performance do app.', '{"categoria":"performance"}'),
    ('Falhas no app mobile', 1, 'Problemas podem ocorrer em versões antigas do aplicativo.', '{"categoria":"mobile"}'),
    ('Falhas no app mobile', 2, 'Atualizar o app pode resolver a maioria dos erros.', '{"categoria":"mobile"}'),
    ('Falhas no app mobile', 3, 'Falhas de sincronização podem ocorrer sem internet.', '{"categoria":"mobile"}'),
    ('Política de reembolso', 1, 'Reembolsos podem ser solicitados em até 7 dias.', '{"categoria":"policy"}'),
    ('Política de reembolso', 2, 'Casos excepcionais devem ser avaliados manualmente.', '{"categoria":"policy"}'),
    ('Política de segurança', 1, 'Usuários devem manter suas credenciais seguras.', '{"categoria":"security"}'),
    ('Política de segurança', 2, 'Não compartilhar senhas com terceiros.', '{"categoria":"security"}'),
    ('Privacidade de dados', 1, 'Dados pessoais são protegidos conforme LGPD.', '{"categoria":"privacy"}'),
    ('Privacidade de dados', 2, 'Usuários podem solicitar exclusão de dados.', '{"categoria":"privacy"}'),
    ('FAQ App Mobile', 1, 'App disponível para Android e iOS.', '{"categoria":"faq"}'),
    ('FAQ App Mobile', 2, 'Requer conexão com internet.', '{"categoria":"faq"}'),
    ('FAQ Conta e Cadastro', 1, 'Cadastro requer e-mail válido.', '{"categoria":"faq"}'),
    ('FAQ Conta e Cadastro', 2, 'Conta pode ser excluída pelo suporte.', '{"categoria":"faq"}')
) AS v(title, chunk_order, content, metadata)
JOIN kb_documents d ON d.title = v.title
WHERE NOT EXISTS (
    SELECT 1
    FROM kb_chunks c
    WHERE c.document_id = d.id AND c.chunk_order = v.chunk_order
);

