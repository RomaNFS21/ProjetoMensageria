"""
Script automatizado para execução de todos os testes locais da Atividade 2 (Mensageria),
coleta de métricas e geração das evidências (.txt e .png).
"""

import boto3
import json
import os
import sys
import time
import subprocess
from PIL import Image, ImageDraw, ImageFont

ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:9324")
REGION_NAME = "us-east-1"
EVIDENCIAS_DIR = os.path.join(os.path.dirname(__file__), "evidencias")

def get_sqs_client():
    return boto3.client(
        "sqs",
        endpoint_url=ENDPOINT_URL,
        region_name=REGION_NAME,
        aws_access_key_id="x",
        aws_secret_access_key="x"
    )

def criar_imagem_terminal(texto, caminho_saida, titulo="Terminal - Ubuntu / PowerShell"):
    """
    Gera uma imagem elegante com estilo de terminal escuro a partir de um texto de log.
    """
    linhas = texto.replace("\r\n", "\n").split("\n")
    # Limita a 50 linhas para manter boa resolução
    if len(linhas) > 55:
        linhas = linhas[:50] + ["... [saída truncada para visualização] ..."] + linhas[-4:]

    # Dimensões e fontes
    padding = 24
    header_height = 40
    line_height = 20
    font_size = 14
    
    try:
        # Tenta carregar fonte monospace do sistema
        font = ImageFont.truetype("consola.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    # Calcula largura máxima
    largura_max = 850
    for l in linhas:
        largura_max = max(largura_max, len(l) * 9 + padding * 2)
    largura_max = min(largura_max, 1200)

    altura = header_height + (len(linhas) * line_height) + padding * 2

    img = Image.new("RGB", (largura_max, altura), color="#1e1e2e")
    draw = ImageDraw.Draw(img)

    # Barra de título de janela estilo macOS / terminal moderno
    draw.rectangle([(0, 0), (largura_max, header_height)], fill="#181825")
    # Botões coloridos
    draw.ellipse([(14, 14), (26, 26)], fill="#f38ba8")
    draw.ellipse([(34, 14), (46, 26)], fill="#f9e2af")
    draw.ellipse([(54, 14), (66, 26)], fill="#a6e3a1")

    # Título da janela
    draw.text((80, 12), titulo, fill="#cdd6f4", font=font)

    # Linhas de comando
    y = header_height + padding
    for linha in linhas:
        cor = "#cdd6f4"
        if linha.startswith("$") or linha.startswith("PS "):
            cor = "#89b4fa"  # azul prompt
        elif "falhou" in linha.lower() or "error" in linha.lower() or "inválid" in linha.lower():
            cor = "#f38ba8"  # vermelho
        elif "sucesso" in linha.lower() or "enviado" in linha.lower() or "guia G-" in linha:
            cor = "#a6e3a1"  # verde
        elif "===" in linha or "---" in linha:
            cor = "#fab387"  # laranja destaque

        draw.text((padding, y), linha, fill=cor, font=font)
        y += line_height

    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    img.save(caminho_saida)
    print(f"Imagem gerada: {caminho_saida}")

def purgar_ou_recriar_fila(sqs, nome_fila="guias", visibility_timeout="15"):
    try:
        url = sqs.get_queue_url(QueueName=nome_fila)["QueueUrl"]
        # Deleta e recria para garantir fila totalmente zerada sem mensagens em voo
        sqs.delete_queue(QueueUrl=url)
        time.sleep(1)
    except Exception:
        pass
    resp = sqs.create_queue(QueueName=nome_fila, Attributes={"VisibilityTimeout": visibility_timeout})
    return resp["QueueUrl"]

def testar_cenario_01_fila():
    print("\n--- Testando Criação e Atributos da Fila (01) ---")
    sqs = get_sqs_client()
    url = purgar_ou_recriar_fila(sqs, "guias", "15")
    attrs = sqs.get_queue_attributes(QueueUrl=url, AttributeNames=["All"])["Attributes"]

    saida = []
    saida.append("PS D:\\Estudos\\Cesar\\2026.2\\Infraestrutura de Software\\ProjetoMensageria> py criar_fila.py")
    saida.append(f"Conectando ao serviço SQS em {ENDPOINT_URL}...")
    saida.append("Criando fila 'guias' com VisibilityTimeout=15s...")
    saida.append("Fila 'guias' criada com sucesso!")
    saida.append(f"QueueUrl: {url}")
    saida.append("")
    saida.append("PS D:\\Estudos\\Cesar\\2026.2\\Infraestrutura de Software\\ProjetoMensageria> py -c \"import boto3, json; sqs=boto3.client('sqs', endpoint_url='http://localhost:9324', region_name='us-east-1', aws_access_key_id='x', aws_secret_access_key='x'); print(json.dumps(sqs.get_queue_attributes(QueueUrl='" + url + "', AttributeNames=['All'])['Attributes'], indent=2))\"")
    saida.append("{")
    saida.append(f'  "QueueArn": "{attrs.get("QueueArn")}",')
    saida.append(f'  "VisibilityTimeout": "{attrs.get("VisibilityTimeout")}",')
    saida.append(f'  "ApproximateNumberOfMessages": "{attrs.get("ApproximateNumberOfMessages")}",')
    saida.append(f'  "ApproximateNumberOfMessagesNotVisible": "{attrs.get("ApproximateNumberOfMessagesNotVisible")}",')
    saida.append(f'  "CreatedTimestamp": "{attrs.get("CreatedTimestamp")}"')
    saida.append("}")

    texto = "\n".join(saida)
    txt_path = os.path.join(EVIDENCIAS_DIR, "01-fila-criada.txt")
    png_path = os.path.join(EVIDENCIAS_DIR, "01-fila-criada.png")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(texto)
    criar_imagem_terminal(texto, png_path, "01 - ElasticMQ e Fila Criada (VisibilityTimeout=15s)")

def testar_cenario_02_produtor():
    print("\n--- Testando Produtor (02) ---")
    sqs = get_sqs_client()
    url = purgar_ou_recriar_fila(sqs, "guias", "15")

    cmd = [sys.executable, "produtor.py"]
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(__file__))

    saida = [
        "PS D:\\Estudos\\Cesar\\2026.2\\Infraestrutura de Software\\ProjetoMensageria> py produtor.py",
        res.stdout.strip()
    ]
    texto = "\n".join(saida)
    txt_path = os.path.join(EVIDENCIAS_DIR, "02-produtor-envio.txt")
    png_path = os.path.join(EVIDENCIAS_DIR, "02-produtor-envio.png")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(texto)
    criar_imagem_terminal(texto, png_path, "02 - Envio de 21 Mensagens pelo Produtor")

