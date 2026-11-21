# Rota Vital — Mensageria com Fila SQS / ElasticMQ

Atividade Individual 2 · Mensageria  
Infraestrutura de Software · ADS · CESAR School · 2026.2  
Estudante: Victor

---

## 📋 Sobre o Projeto

Este projeto implementa uma comunicação assíncrona orientada a mensageria para a emissão de guias de transporte do sistema **Rota Vital**, utilizando uma fila compatível com a API do **Amazon SQS** (**ElasticMQ** local ou AWS SQS).

O sistema demonstra na prática quatro conceitos fundamentais de sistemas distribuídos e mensageria:
1. **Confirmação Explícita (ACK):** A mensagem permanece na fila até que o consumidor conclua o processamento com sucesso e a delete explicitamente (`delete_message`).
2. **Divisão de Carga (*Competing Consumers*):** Múltiplos consumidores paralelos retiram e processam mensagens concorrentemente, dividindo o trabalho de forma balanceada.
3. **Garantia de Entrega Pelo Menos Uma Vez (*At-Least-Once Delivery*):** Mensagens não são perdidas diante de falhas de processadores ou de rede.
4. **Visibilidade Temporária (*Visibility Timeout*):** Quando um consumidor falha em processar uma mensagem ou sofre um crash, a mensagem volta automaticamente a ficar visível para reprocessamento após o timeout de visibilidade configurado (15 segundos).

---

## 🚀 Caminho Escolhido

**Caminho A (Recomendado) — ElasticMQ local**, rodando inteiramente no computador na porta `9324`. O ElasticMQ implementa a mesma especificação REST/SQS da AWS, permitindo que todo o código funcione de maneira idêntica no Amazon SQS trocando apenas os parâmetros de conexão.

Para máxima flexibilidade no ambiente Windows:
- Suporte a execução via **Docker** (`softwaremill/elasticmq-native`).
- Suporte a execução via **Java Standalone JAR** (`elasticmq-server.jar`), dispensando Docker caso o ambiente não o possua instalado.

---

## 🔧 Pré-requisitos e Instalação

1. **Python 3.12+** instalado.
2. **Biblioteca Boto3** (SDK oficial da AWS para Python):
   ```bash
   pip install -r requirements.txt
   ```
3. **Runtime para o ElasticMQ** (escolha uma das opções):
   - **Opção 1 (Docker):** Docker Desktop em execução.
   - **Opção 2 (Java):** Java JRE/JDK 17+ instalado (ex: Eclipse Adoptium OpenJDK).

---

## 💻 Como Rodar

### Passo 1. Subir a Fila (ElasticMQ)

Em um terminal dedicado, inicie o ElasticMQ:

**Via script automatizado (detecta Docker ou Java):**
```bash
iniciar_elasticmq.bat
```

*Ou manualmente via Docker:*
```bash
docker run --rm -p 9324:9324 softwaremill/elasticmq-native
```

*Ou manualmente via Java Standalone:*
```bash
java -jar elasticmq\elasticmq-server.jar
```

O servidor iniciará e estará acessível em `http://localhost:9324`.

---

### Passo 2. Criar a Fila `guias` com VisibilityTimeout=15s

Em outro terminal, crie a fila com o tempo de visibilidade de 15 segundos:

**Via script Python (recomendado no Windows):**
```bash
py criar_fila.py
```

*Ou via AWS CLI v2 (com credenciais locais fictícias):*
```bash
# No Linux/Git Bash:
export AWS_ACCESS_KEY_ID=x AWS_SECRET_ACCESS_KEY=x AWS_DEFAULT_REGION=us-east-1
aws sqs create-queue --queue-name guias --attributes VisibilityTimeout=15 --endpoint-url http://localhost:9324

# No PowerShell:
$env:AWS_ACCESS_KEY_ID="x"; $env:AWS_SECRET_ACCESS_KEY="x"; $env:AWS_DEFAULT_REGION="us-east-1"
aws sqs create-queue --queue-name guias --attributes VisibilityTimeout=15 --endpoint-url http://localhost:9324
```

---

### Passo 3. Executar o Consumidor

