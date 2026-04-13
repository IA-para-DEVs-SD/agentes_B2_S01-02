Exemplo com o seu ticket 1001

Histórico já existente:

client: Não consigo fazer login
atendente: Você pode tentar redefinir sua senha
client: Já tentei e não funcionou

Agora chega uma nova mensagem:

client: Agora apareceu que minha conta está bloqueada

Se o agente olhar só essa nova mensagem, ele pode responder algo genérico.

Mas se ele tiver memória, ele entende:

o problema começou com login
já tentaram redefinir senha
não funcionou
agora surgiu evidência nova: conta bloqueada

Então a resposta pode evoluir direito.

Fluxo conceitual

nova mensagem
   ↓
salva no banco (conversations)
   ↓
busca histórico do ticket
   ↓
recalcula estado
   ↓
salva estado (ticket_memory)
   ↓
gera resposta


python3 insert_message.py
