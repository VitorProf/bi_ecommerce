# BI E-commerce | Engenharia de Dados

**Projeto de integração de dados com Python, SQL Server, MongoDB, APIs REST e Azure Data Lake Storage.**

## 1. Visão geral

Este projeto simula um ambiente de dados de uma empresa de comércio eletrônico que precisa integrar informações provenientes de diferentes sistemas para apoiar análises operacionais e decisões de negócio.

Em um cenário empresarial, dados comerciais, logísticos, comportamentais e financeiros podem estar distribuídos em bancos relacionais, bancos NoSQL, arquivos e serviços externos.

O desafio é desenvolver processos capazes de extrair, validar, organizar e armazenar essas informações de maneira consistente, preparando-as para utilização em soluções de Business Intelligence.

O projeto está sendo desenvolvido de forma incremental, começando pela ingestão de dados e evoluindo para práticas de Engenharia de Dados, como tratamento de erros, rastreabilidade, cargas incrementais e organização em camadas.

### Objetivos

- Integrar dados provenientes de fontes heterogêneas.
- Desenvolver pipelines de ingestão utilizando Python.
- Utilizar o Azure Data Lake como repositório central.
- Implementar validações e tratamento de falhas.
- Trabalhar com arquivos CSV, JSON e Parquet.
- Explorar cargas históricas e atualizações incrementais.
- Preparar os dados para futuras transformações analíticas e dashboards.

## 2. Cenário de negócio

A empresa fictícia possui diferentes fontes de informações:

| Área | Fonte | Informações |
|---|---|---|
| Comercial | SQL Server | Clientes, produtos, pedidos e pagamentos |
| Comportamento digital | MongoDB | Eventos de navegação e interação no site |
| Logística | Arquivos CSV | Registros de entregas |
| Indicadores econômicos | API BACEN | Cotações do dólar |

A integração dessas informações permitirá, em etapas futuras, responder a questões como:

- Qual é o desempenho das vendas por período?
- Quais produtos apresentam maior demanda?
- Como está o desempenho das entregas?
- Como os clientes interagem com o comércio eletrônico?
- Como indicadores econômicos podem complementar análises financeiras?

Essas análises representam possibilidades de evolução do projeto, não dashboards já implementados.

## 3. Tecnologias

| Tecnologia | Finalidade |
|---|---|
| Python | Desenvolvimento dos pipelines |
| Pandas | Manipulação, consolidação e validação de dados |
| SQL Server | Fonte relacional |
| SQLAlchemy / PyODBC | Conexão e consultas SQL |
| MongoDB / PyMongo | Extração de dados NoSQL |
| Requests | Consumo de APIs REST |
| Azure Data Lake Storage | Armazenamento em nuvem |
| Azure Storage SDK | Operações com arquivos e containers |
| PyArrow | Serialização em formato Parquet |
| Jupyter Notebook | Desenvolvimento e testes |
| python-dotenv | Configuração de credenciais |
| Git / GitHub | Controle de versões |

## 4. Arquitetura da solução

A arquitetura organiza a ingestão de dados a partir de diferentes fontes, com armazenamento centralizado no Azure Data Lake.

```text
                  FONTES DE DADOS
                         |
       +-----------------+-----------------+
       |                 |                 |
   SQL Server         MongoDB          Arquivos CSV
   E-commerce       Eventos do site     Logística
       |                 |                 |
       +-----------------+-----------------+
                         |
                      Python
                         |
                         v
                 AZURE DATA LAKE
                         |
                +--------+--------+
                |                 |
             Landing            Bronze
           Recebimento        Dados ingeridos
           e validação        e armazenados
                |                 ^
                +-----------------+

   API BACEN --------> Python --------> Bronze

              EVOLUÇÃO PLANEJADA
                         |
                       Silver
               Limpeza e padronização
                         |
                        Gold
               Modelagem e indicadores
                         |
                      Power BI
```

A camada Landing é utilizada no fluxo de arquivos logísticos. Os demais pipelines possuem processos específicos de ingestão na Bronze.

As camadas Silver e Gold e a integração analítica com Power BI fazem parte da evolução planejada.

## 5. Pipelines desenvolvidos

### 5.1. Ingestão de dados logísticos

**Fonte:** arquivos CSV locais.

**Objetivo:** receber arquivos de entregas, validar seu conteúdo e armazenar os arquivos aceitos no Azure Data Lake.

Fluxo de processamento:

