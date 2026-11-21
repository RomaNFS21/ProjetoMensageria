"""
Script para configurar Dead Letter Queue (DLQ) para a fila 'guias'.
Após 3 tentativas com falha (maxReceiveCount=3), a mensagem inválida
é automaticamente movida para a fila 'guias-dlq'.
"""

import boto3
import json
import os
import sys

endpoint_url = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:9324")
region_name = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "x")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "x")

def configurar_dlq():
    sqs = boto3.client(
        "sqs",
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    print(f"Conectando ao SQS em {endpoint_url}...")

    # 1. Obter ou criar a fila principal 'guias'
    try:
        url_principal = sqs.get_queue_url(QueueName="guias")["QueueUrl"]
    except sqs.exceptions.QueueDoesNotExist:
        resp = sqs.create_queue(QueueName="guias", Attributes={"VisibilityTimeout": "15"})
        url_principal = resp["QueueUrl"]
        print("Fila 'guias' criada.")

    # 2. Criar a fila de mensagens mortas 'guias-dlq'
    try:
        url_dlq = sqs.get_queue_url(QueueName="guias-dlq")["QueueUrl"]
        print(f"DLQ 'guias-dlq' já existe: {url_dlq}")
    except sqs.exceptions.QueueDoesNotExist:
        resp_dlq = sqs.create_queue(QueueName="guias-dlq")
        url_dlq = resp_dlq["QueueUrl"]
        print(f"DLQ 'guias-dlq' criada: {url_dlq}")

    # 3. Obter o ARN da DLQ
    dlq_attrs = sqs.get_queue_attributes(QueueUrl=url_dlq, AttributeNames=["QueueArn"])
    dlq_arn = dlq_attrs["Attributes"]["QueueArn"]
    print(f"ARN da DLQ: {dlq_arn}")

    # 4. Configurar RedrivePolicy na fila 'guias'
    redrive_policy = {
        "deadLetterTargetArn": dlq_arn,
        "maxReceiveCount": "3"
    }

    sqs.set_queue_attributes(
        QueueUrl=url_principal,
        Attributes={
            "RedrivePolicy": json.dumps(redrive_policy)
        }
    )

    print("RedrivePolicy configurada com sucesso na fila 'guias'!")
    print(f"Mensagens com falha serão enviadas para 'guias-dlq' após 3 tentativas.")

if __name__ == "__main__":
    configurar_dlq()