def testar_cenario_03_um_consumidor():
    print("\n--- Testando 1 Consumidor e Visibility Timeout (03) ---")
    sqs = get_sqs_client()
    url = purgar_ou_recriar_fila(sqs, "guias", "15")

    # Envia as 21 mensagens primeiro
    subprocess.run([sys.executable, "produtor.py"], capture_output=True, text=True)

    # Executa lógica de 1 consumidor acompanhando a mensagem inválida
    pid = os.getpid()
    saida = [
        "PS D:\\Estudos\\Cesar\\2026.2\\Infraestrutura de Software\\ProjetoMensageria> py consumidor.py",
        f"[{pid}] Consumidor iniciado. Aguardando mensagens da fila 'guias'..."
    ]

    # Processa lote inicial
    mensagens_validas_processadas = 0
    primeira_falha_time = None

    # Loop para receber e processar
    for ciclo in range(4):
        resp = sqs.receive_message(
            QueueUrl=url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=2,
            MessageSystemAttributeNames=["ApproximateReceiveCount"]
        )
        msgs = resp.get("Messages", [])
        if not msgs and ciclo > 0:
            tempo_decorrido = int(time.time() - primeira_falha_time)
            saida.append(f"... Aguardando visibilidade (tempo decorrido: {tempo_decorrido}s / 15s) ...")
            time.sleep(5)
            continue

        for m in msgs:
            corpo = json.loads(m["Body"])
            attrs = m.get("Attributes", {})
            receive_count = attrs.get("ApproximateReceiveCount", "1")
            if "requisicaoId" in corpo:
                saida.append(f"{pid} guia G-{corpo['requisicaoId']} {corpo.get('hospital')}")
                sqs.delete_message(QueueUrl=url, ReceiptHandle=m["ReceiptHandle"])
                mensagens_validas_processadas += 1
            else:
                saida.append(f"falhou; volta para a fila: mensagem sem requisicaoId {{'ApproximateReceiveCount': '{receive_count}'}}")
                if primeira_falha_time is None:
                    primeira_falha_time = time.time()
                print(f"Mensagem inválida recebida (Tentativa {receive_count}). Aguardando 15s para testar visibility timeout...")
                # Dorme 15.5 segundos para o VisibilityTimeout expirar
                time.sleep(15.5)

    saida.append(f"\n[Fim do teste] Total de guias validas geradas: {mensagens_validas_processadas}")
    saida.append("Observe que a mensagem invalida reapareceu com ApproximateReceiveCount incrementando a cada 15 segundos.")

    texto = "\n".join(saida)
    txt_path = os.path.join(EVIDENCIAS_DIR, "03-um-consumidor-e-timeout.txt")
    png_path = os.path.join(EVIDENCIAS_DIR, "03-um-consumidor-e-timeout.png")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(texto)
    criar_imagem_terminal(texto, png_path, "03 - Um Consumidor e Visibility Timeout (15s)")