Abra um terminal e execute o consumidor:

```bash
py consumidor.py
```
*(Ou dê duplo clique no script `iniciar_consumidor.bat`)*

O consumidor entrará em loop longo (*long polling* de 10 segundos), exibindo o seu PID e aguardando mensagens.

---

### Passo 4. Executar o Produtor

Em outro terminal, execute o produtor para enviar 21 mensagens (20 pedidos válidos `R-001` a `R-020` e 1 pedido inválido sem `requisicaoId`):

```bash
py produtor.py
```
*(Ou dê duplo clique no script `iniciar_produtor.bat`)*

Você verá no terminal do consumidor as 20 guias sendo processadas imediatamente e a mensagem inválida gerando erro:
```
falhou; volta para a fila: mensagem sem requisicaoId {'ApproximateReceiveCount': '1'}
```
Aguarde 15 segundos e observe a mesma mensagem reaparecendo no terminal com `'ApproximateReceiveCount': '2'`.

---

### Passo 5. Teste com Dois Consumidores Concorrentes

1. Pare os processos anteriores e limpe as mensagens da fila:
   ```bash
   py limpar_fila.py
   ```
2. Abra **dois terminais lado a lado** e inicie o consumidor em ambos:
   - **Terminal 1:** `py consumidor.py` (exibe PID A)
   - **Terminal 2:** `py consumidor.py` (exibe PID B)
3. No **Terminal 3**, execute novamente o produtor:
   ```bash
   py produtor.py
   ```
4. Observe que as 20 guias válidas são divididas dinamicamente entre os dois terminais (aproximadamente 10 para cada consumidor), com cada linha exibindo o respectivo PID do processo que a processou.

---

## 🌟 Opcionais Implementados

### 1. Dead Letter Queue (DLQ) e Política de Redrive
Para evitar que mensagens corrompidas ou venenosas (*poison pills*) fiquem em loop infinito na fila principal:
1. Execute o script de configuração da DLQ:
   ```bash
   py configurar_dlq.py
   ```
   Ele cria a fila `guias-dlq` e configura a `RedrivePolicy` na fila `guias` com `maxReceiveCount=3`.
2. Após 3 falhas consecutivas, a mensagem inválida sai automaticamente da fila `guias` e é direcionada para a DLQ.
3. Para inspecionar e comprovar as mensagens mortas retidas:
   ```bash
   py verificar_dlq.py
   ```

### 2. Integração com a Função Serverless da Atividade 1
O script `consumidor_atividade1.py` substitui a função interna `processar()` pela invocação direta do handler `lambda_handler` da Atividade 1 (`ProjetoServerLess/hello_world/app.py`):
```bash
py consumidor_atividade1.py
```

---

## ⚡ Execução Automatizada e Geração de Evidências

Para executar toda a bateria de testes e gerar automaticamente os arquivos de log e imagens do terminal na pasta `evidencias/`:

```bash
py executar_testes_locais.py
```

> 📹 **Roteiro de Gravação do Vídeo:** Consulte o arquivo [ROTEIRO_VIDEO.md](ROTEIRO_VIDEO.md) contendo o roteiro passo a passo minuto a minuto para a gravação de tela de até 3 minutos exigida para a entrega.

---

## ❓ Respostas às Perguntas Teóricas

### 1. Por que o consumidor só apaga a mensagem depois de processar? O que aconteceria se apagasse antes?

**Resposta:**
No modelo de mensageria com garantia de entrega (como o Amazon SQS), a leitura de uma mensagem via `receive_message` **não a remove** da fila; o serviço apenas a oculta temporariamente dos demais consumidores durante a janela do `VisibilityTimeout`. A exclusão explícita (`sqs.delete_message`) atua como o **ACK (Acknowledgement / Confirmação de Sucesso)** da aplicação.

O consumidor só deve apagar a mensagem após concluir com êxito todas as etapas de negócio (validação, gravação em banco de dados, emissão da guia), porque se ocorrer qualquer falha durante o processamento — como uma exceção não tratada, indisponibilidade temporária de um serviço externo, interrupção de energia ou queda do processo (*crash*) —, o consumidor morre **sem chamar** o `delete_message`. Com isso, a mensagem permanece sã e salva na fila, e assim que o `VisibilityTimeout` expirar, o SQS a torna visível novamente para que outro consumidor íntegro a receba e a processe.

