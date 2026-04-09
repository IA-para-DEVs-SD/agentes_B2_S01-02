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

CREATE TABLE feedbacks (
    feedback_id INT PRIMARY KEY,
    feedback_text TEXT,
    created_at TIMESTAMP,
    channel VARCHAR(20)
);