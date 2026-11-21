import json
import os
import sys
import boto3

# Conexão com o serviço SQS (ElasticMQ local na porta 9324 ou AWS SQS)
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

def processar(pedido):
    """
    Processa a requisição do Rota Vital.
    Lança ValueError caso a mensagem seja inválida (sem requisicaoId).
    """
    if "requisicaoId" not in pedido:
        raise ValueError("mensagem sem requisicaoId")
    print(pid, "guia G-" + pedido["requisicaoId"], pedido.get("hospital"), flush=True)

print(f"[{pid}] Consumidor iniciado. Aguardando mensagens da fila 'guias'...", flush=True)

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
                processar(json.loads(m["Body"]))
                # A mensagem só sai da fila quando o consumidor confirma e apaga
                sqs.delete_message(QueueUrl=url, ReceiptHandle=m["ReceiptHandle"])
            except Exception as e:
                # Falha: a mensagem NÃO é apagada. O SQS a tornará visível novamente após o VisibilityTimeout.
                print("falhou; volta para a fila:", e, m.get("Attributes"), flush=True)
except KeyboardInterrupt:
    print(f"\n[{pid}] Consumidor encerrado pelo usuário.", flush=True)