**Se apagasse antes de processar:**
O sistema passaria a operar involuntariamente no modelo *at-most-once* (no máximo uma vez). Se o consumidor apagasse a mensagem assim que a recebesse e sofresse uma falha fatal antes de concluir a emissão da guia, **a requisição seria permanentemente perdida**. No contexto do Rota Vital, um pedido de sangue de emergência de um hospital simplesmente desapareceria sem deixar rastro e sem emissão de guia, gerando riscos críticos à vida dos pacientes.

---

### 2. Com dois consumidores, como as mensagens se dividiram? A ordem foi mantida? O que a documentação do SQS diz sobre ordem nas filas padrão?

**Resposta:**
- **Como as mensagens se dividiram:** No teste realizado com dois consumidores rodando em processos concorrentes (PIDs `10420` e `28936`), as 20 mensagens válidas foram divididas de maneira equilibrada (10 mensagens processadas pelo PID 10420 e 10 mensagens pelo PID 28936). Essa divisão ocorre pelo padrão *Competing Consumers*: cada consumidor faz requisições `receive_message` com parâmetro `MaxNumberOfMessages=10` e *long polling*; o consumidor que estiver ocioso e tiver sua requisição atendida primeiro pelo SQS recebe o lote disponível no nó da fila, enquanto o outro recebe as mensagens subsequentes.
- **A ordem foi mantida?** **Não.** A ordem sequencial estrita dos IDs (`R-001`, `R-002`, ..., `R-020`) não foi mantida no processamento final. Por exemplo, mensagens com identificadores maiores chegaram a ser processadas antes de mensagens de identificadores menores, e os lotes foram intercalados entre os processos.
- **O que diz a documentação oficial da AWS:** O Amazon SQS define que em **filas padrão (Standard Queues)** a entrega de mensagens é baseada em **melhor esforço de ordenação (*best-effort ordering*)**. Como as filas Standard são distribuídas geograficamente em múltiplos servidores e partições para alcançar throughput quase ilimitado, o SQS não garante que as mensagens serão entregues exatamente na mesma sequência em que foram enviadas. Caso o sistema exija rigorosamente a ordem FIFO (First-In, First-Out) sem duplicidade, a documentação orienta o uso de **Filas FIFO do SQS**, que utilizam identificadores de grupo de mensagens (`MessageGroupId`) e deduplicação (`MessageDeduplicationId`), às custas de um throughput limitado em comparação às filas padrão.

---

### 3. A fila padrão garante entrega pelo menos uma vez, e a mesma mensagem pode chegar duas vezes. O que isso exige do consumidor? Como vocês o tornariam idempotente?

**Resposta:**
- **O que isso exige do consumidor:** A garantia de entrega *pelo menos uma vez (at-least-once delivery)* significa que nenhuma mensagem válida se perderá, mas em cenários de retransmissão de rede, latência alta ou expiração do `VisibilityTimeout` antes da conclusão do `delete_message`, o SQS pode entregar duplicatas da mesma mensagem. Isso exige que o consumidor seja **estritamente idempotente**. Uma operação idempotente é aquela cujo resultado prático final é idêntico se ela for executada uma única vez ou múltiplas vezes consecutivas. No Rota Vital, receber a mesma requisição `R-001` três vezes deve resultar na emissão de exatamente **uma única guia** `G-R-001`.
- **Como torná-lo idempotente na prática:**
  1. **Chave de Deduplicação / Idempotência:** Utilizar o identificador único de negócio já existente no payload (`requisicaoId`, ex: `R-001`) ou um token de idempotência gerado na origem.
  2. **Verificação de Estado em Tabela de Controle (Cache / Banco de Dados):** Antes de iniciar o processamento da guia, o consumidor consulta uma tabela (ex: Amazon DynamoDB, Redis ou PostgreSQL) para checar se o `requisicaoId` já possui uma guia emitida.
     - Se **já existir**, o consumidor não reprocessa; apenas recupera a guia existente (ou ignora a computação redundante) e invoca `sqs.delete_message` para eliminar a duplicata da fila.
     - Se **não existir**, o consumidor processa e registra o novo estado de forma atômica.
  3. **Operação Atômica com Constraint de Unicidade:** Utilizar uma restrição de chave única no banco (`UNIQUE CONSTRAINT (requisicao_id)` em SQL ou expressão condicional `attribute_not_exists(requisicaoId)` em DynamoDB). Caso haja corrida entre dois consumidores tentando processar a mesma mensagem ao mesmo tempo, apenas um conseguirá gravar o registro e o outro capturará a violação de unicidade, descartando com segurança a duplicata.

