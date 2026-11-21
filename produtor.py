import json
import os
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

print("Iniciando publicação de mensagens na fila 'guias'...")

# Publica 20 pedidos válidos
for i in range(1, 21):
    pedido = {"requisicaoId": f"R-{i:03d}", "hospital": "H-Recife"}
    sqs.send_message(QueueUrl=url, MessageBody=json.dumps(pedido))
    print(f"Enviado: R-{i:03d}")

# Publica 1 pedido inválido (sem requisicaoId)
sqs.send_message(QueueUrl=url, MessageBody=json.dumps({"hospital": "H-Recife"}))
print("Enviado pedido inválido (sem requisicaoId)")

print("21 mensagens enviadas")
