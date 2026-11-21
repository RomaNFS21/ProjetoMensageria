"""
Script para purgar/limpar as mensagens das filas 'guias' e 'guias-dlq'.
"""

import boto3
import os

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

for fila in ["guias", "guias-dlq"]:
    try:
        url = sqs.get_queue_url(QueueName=fila)["QueueUrl"]
        sqs.purge_queue(QueueUrl=url)
        print(f"Fila '{fila}' purgada com sucesso.")
    except sqs.exceptions.QueueDoesNotExist:
        pass
    except Exception as e:
        print(f"Aviso ao purgar '{fila}': {e}")
