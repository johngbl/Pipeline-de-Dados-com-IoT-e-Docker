import os
import re
try:
	import streamlit as st
	import pandas as pd
	import plotly.express as px
	from sqlalchemy import create_engine, text
except Exception:
	st = None
	pd = None
	px = None
	create_engine = None
	text = None

try:
	from dotenv import load_dotenv
except Exception:
	load_dotenv = None

if load_dotenv is not None:
	load_dotenv()

def build_db_url() -> str:
	db_url = os.getenv('DATABASE_URL')
	if db_url:
		return db_url
	user = os.getenv('PGUSER', 'postgres')
	password = os.getenv('PGPASSWORD', '')
	host = os.getenv('PGHOST', 'localhost')
	port = os.getenv('PGPORT', '5432')
	db = os.getenv('PGDATABASE', 'iot_db')
	if password:
		return f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}'
	return f'postgresql+psycopg2://{user}@{host}:{port}/{db}'

DB_URL = build_db_url()
engine = None
if create_engine is not None:
	try:
		engine = create_engine(DB_URL)
	except Exception:
		engine = None

def load_data(view_name):
	if pd is None:
		raise RuntimeError('Pandas não está disponível. Instale dependências com pip install -r requirements.txt')
	if engine is None:
		raise RuntimeError('Conexão com banco não configurada. Defina DATABASE_URL ou instale driver adequado.')
	if not isinstance(view_name, str) or not re.match(r'^[A-Za-z0-9_]+$', view_name):
		raise ValueError('Nome de view inválido')
	return pd.read_sql(text(f'SELECT * FROM {view_name}'), engine)

if st is None:
	print('Dependências para o dashboard (streamlit/plotly/pandas/sqlalchemy) não estão instaladas no ambiente atual.')
else:
	st.title('Dashboard de Temperaturas IoT')
	st.caption(f'Conectado em: {DB_URL.split("@")[-1] if "@" in DB_URL else "DATABASE_URL"}')

	st.header('Média de Temperatura por Dispositivo')
	df_avg_temp = load_data('avg_temp_por_dispositivo')
	if not df_avg_temp.empty:
		fig1 = px.bar(df_avg_temp, x='device_id', y='avg_temp')
		st.plotly_chart(fig1)
	else:
		st.write('Nenhum dado em avg_temp_por_dispositivo.')

	st.header('Temperaturas Máximas e Mínimas por Dia')
	df_temp_stats = load_data('temp_stats_por_dia')
	if not df_temp_stats.empty:
		fig3 = px.line(df_temp_stats, x='date', y=['min_temp', 'max_temp'])
		st.plotly_chart(fig3)
	else:
		st.write('Nenhum dado em temp_stats_por_dia.')

	st.header('Contagem In/Out por Sala')
	df_in_out = load_data('in_out_ratio_por_room')
	if not df_in_out.empty:
		fig2 = px.bar(df_in_out, x='room_id', y=['in_count', 'out_count'])
		st.plotly_chart(fig2)
	else:
		st.write('Nenhum dado em in_out_ratio_por_room.')
