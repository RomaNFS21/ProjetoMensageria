# Roteiro para Gravação do Vídeo de Demonstração

**Atividade Individual 2 — Mensageria (CESAR School · 2026.2)**  
**Duração máxima:** até 3 minutos  
**Entrega:** Link do vídeo (YouTube não-listado, Google Drive ou Loom) postado no Google Classroom.

---

## 🎯 Objetivo do Vídeo

Demonstrar de forma prática e objetiva:
1. A fila ElasticMQ (ou Amazon SQS) no ar e configurada com `VisibilityTimeout=15s`.
2. O envio de 21 mensagens pelo produtor (20 pedidos válidos e 1 inválido).
3. A divisão de trabalho entre **dois consumidores simultâneos** rodando em terminais separados (cada um exibindo seu PID).
4. O tratamento de falha: a **mensagem inválida voltando para a fila após o Visibility Timeout** de 15 segundos, com `ApproximateReceiveCount` aumentando.
5. (Opcional/Bônus): A atuação da **Dead Letter Queue (DLQ)** isolando a mensagem inválida após 3 tentativas.

---

## ⏱️ Minuto a Minuto Sugerido

### Minuto 0:00 a 0:35 — Apresentação e Fila no Ar
- **O que falar:**
  > "Olá, sou Victor. Esta é a apresentação da Atividade 2 de Mensageria da disciplina de Infraestrutura de Software. Implementamos uma arquitetura orientada a mensageria compatível com Amazon SQS utilizando o ElasticMQ local na porta 9324."
- **O que mostrar na tela:**
  - Terminal com o ElasticMQ rodando (`iniciar_elasticmq.bat` ou `docker run`), mostrando o servidor SQS ativo em `http://localhost:9324`.
  - Execução rápida do comando de verificação ou criação da fila:
    ```bash
    py criar_fila.py
    ```
  - Destaque para o atributo `VisibilityTimeout = 15` segundos.

### Minuto 0:35 a 1:40 — Dois Consumidores e Divisão de Carga
- **O que falar:**
  > "Agora, vamos abrir dois terminais lado a lado para rodar dois consumidores independentes. Cada consumidor roda em um processo separado e imprime seu PID único no início de cada linha de processamento. Em seguida, vamos executar o produtor."
- **O que mostrar na tela:**
  - Dividir a tela com dois terminais abertos:
    - **Terminal 1:** `py consumidor.py` (aparece: `[PID 1] Consumidor iniciado...`)
    - **Terminal 2:** `py consumidor.py` (aparece: `[PID 2] Consumidor iniciado...`)
  - No **Terminal 3**, rodar o produtor:
    ```bash
    py produtor.py
    ```
  - Mostrar os dois consumidores processando em paralelo:
    - O Terminal 1 processa algumas guias (ex: `PID1 guia G-R-001 H-Recife`).
    - O Terminal 2 processa outras guias (ex: `PID2 guia G-R-002 H-Recife`).
  - **Comentário de áudio:**
    > "Vejam que as mensagens são divididas dinamicamente entre os dois consumidores (padrão Competing Consumers). Como estamos em uma fila SQS Standard, a ordem de entrega é de melhor esforço (best-effort)."

### Minuto 1:40 a 2:30 — Mensagem Inválida e Visibility Timeout
- **O que falar:**
  > "O produtor enviou 20 pedidos válidos e 1 pedido inválido sem 'requisicaoId'. Quando o consumidor tentou processar esse pedido, ocorreu uma falha intencional. Como o consumidor só apaga a mensagem após o processamento bem-sucedido, o delete_message não foi chamado."
- **O que mostrar na tela:**
  - O log no terminal exibindo:
    ```
    falhou; volta para a fila: mensagem sem requisicaoId {'ApproximateReceiveCount': '1'}
    ```
  - Aguardar ~15 segundos em silêncio ou explicando o conceito.
  - Mostrar a mesma mensagem reaparecendo no terminal:
    ```
    falhou; volta para a fila: mensagem sem requisicaoId {'ApproximateReceiveCount': '2'}
    ```
  - **Comentário de áudio:**
    > "Exatamente após os 15 segundos do VisibilityTimeout, o SQS tornou a mensagem visível novamente. Ela foi reentregue ao consumidor, agora com o ApproximateReceiveCount igual a 2. Isso comprova a garantia de entrega pelo menos uma vez (at-least-once) e o funcionamento do Visibility Timeout."

### Minuto 2:30 a 3:00 — Conclusão e DLQ (Opcional)
- **O que falar:**
  > "Configuramos também uma Dead Letter Queue (DLQ) com maxReceiveCount=3. Após 3 tentativas com falha, a mensagem é retirada da fila principal e enviada para a fila 'guias-dlq', evitando o envenenamento da fila (poison pill). Todos os requisitos foram atendidos e testados."
- **O que mostrar na tela:**
  - Exibir rapidamente o comando:
    ```bash
    py verificar_dlq.py
    ```
  - Mostrar a mensagem isolada na `guias-dlq`.
  - Agradecer e encerrar.

---

## 🛠️ Dicas para a Gravação
- Deixe as janelas organizadas antes de iniciar a gravação (ElasticMQ de um lado, os 2 consumidores lado a lado, e o produtor pronto para rodar).
- A ferramenta OBS Studio, Windows Game Bar (`Win + G`) ou extensões de navegador como Loom são ótimas opções.
- Mantenha o áudio claro e objetivo, sem pausas excessivas.
