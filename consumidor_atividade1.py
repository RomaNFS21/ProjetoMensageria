"""
Consumidor alternativo (opcional) que integra diretamente com a função
Serverless (Lambda handler) da Atividade 1 (Rota Vital).
"""

import json
import os
import sys
import boto3

# Adiciona o diretório do ProjetoServerLess ao sys.path para importar a função lambda_handler
caminho_atividade1 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ProjetoServerLess", "hello_world"))
if caminho_atividade1 not in sys.path:
    sys.path.insert(0, caminho_atividade1)

try:
    from app import lambda_handler
    print("Função lambda_handler da Atividade 1 importada com sucesso!")
except ImportError:
    # Fallback caso a pasta da Atividade 1 não esteja no caminho padrão
    def lambda_handler(event, context):
        pedido = json.loads(event.get("body") or "{}")
        if "requisicaoId" not in pedido:
            return {"statusCode": 400, "body": json.dumps({"erro": "requisicaoId obrigatório"})}
        guia = {"guia": "G-" + pedido["requisicaoId"], "hospital": pedido.get("hospital")}
        return {"statusCode": 201, "body": json.dumps(guia)}

endpoint_url = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:9324")
region_name = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "x")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "x")

sqs = boto3.client(
    "sqs",
    endpoint_url=endpoint_url,
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

url = sqs.get_queue_url(QueueName="guias")["QueueUrl"]
pid = os.getpid()

def processar_via_atividade1(corpo_mensagem):
    """
    Simula a invocação do Lambda da Atividade 1 com o evento SQS.
    """
    evento = {"body": corpo_mensagem}
    resposta = lambda_handler(evento, None)
    
    if resposta["statusCode"] >= 400:
        detalhes = json.loads(resposta["body"])
        raise ValueError(f"Lambda retornou erro {resposta['statusCode']}: {detalhes.get('erro')}")
    
    dados_guia = json.loads(resposta["body"])
    print(pid, "guia " + dados_guia["guia"], dados_guia.get("hospital"), flush=True)

print(f"[{pid}] Consumidor Atividade 1 iniciado. Aguardando mensagens...", flush=True)

try:
    while True:
        resp = sqs.receive_message(
            QueueUrl=url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=10,
            MessageSystemAttributeNames=["ApproximateReceiveCount"]
        )
        for m in resp.get("Messages", []):
            try:
                processar_via_atividade1(m["Body"])
                sqs.delete_message(QueueUrl=url, ReceiptHandle=m["ReceiptHandle"])
            except Exception as e:
                print("falhou; volta para a fila:", e, m.get("Attributes"), flush=True)
except KeyboardInterrupt:
    print(f"\n[{pid}] Consumidor encerrado.", flush=True)