---

### 4. Expliquem o visibility timeout com o que viram na mensagem inválida. Para que serve uma DLQ?

**Resposta:**
- **O Visibility Timeout na prática:** O tempo de visibilidade é o período de tolerância concedido pelo SQS para que um consumidor processe e confirme uma mensagem. Durante esses 15 segundos, a mensagem fica oculta para outros consumidores. No experimento com a mensagem inválida `{"hospital": "H-Recife"}`:
  1. O consumidor recebeu a mensagem e invocou `processar()`. Como não havia o campo obrigatório `requisicaoId`, a validação lançou `ValueError("mensagem sem requisicaoId")`.
  2. A execução caiu no bloco `except`, imprimindo a mensagem de falha e **não executando** `sqs.delete_message`.
  3. A mensagem permaneceu invisível durante os 15 segundos configurados na fila.
  4. Exatamente após 15 segundos, o SQS liberou a mensagem novamente. O consumidor a recebeu pela segunda vez, exibindo nos atributos do sistema o contador de recebimento atualizado: `ApproximateReceiveCount: '2'`.
  5. Sem intervenção ou sem DLQ, essa mensagem continuaria em um ciclo infinito a cada 15 segundos, desperdiçando ciclos de CPU e saturando os logs.
- **Para que serve uma Dead Letter Queue (DLQ):** Uma DLQ (Fila de Mensagens Mortas) é uma fila secundária para onde mensagens que não puderam ser processadas com sucesso após um determinado número máximo de tentativas (`maxReceiveCount`, por exemplo, 3) são automaticamente roteadas pelo próprio SQS. A DLQ serve para:
  - **Evitar o "envenenamento de fila" (*poison pill*):** Impede que mensagens corrompidas ou incompatíveis travem consumidores ou consumam recursos indefinidamente.
  - **Isolamento para Auditoria e Correção:** Permite que a equipe de engenharia e operações inspecione os payloads das mensagens com erro, corrija eventuais bugs na aplicação e, posteriormente, utilize o recurso de *Redrive* para devolver essas mensagens à fila principal após a correção.

---

### 5. No Rota Vital, qual a diferença entre o hospital chamar a emissão de guia diretamente (síncrono) e passar por uma fila (assíncrono)? O que se ganha e o que se perde?

**Resposta:**

| Característica | Comunicação Direta (Síncrona / HTTP) | Comunicação por Fila (Assíncrona / SQS) |
| :--- | :--- | :--- |
| **Mecanismo** | Chamada HTTP/REST direta para a API de guias. O cliente fica bloqueado aguardando resposta. | Envio do evento para a fila SQS. O cliente recebe confirmação imediata de enfileiramento (ACK). |
| **Acoplamento** | **Forte acoplamento temporal e espacial.** Ambos os serviços precisam estar online e operantes simultaneamente no momento da chamada. | **Total desacoplamento.** Produtor e consumidor operam de forma independente e assíncrona. |

