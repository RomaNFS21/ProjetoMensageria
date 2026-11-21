@echo off
echo Iniciando ElasticMQ local...
where docker >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Docker detectado. Iniciando via Docker...
    docker run --rm -p 9324:9324 softwaremill/elasticmq-native
) else (
    echo Docker nao encontrado. Iniciando via Java standalone...
    if exist "elasticmq\elasticmq-server.jar" (
        java -jar elasticmq\elasticmq-server.jar
    ) else (
        echo Arquivo elasticmq\elasticmq-server.jar nao encontrado!
        pause
    )
)