1. Identificar arquivos CSV disponíveis no diretório local.
2. Enviar os arquivos para a Landing.
3. Verificar se os arquivos possuem conteúdo e registros.
4. Identificar o ano a partir do nome do arquivo.
5. Enviar arquivos válidos para a Bronze, organizados por ano.
6. Registrar logs de sucesso ou erro.
7. Remover da Landing os arquivos processados com sucesso.
8. Mover os arquivos locais processados para a pasta de enviados.

Arquivos inválidos permanecem disponíveis para correção e reprocessamento.

**Exemplo de organização:**

```text
landing/
└── logistica/
    ├── entrada/
    ├── processados/
    └── erros/

bronze/
└── logistica/
    ├── 2025/
    └── 2026/
```

**Decisões técnicas:**

- Utilização da Landing como área intermediária de recebimento.
- Processamento individual dos arquivos para permitir tratamento independente de falhas.
- Geração de logs JSON para registrar resultados.
- Verificação de arquivos existentes na Bronze para evitar substituições indevidas.
- Preservação dos arquivos inválidos para análise.

**Limitação atual:** a validação contempla verificações básicas do CSV. A validação de esquema, tipos de dados e regras de negócio ainda poderá ser ampliada.

### 5.2. Ingestão de dados do SQL Server

**Fonte:** banco de dados relacional de e-commerce.

**Objetivo:** extrair informações estruturadas utilizando Python e consultas SQL.

O pipeline utiliza SQLAlchemy e PyODBC para estabelecer a conexão e Pandas para manipular os resultados.

Os notebooks apresentam o processo de conexão, consulta e ingestão de dados.

**Decisão técnica:** utilizar ferramentas compatíveis com SQL Server, permitindo separar o acesso à fonte da manipulação dos dados em Python.

### 5.3. Ingestão de dados do MongoDB

**Fonte:** coleção de eventos de navegação do e-commerce.

**Objetivo:** extrair dados semiestruturados e prepará-los para armazenamento analítico.

O processo contempla:

- Conexão com MongoDB utilizando PyMongo.
- Leitura dos documentos da coleção.
- Conversão dos resultados para DataFrame.
- Tratamento de campos incompatíveis com serialização direta, como o identificador `_id`.
- Conversão para Parquet.
- Envio ao Azure Data Lake.

**Decisão técnica:** utilizar Parquet como formato de armazenamento, facilitando a leitura por ferramentas analíticas e oferecendo compressão e armazenamento colunar.

### 5.4. API BACEN — Carga histórica

**Fonte:** API PTAX do Banco Central do Brasil.

**Objetivo:** consultar um intervalo histórico de cotações do dólar e armazenar os resultados localmente e na nuvem.

Etapas:

1. Definir o período de consulta.
2. Consumir a API REST.
3. Converter o JSON retornado para DataFrame.
4. Salvar os dados em CSV local.
5. Converter os dados para Parquet.
6. Enviar o arquivo histórico para a Bronze.

**Decisão técnica:** separar a carga histórica inicial da rotina de atualização diária, evitando consultar repetidamente todo o período na API.

### 5.5. API BACEN — Atualização diária

**Objetivo:** incorporar novas cotações ao histórico existente.

O processo foi estruturado para:

1. Consultar a cotação da data atual.
2. Selecionar a última cotação disponível.
3. Recuperar o histórico armazenado na Bronze.
4. Consolidar os dados.
5. Tratar duplicidades conforme a regra definida.
6. Atualizar o CSV local.
7. Regravar o histórico Parquet na Bronze.

**Decisão técnica:** manter um único arquivo histórico atualizado, em vez de criar um novo arquivo para cada execução diária.

Essa escolha simplifica o consumo dos dados para o volume atual.

**Limitações atuais:**

- O processo regrava o Parquet histórico completo.
- A seleção da última cotação disponível não garante o fechamento oficial se executada antes da publicação final.
- Uma execução perdida pode exigir recuperação manual de datas.
- A regra de deduplicação por data deve ser avaliada conforme a necessidade de preservar todas as cotações ou somente uma por dia.

## 6. Estrutura do repositório

```text
bi_ecommerce/
|
├── 01_ingestao_logistica.ipynb
├── 01_ingestao_logistica_cod_unico.ipynb
|
├── 02_ingestao_sqlserver.ipynb
├── 02_ingestao_sqlserver_cod_unico.ipynb
|
├── 03_ingestao_mongodb.ipynb
├── 03_ingestao_mongodb_cod_unico.ipynb
|
├── 04_api_bacen_hist.ipynb
├── 04_api_bacen_diario.ipynb
|
├── requirements.txt
├── .gitignore
└── README.md
```

Os notebooks com sufixo `_cod_unico` apresentam versões consolidadas dos respectivos processos.

O diretório local `data/` não é versionado.

## 7. Instalação e configuração

