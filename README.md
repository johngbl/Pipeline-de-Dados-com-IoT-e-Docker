# Pipeline de Dados com IoT e Docker (CSV → PostgreSQL → Views → Streamlit)

## Contexto e objetivo
Este projeto implementa um **pipeline de dados** para leituras de temperatura (IoT), realizando:

- **Ingestão** de um CSV público (Kaggle) para **PostgreSQL**
- **Criação de 3 views SQL** para análises
- **Dashboard Streamlit** com gráficos interativos consumindo as views

## Estrutura do repositório
- **`src/`**: código (`ingest.py`, `dashboard.py`, `sql_views.sql`)
- **`data/`**: dataset local (`IOT-temp.csv`) *(não recomendado versionar em Git)*
- **`docs/`**: documentos e imagens (prints do dashboard, enunciado, etc.)

## Dataset (Kaggle)
Fonte: **Temperature Readings: IoT Devices**. Baixe o CSV e salve em `data/IOT-temp.csv`.

## Tecnologias
- Python, Pandas
- Docker (PostgreSQL)
- SQLAlchemy + psycopg2
- Streamlit + Plotly

## Pré-requisitos
- **Python 3.x**
- **Docker**
- **psql** (cliente do PostgreSQL) para aplicar o arquivo de views

## 1) Subir o PostgreSQL com Docker (`docker run`)
Crie um container PostgreSQL com banco `iot_db`:

```powershell
docker run --name postgres-iot `
  -e POSTGRES_PASSWORD=your_password `
  -e POSTGRES_DB=iot_db `
  -p 5432:5432 `
  -d postgres
```

Comandos úteis:

```powershell
docker ps
docker logs -f postgres-iot
docker stop postgres-iot
docker start postgres-iot
```

## 2) Ambiente Python e dependências
Criar e ativar ambiente virtual (PowerShell):

```powershell
cd "C:\Users\John\Desktop\Pipeline de Dados com IoT e Docker"
python -m venv venv
.\venv\Scripts\Activate
```

Instalar dependências:

```powershell
pip install -r requirements.txt
```

## 3) Configuração de variáveis (.env)
Copie `.env.example` para `.env` e ajuste as credenciais do PostgreSQL:

```powershell
Copy-Item .env.example .env
```

Variáveis suportadas:
- `DATABASE_URL` (opcional) **ou** `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`

## 4) Ingestão do CSV para o PostgreSQL
O script cria a tabela `temperature_readings` e insere os dados de `data/IOT-temp.csv` (preferido).

```powershell
python .\src\ingest.py
```

## 5) Criar/Recriar as views SQL
O arquivo de views é reaplicável (usa `DROP VIEW IF EXISTS`).

```powershell
psql -h $env:PGHOST -U $env:PGUSER -d $env:PGDATABASE -f .\src\sql_views.sql
```

## 6) Rodar o dashboard (Streamlit)

```powershell
streamlit run .\src\dashboard.py
```

## Views SQL (explicação e propósito)
- **`avg_temp_por_dispositivo`**: média de temperatura por `room_id` (tratado como “dispositivo/sala”) para comparar ambientes.
- **`temp_stats_por_dia`**: mínimo, máximo, média e total de leituras por dia (variação diária e comportamento geral).
- **`in_out_ratio_por_room`**: contagem de leituras `In` vs `Out` por sala e proporção `In` (perfil de origem das leituras).

## Capturas de tela do dashboard
Prints gerados durante a execução do Streamlit:

- Média de Temperatura por Dispositivo: `docs/Média de Temperatura por Dispositivo.png`
- Temperaturas Máximas e Mínimas por Dia: `docs/Temperaturas Máximas e Mínimas por Dia.png`
- Contagem In/Out por Sala: `docs/Contagem In_Out por Sala.png`

## Comandos Git utilizados (exemplos)
```bash
git init
git add .
git commit -m "Projeto inicial: Pipeline de Dados IoT"
git remote add origin URL_DO_SEU_REPOSITORIO
git push -u origin main
```