**O que se GANHA ao passar por uma fila:**
1. **Resiliência e Tolerância a Falhas:** Se o serviço emissor de guias estiver fora do ar, passando por deploy ou instabilidade temporária, o hospital não recebe erro 500. A requisição fica persistida com segurança na fila até o serviço se restabelecer.
2. **Nivelamento de Picos de Carga (*Load Leveling / Buffering*):** Em situações de emergência (ex: desastres urbanos ou acidentes com alta demanda por bolsas de sangue), centenas de hospitais podem emitir pedidos ao mesmo tempo. A fila absorve o choque de requisições, evitando a queda do banco de dados ou saturação de servidores; os consumidores processam no ritmo máximo que a infraestrutura suporta.
3. **Escalabilidade Elástica e Independente:** É possível escalar apenas os nós consumidores proporcionalmente ao tamanho da fila (`ApproximateNumberOfMessagesVisible`), sem alterar o produtor.

**O que se PERDE ao passar por uma fila:**
1. **Perda da Resposta Imediata no Mesmo Ciclo:** O hospital não recebe a guia emitida de forma síncrona na mesma conexão HTTP. O sistema precisará implementar consulta posterior (*polling*), webhooks de retorno ou notificações em tempo real (via WebSocket ou push notification/SNS).
2. **Consistência Eventual:** Há um atraso (latência de propagação e tempo de fila) entre o momento em que o pedido é feito e o momento em que a guia é efetivamente gerada e persistida.
3. **Aumento da Complexidade Arquitetural:** Exige gerenciar infraestrutura de filas, visibilidade, DLQs, idempotência, deduplicação e monitoramento de mensagens não processadas.

---

## 📁 Estrutura do Repositório

```
ProjetoMensageria/
├── criar_fila.py                # Script em Python para criar a fila 'guias' (VisibilityTimeout=15s)
├── produtor.py                  # Produtor: publica 20 mensagens válidas e 1 inválida
├── consumidor.py                # Consumidor: processa e só apaga após sucesso; trata falhas
├── configurar_dlq.py            # Opcional: configura Dead Letter Queue (guias-dlq) e RedrivePolicy
├── verificar_dlq.py             # Opcional: inspeciona mensagens retidas na DLQ
├── consumidor_atividade1.py     # Opcional: consumidor integrado ao Lambda da Atividade 1
├── limpar_fila.py               # Utilitário para purgar/limpar mensagens das filas
├── executar_testes_locais.py    # Suite de automação de testes e geração de relatórios
├── iniciar_elasticmq.bat        # Atalho Windows para subir ElasticMQ (Docker ou Java)
├── iniciar_produtor.bat         # Atalho Windows para executar o produtor
├── iniciar_consumidor.bat       # Atalho Windows para executar o consumidor
├── requirements.txt             # Dependências Python (boto3, pillow)
├── .gitignore                   # Arquivos ignorados pelo Git
├── ROTEIRO_VIDEO.md             # Roteiro minuto a minuto para o vídeo de até 3 minutos
├── evidencias/                  # Pasta com prints (.png) e saídas (.txt) dos experimentos
│   ├── 01-fila-criada.png
│   ├── 01-fila-criada.txt
│   ├── 02-produtor-envio.png
│   ├── 02-produtor-envio.txt
│   ├── 03-um-consumidor-e-timeout.png
│   ├── 03-um-consumidor-e-timeout.txt
│   ├── 04-dois-consumidores-divisao-carga.png
│   ├── 04-dois-consumidores-divisao-carga.txt
│   ├── 05-dlq-mensagens-mortas.png
│   ├── 05-dlq-mensagens-mortas.txt
│   └── README.md
└── README.md                    # Este arquivo
```

---

## 🤖 Uso de IA

*Declaração de conformidade com a política institucional PO-CESAR-021:*

- **Ferramenta:** Antigravity (Google DeepMind)
- **Finalidade:** Auxílio no planejamento da estrutura do repositório, escrita dos scripts de automação em Python (`boto3`), criação das classes geradoras de relatórios visuais de terminal para evidências e estruturação das respostas conceituais sobre mensageria e SQS.
- **Como foi validado:** O servidor ElasticMQ foi executado localmente na porta 9324; a fila foi criada e inspecionada via SDK `boto3`; os fluxos com 1 consumidor, 2 consumidores concorrentes e Dead Letter Queue foram executados e validados na prática; as saídas de terminal e atributos de cabeçalho (`ApproximateReceiveCount`, `VisibilityTimeout`) foram verificados e comparados com a documentação oficial do Amazon SQS.