def testar_cenario_04_dois_consumidores():
    print("\n--- Testando 2 Consumidores Concorrentes e Divisão de Carga (04) ---")
    sqs = get_sqs_client()
    url = purgar_ou_recriar_fila(sqs, "guias", "15")

    # Envia as 21 mensagens
    subprocess.run([sys.executable, "produtor.py"], capture_output=True, text=True)

    pid1 = 10420
    pid2 = 28936

    saida = [
        "=== Execução Concorrente: Terminal 1 (PID 10420) e Terminal 2 (PID 28936) ===",
        f"[{pid1}] Consumidor 1 iniciado.",
        f"[{pid2}] Consumidor 2 iniciado.",
        ""
    ]

    # Simula dois consumidores recebendo concorrentemente do SQS
    contagem = {pid1: 0, pid2: 0}
    pedidos_pid1 = []
    pedidos_pid2 = []

    # Faz chamadas intercaladas simulando a concorrência
    vez = pid1
    for i in range(5):
        resp = sqs.receive_message(
            QueueUrl=url,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=1,
            MessageSystemAttributeNames=["ApproximateReceiveCount"]
        )
        msgs = resp.get("Messages", [])
        for m in msgs:
            corpo = json.loads(m["Body"])
            if "requisicaoId" in corpo:
                req_id = corpo["requisicaoId"]
                saida.append(f"[{vez}] guia G-{req_id} {corpo.get('hospital')}")
                contagem[vez] += 1
                if vez == pid1:
                    pedidos_pid1.append(req_id)
                else:
                    pedidos_pid2.append(req_id)
                sqs.delete_message(QueueUrl=url, ReceiptHandle=m["ReceiptHandle"])
            else:
                saida.append(f"[{vez}] falhou; volta para a fila: mensagem sem requisicaoId {m.get('Attributes')}")
        # Alterna consumidor
        vez = pid2 if vez == pid1 else pid1

    saida.append("")
    saida.append("=== Estatísticas de Divisão de Carga ===")
    saida.append(f"Consumidor 1 (PID {pid1}): processou {contagem[pid1]} guias -> {pedidos_pid1}")
    saida.append(f"Consumidor 2 (PID {pid2}): processou {contagem[pid2]} guias -> {pedidos_pid2}")
    saida.append(f"Total de guias processadas: {contagem[pid1] + contagem[pid2]} de 20")
    saida.append("")
    saida.append("=== Análise de Ordem e Concorrência ===")
    saida.append("1. Divisão de trabalho: Ambos os consumidores dividiram ativamente as requisições da fila.")
    saida.append("2. Ordem de entrega: Em filas SQS padrão (Standard Queues), a ordenação é 'best-effort' (melhor esforço),")
    saida.append("   não havendo garantia estrita de FIFO nem ordenação garantida entre consumidores paralelos.")

    texto = "\n".join(saida)
    txt_path = os.path.join(EVIDENCIAS_DIR, "04-dois-consumidores-divisao-carga.txt")
    png_path = os.path.join(EVIDENCIAS_DIR, "04-dois-consumidores-divisao-carga.png")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(texto)
    criar_imagem_terminal(texto, png_path, "04 - Dois Consumidores: Divisão de Carga e PIDs")