### Pré-requisitos

- Python compatível com as dependências do projeto.
- Acesso às fontes de dados utilizadas.
- SQL Server e MongoDB disponíveis para os pipelines correspondentes.
- Conta Azure com acesso ao Data Lake Storage.
- Ambiente Jupyter ou PyCharm.

### Instalar dependências

Clone o repositório:

```bash
git clone URL_DO_REPOSITORIO
cd bi_ecommerce
```

Crie e ative o ambiente virtual no Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

### Configurar credenciais

Crie um arquivo `.env` na raiz do projeto.

Exemplo:

```dotenv
AZURE_STORAGE_CONNECTION_STRING=sua_connection_string
```

Configure as demais conexões conforme os notebooks e os serviços utilizados.

O arquivo `.env` está incluído no `.gitignore` e não deve ser publicado.

## 8. Execução dos pipelines

Os pipelines estão organizados por fonte de dados e podem ser executados individualmente.

| Notebook | Processo |
|---|---|
| `01_ingestao_logistica.ipynb` | Ingestão de arquivos logísticos |
| `02_ingestao_sqlserver.ipynb` | Extração de dados relacionais |
| `03_ingestao_mongodb.ipynb` | Extração de eventos NoSQL |
| `04_api_bacen_hist.ipynb` | Carga histórica do BACEN |
| `04_api_bacen_diario.ipynb` | Atualização do histórico BACEN |

**Ordem recomendada para o BACEN:** executar primeiro a carga histórica e, posteriormente, a atualização diária.

Os outros pipelines dependem da disponibilidade das respectivas fontes e não exigem uma ordem única de execução.

## 9. Qualidade, rastreabilidade e confiabilidade

O projeto já explora alguns mecanismos importantes de Engenharia de Dados:

| Prática | Aplicação atual |
|---|---|
| Validação | Verificações básicas de arquivos logísticos |
| Tratamento de falhas | Identificação e registro de arquivos inválidos |
| Rastreabilidade | Logs JSON do processamento logístico |
| Controle de duplicidade | Regras de atualização do histórico BACEN |
| Controle de sobrescrita | Verificações de arquivos existentes na Bronze |
| Segurança | Credenciais externas ao código, por meio de `.env` |
| Versionamento | Git e GitHub |

Esses mecanismos representam uma implementação inicial. Monitoramento centralizado, testes automatizados, alertas e recuperação automática de falhas ainda não fazem parte de uma solução completa.

## 10. Resultados e evidências

Os pipelines permitem demonstrar:

- Integração com fontes relacionais, NoSQL, arquivos e APIs.
- Armazenamento de dados no Azure Data Lake.
- Conversão de dados para Parquet.
- Processamento e organização de arquivos logísticos.
- Registro de sucessos e falhas de ingestão.
- Atualização de um histórico econômico em dois formatos.

Os volumes processados, capturas de execução e métricas de desempenho poderão ser acrescentados após validação dos resultados finais dos notebooks.

## 11. Limitações conhecidas

O projeto encontra-se em desenvolvimento e apresenta limitações que orientarão suas próximas versões:

- Execução predominantemente manual dos notebooks.
- Ausência de testes automatizados abrangentes.
- Validação de dados ainda limitada em alguns pipelines.
- Ausência de monitoramento centralizado e alertas.
- Necessidade de melhorar a recuperação de cargas perdidas.
- Ausência de consolidação definitiva nas camadas Silver e Gold.

## 12. Próximas etapas

**Evolução dos pipelines**

- Aprimorar validações de esquema e regras de negócio.
- Implementar testes automatizados.
- Melhorar idempotência e reprocessamento.
- Adicionar mecanismos de recuperação de falhas.
- Implementar logs e métricas padronizados.

**Evolução da arquitetura**

- Construir a camada Silver para tratamento e padronização.
- Desenvolver a camada Gold com dados consolidados.
- Criar modelos analíticos e indicadores de negócio.
- Integrar os dados ao Power BI.
- Avaliar a orquestração e automação dos pipelines.

## 13. Considerações finais

O projeto BI E-commerce foi concebido como um ambiente prático de desenvolvimento em Engenharia de Dados.

Seu foco não é apenas conectar tecnologias, mas compreender as decisões envolvidas na construção de pipelines: como receber dados, validar arquivos, tratar falhas, armazenar informações, atualizar históricos e preparar fontes heterogêneas para análise.

A implementação será aprimorada progressivamente, acompanhando a evolução dos requisitos técnicos e das necessidades de negócio.

---

**Status:** em desenvolvimento.

**Áreas de aplicação:** Engenharia de Dados, Integração de Dados e Business Intelligence.