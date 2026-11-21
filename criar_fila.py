"""
Script para criação da fila 'guias' com VisibilityTimeout de 15 segundos.
Compatível com ElasticMQ local (localhost:9324) e Amazon SQS.
"""

import boto3
import sys

def criar_fila():
    endpoint_url = "http://localhost:9324"
    region = "us-east-1"
    
    print(f"Conectando ao serviço SQS em {endpoint_url}...")
    sqs = boto3.client(
        "sqs",
        endpoint_url=endpoint_url,
        region_name=region,
        aws_access_key_id="x",
        aws_secret_access_key="x"
    )

    nome_fila = "guias"
    visibilidade_timeout = "15"  # 15 segundos conforme especificado

    try:
        # Verifica se já existe
        try:
            url_existente = sqs.get_queue_url(QueueName=nome_fila)["QueueUrl"]
            print(f"A fila '{nome_fila}' já existe: {url_existente}")
            
            # Obtém atributos da fila existente
            attrs = sqs.get_queue_attributes(QueueUrl=url_existente, AttributeNames=["All"])["Attributes"]
            print(f"Atributos da fila:")
            print(f" - VisibilityTimeout: {attrs.get('VisibilityTimeout')}s")
            print(f" - ApproximateNumberOfMessages: {attrs.get('ApproximateNumberOfMessages')}")
            return url_existente
        except sqs.exceptions.QueueDoesNotExist:
            pass

        print(f"Criando fila '{nome_fila}' com VisibilityTimeout={visibilidade_timeout}s...")
        resp = sqs.create_queue(
            QueueName=nome_fila,
            Attributes={
                "VisibilityTimeout": visibilidade_timeout
            }
        )
        url = resp["QueueUrl"]
        print(f"Fila '{nome_fila}' criada com sucesso!")
        print(f"QueueUrl: {url}")
        return url

    except Exception as e:
        print(f"Erro ao conectar ou criar fila: {e}", file=sys.stderr)
        print("Certifique-se de que o ElasticMQ está em execução na porta 9324.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    criar_fila()