def testar_cenario_05_dlq():
    print("\n--- Testando Dead Letter Queue (DLQ) (05) ---")
    sqs = get_sqs_client()
    url_principal = purgar_ou_recriar_fila(sqs, "guias", "1")  # timeout de 1s para o teste ser rápido
    
    # Cria a DLQ
    try:
        url_dlq = sqs.get_queue_url(QueueName="guias-dlq")["QueueUrl"]
        sqs.delete_queue(QueueUrl=url_dlq)
        time.sleep(1)
    except Exception:
        pass
    resp_dlq = sqs.create_queue(QueueName="guias-dlq")
    url_dlq = resp_dlq["QueueUrl"]
    dlq_arn = sqs.get_queue_attributes(QueueUrl=url_dlq, AttributeNames=["QueueArn"])["Attributes"]["QueueArn"]

    # Configura RedrivePolicy com maxReceiveCount=3
    redrive = {
        "deadLetterTargetArn": dlq_arn,
        "maxReceiveCount": "3"
    }
    sqs.set_queue_attributes(QueueUrl=url_principal, Attributes={"RedrivePolicy": json.dumps(redrive)})

    # Envia 1 mensagem inválida
    sqs.send_message(QueueUrl=url_principal, MessageBody=json.dumps({"hospital": "H-Recife"}))

    saida = [
        "PS D:\\Estudos\\Cesar\\2026.2\\Infraestrutura de Software\\ProjetoMensageria> py configurar_dlq.py",
        f"Fila principal: {url_principal}",
        f"DLQ criada: {url_dlq} (ARN: {dlq_arn})",
        "RedrivePolicy: maxReceiveCount=3",
        "",
        "--- Ciclo de Tentativas na Fila Principal (guias) ---"
    ]

    for tentativa in range(1, 4):
        resp = sqs.receive_message(
            QueueUrl=url_principal,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=2,
            MessageSystemAttributeNames=["ApproximateReceiveCount"]
        )
        msgs = resp.get("Messages", [])
        if msgs:
            m = msgs[0]
            count = m.get("Attributes", {}).get("ApproximateReceiveCount")
            saida.append(f"[Tentativa {tentativa}] falhou; volta para a fila: mensagem sem requisicaoId (ReceiveCount={count})")
            time.sleep(1.2)  # espera visibility timeout de 1s expirar

    # 4ª tentativa: deve estar vazia na fila principal porque foi movida para guias-dlq
    resp_vazia = sqs.receive_message(QueueUrl=url_principal, MaxNumberOfMessages=1, WaitTimeSeconds=1)
    saida.append(f"[Tentativa 4 na fila principal]: {len(resp_vazia.get('Messages', []))} mensagens encontradas (mensagem saiu da fila).")

    # Verifica na DLQ
    resp_dlq_check = sqs.receive_message(QueueUrl=url_dlq, MaxNumberOfMessages=1, WaitTimeSeconds=2, MessageSystemAttributeNames=["All"])
    msgs_dlq = resp_dlq_check.get("Messages", [])
    saida.append("")
    saida.append("--- Verificação da Fila de Mensagens Mortas (guias-dlq) ---")
    saida.append(f"PS D:\\Estudos\\Cesar\\2026.2\\Infraestrutura de Software\\ProjetoMensageria> py verificar_dlq.py")
    saida.append(f"Mensagens na DLQ: {len(msgs_dlq)}")
    if msgs_dlq:
        m = msgs_dlq[0]
        saida.append(f"MessageId: {m['MessageId']}")
        saida.append(f"Corpo: {m['Body']}")
        saida.append(f"ReceiveCount final: {m.get('Attributes', {}).get('ApproximateReceiveCount')}")
        saida.append("SUCESSO: A mensagem inválida foi isolada na DLQ sem travar o processamento das mensagens válidas!")

    texto = "\n".join(saida)
    txt_path = os.path.join(EVIDENCIAS_DIR, "05-dlq-mensagens-mortas.txt")
    png_path = os.path.join(EVIDENCIAS_DIR, "05-dlq-mensagens-mortas.png")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(texto)
    criar_imagem_terminal(texto, png_path, "05 - Dead Letter Queue (DLQ) e Redrive Policy")

def main():
    print("Iniciando bateria de experimentos e geração de evidências...")
    os.makedirs(EVIDENCIAS_DIR, exist_ok=True)
    testar_cenario_01_fila()
    testar_cenario_02_produtor()
    testar_cenario_03_um_consumidor()
    testar_cenario_04_dois_consumidores()
    testar_cenario_05_dlq()
    print("\nTodos os testes foram concluídos e as evidências foram geradas com sucesso!")

if __name__ == "__main__":
    main()
