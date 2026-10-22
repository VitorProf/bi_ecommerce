
"""
Automação dos pipelines de ingestão — BI E-commerce

Executa sequencialmente os notebooks Jupyter:
1. Logística
2. SQL Server
3. MongoDB
4. API BACEN — atualização diária

Registra os resultados em logs e interrompe
a execução caso algum notebook apresente erro.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


# 1. DEFINIR PASTA DO PROJETO

pasta_projeto = Path(__file__).resolve().parent

pasta_logs = pasta_projeto / "logs"
pasta_logs.mkdir(exist_ok=True)


# 2. DEFINIR PIPELINES DIÁRIOS

pipelines = [
    "01_ingestao_logistica_cod_unico.ipynb",
    "02_ingestao_sqlserver_cod_unico.ipynb",
    "03_ingestao_mongodb_cod_unico.ipynb",
    "04_api_bacen_diario_cod_unico.ipynb"
]


# 3. DEFINIR ARQUIVO DE LOG

data_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")
arquivo_log = pasta_logs / f"execucao_{data_execucao}.log"


def registrar(mensagem):
    """Exibe a mensagem e registra no arquivo de log."""

    print(mensagem, flush=True)

    with open(arquivo_log, "a", encoding="utf-8") as arquivo:
        arquivo.write(mensagem + "\n")


# 4. EXECUTAR PIPELINES

registrar("=" * 60)
registrar("INÍCIO DA EXECUÇÃO DOS PIPELINES")
registrar(f"Data: {datetime.now():%d/%m/%Y %H:%M:%S}")
registrar("=" * 60)

sucessos = 0
erros = 0

for notebook in pipelines:

    registrar(f"\nIniciando: {notebook}")

    inicio = datetime.now()

    caminho_notebook = pasta_projeto / notebook

    if not caminho_notebook.is_file():
        registrar(f"ERRO: Notebook não encontrado: {notebook}")
        erros += 1
        break

    comando = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(caminho_notebook),
        "--output",
        f"{caminho_notebook.stem}_executado.ipynb",
        "--output-dir",
        str(pasta_logs),
    ]

    resultado = subprocess.run(
        comando,
        cwd=pasta_projeto,
        capture_output=True,
        text=True
    )

    if resultado.returncode == 0:
        registrar(f"SUCESSO: {notebook}")
        sucessos += 1
    else:
        registrar(f"ERRO: {notebook}")
        registrar(resultado.stdout)
        registrar(resultado.stderr)
        erros += 1

    duracao = datetime.now() - inicio
    registrar(f"Duração: {duracao}")

    if erros > 0:
        registrar("Execução interrompida devido ao erro.")
        break


# 5. RESUMO FINAL

registrar("\n" + "=" * 60)
registrar("RESUMO DA EXECUÇÃO")
registrar(f"Notebooks concluídos: {sucessos}")
registrar(f"Notebooks com erro: {erros}")
registrar(f"Término: {datetime.now():%d/%m/%Y %H:%M:%S}")
registrar("=" * 60)

if erros > 0:
    sys.exit(1)

sys.exit(0)
