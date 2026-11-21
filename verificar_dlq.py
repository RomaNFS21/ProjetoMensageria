"""
Script para inspecionar mensagens mortas na fila 'guias-dlq'.
"""

import boto3
import json
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

try:
    url_dlq = sqs.get_queue_url(QueueName="guias-dlq")["QueueUrl"]
    attrs = sqs.get_queue_attributes(QueueUrl=url_dlq, AttributeNames=["All"])["Attributes"]
    print("=== Status da Fila de Mensagens Mortas (guias-dlq) ===")
    print(f"URL: {url_dlq}")
    print(f"Mensagens disponíveis na DLQ: {attrs.get('ApproximateNumberOfMessages')}")
    print(f"Mensagens em voo (in-flight): {attrs.get('ApproximateNumberOfMessagesNotVisible')}")

    resp = sqs.receive_message(
        QueueUrl=url_dlq,
        MaxNumberOfMessages=10,
        WaitTimeSeconds=2,
        MessageSystemAttributeNames=["All"]
    )
    
    msgs = resp.get("Messages", [])
    if msgs:
        print(f"\nEncontrada(s) {len(msgs)} mensagem(ns) morta(s):")
        for i, m in enumerate(msgs, 1):
            print(f"\n--- Mensagem {i} ---")
            print(f"MessageId: {m['MessageId']}")
            print(f"Corpo: {m['Body']}")
            print(f"ApproximateReceiveCount: {m.get('Attributes', {}).get('ApproximateReceiveCount')}")
    else:
        print("\nNenhuma mensagem recebida na DLQ no momento.")

except sqs.exceptions.QueueDoesNotExist:
    print("A fila 'guias-dlq' ainda não foi criada. Execute 'configurar_dlq.py'.")
