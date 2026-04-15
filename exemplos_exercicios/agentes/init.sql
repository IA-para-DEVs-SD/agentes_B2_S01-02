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
(
    'support_kb',
    'Base de conhecimento com problemas comuns de suporte ao usuário, incluindo dificuldades de login, erros de pagamento, lentidão do sistema e falhas no aplicativo.'
),
(
    'policy_kb',
    'Base com políticas internas e regras do sistema, incluindo reembolso, segurança da conta e privacidade de dados, usada para orientar decisões e validações.'
),
(
    'product_faq',
    'Perguntas frequentes sobre o produto e uso do aplicativo, incluindo criação de conta, funcionalidades básicas e requisitos do sistema.'
)
ON CONFLICT (name) DO NOTHING;


INSERT INTO kb_documents (kb_id, title, source)
SELECT
    kb.id,
    v.title,
    v.source
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
JOIN knowledge_bases kb
    ON kb.name = v.kb_name
WHERE NOT EXISTS (
    SELECT 1
    FROM kb_documents d
    WHERE d.kb_id = kb.id
      AND d.title = v.title
);


INSERT INTO kb_chunks (document_id, chunk_order, content, metadata)
SELECT
    d.id,
    v.chunk_order,
    v.content,
    v.metadata::jsonb
FROM (
    VALUES
        ('support_kb', 'Erros de pagamento', 1, 'Cobrança duplicada pode acontecer quando há falha na confirmação da transação ou múltiplas tentativas de pagamento. Antes de solicitar estorno, verifique o histórico completo da conta.', '{"categoria":"pagamento","tipo":"kb"}'),
        ('support_kb', 'Erros de pagamento', 2, 'Timeout durante a transação pode causar incerteza no usuário, mesmo quando a operadora processa o pagamento. Oriente aguardar alguns minutos antes de tentar novamente.', '{"categoria":"pagamento","tipo":"kb"}'),
        ('support_kb', 'Erros de pagamento', 3, 'Recusas de pagamento podem ocorrer por limites do cartão ou bloqueios da operadora. Sempre validar com o usuário antes de abrir chamado.', '{"categoria":"pagamento","tipo":"kb"}'),

        ('support_kb', 'Problemas de login', 1, 'Se o usuário não conseguir acessar a conta, confirme e-mail, senha e possíveis erros de digitação antes de iniciar recuperação.', '{"categoria":"login","tipo":"kb"}'),
        ('support_kb', 'Problemas de login', 2, 'Bloqueios temporários acontecem após várias tentativas inválidas. Nesses casos, o usuário deve aguardar ou seguir o fluxo de recuperação.', '{"categoria":"login","tipo":"kb"}'),
        ('support_kb', 'Problemas de login', 3, 'Recuperação de senha deve ser feita pelo e-mail cadastrado. Caso não tenha acesso, será necessário validar identidade.', '{"categoria":"login","tipo":"kb"}'),

        ('support_kb', 'Lentidão no sistema', 1, 'O sistema pode apresentar lentidão em horários de pico devido ao alto volume de acessos simultâneos.', '{"categoria":"performance","tipo":"kb"}'),
        ('support_kb', 'Lentidão no sistema', 2, 'Verifique conexão, navegador e dispositivo do usuário, pois problemas locais podem impactar a performance.', '{"categoria":"performance","tipo":"kb"}'),
        ('support_kb', 'Lentidão no sistema', 3, 'Cache acumulado pode afetar o desempenho. Recomenda-se limpeza e novo teste.', '{"categoria":"performance","tipo":"kb"}'),

        ('support_kb', 'Falhas no app mobile', 1, 'Versões antigas do aplicativo podem causar erros. Confirmar versão instalada e sistema operacional.', '{"categoria":"mobile","tipo":"kb"}'),
        ('support_kb', 'Falhas no app mobile', 2, 'Atualizar o aplicativo resolve a maioria dos problemas relacionados a compatibilidade e sincronização.', '{"categoria":"mobile","tipo":"kb"}'),
        ('support_kb', 'Falhas no app mobile', 3, 'Falhas de sincronização podem ocorrer sem conexão estável com a internet.', '{"categoria":"mobile","tipo":"kb"}'),

        ('policy_kb', 'Política de reembolso', 1, 'Reembolsos podem ser solicitados dentro do prazo definido pela política vigente, mediante validação do pagamento.', '{"categoria":"policy","tipo":"policy"}'),
        ('policy_kb', 'Política de reembolso', 2, 'Casos excepcionais devem ser analisados manualmente com base em evidências e histórico.', '{"categoria":"policy","tipo":"policy"}'),

        ('policy_kb', 'Política de segurança', 1, 'Usuários devem manter credenciais seguras e não compartilhar senhas com terceiros.', '{"categoria":"security","tipo":"policy"}'),
        ('policy_kb', 'Política de segurança', 2, 'Atividades suspeitas devem ser tratadas com prioridade e podem exigir redefinição de acesso.', '{"categoria":"security","tipo":"policy"}'),

        ('policy_kb', 'Privacidade de dados', 1, 'Dados pessoais são tratados conforme LGPD e políticas internas de privacidade.', '{"categoria":"privacy","tipo":"policy"}'),
        ('policy_kb', 'Privacidade de dados', 2, 'Usuários podem solicitar exclusão de dados, respeitando obrigações legais.', '{"categoria":"privacy","tipo":"policy"}'),

        ('product_faq', 'FAQ App Mobile', 1, 'O aplicativo está disponível para Android e iOS e requer conexão com internet.', '{"categoria":"faq","tipo":"faq"}'),
        ('product_faq', 'FAQ App Mobile', 2, 'Para melhor desempenho, manter o app sempre atualizado.', '{"categoria":"faq","tipo":"faq"}'),

        ('product_faq', 'FAQ Conta e Cadastro', 1, 'O cadastro requer e-mail válido e acesso ao mesmo para validação.', '{"categoria":"faq","tipo":"faq"}'),
        ('product_faq', 'FAQ Conta e Cadastro', 2, 'A conta pode ser excluída mediante solicitação ao suporte.', '{"categoria":"faq","tipo":"faq"}')
) AS v(kb_name, title, chunk_order, content, metadata)
JOIN knowledge_bases kb
    ON kb.name = v.kb_name
JOIN kb_documents d
    ON d.kb_id = kb.id
   AND d.title = v.title
WHERE NOT EXISTS (
    SELECT 1
    FROM kb_chunks c
    WHERE c.document_id = d.id
      AND c.chunk_order = v.chunk_order
);
