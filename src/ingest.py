#!/usr/bin/env python3
from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
try:
    from sqlalchemy.dialects.postgresql import insert as pg_insert
except Exception:
    pg_insert = None

load_dotenv()

DB_URL = os.getenv('DATABASE_URL')
if not DB_URL:
    user = os.getenv('PGUSER', 'postgres')
    password = os.getenv('PGPASSWORD', '')
    host = os.getenv('PGHOST', 'localhost')
    port = os.getenv('PGPORT', '5432')
    db = os.getenv('PGDATABASE', 'iot_db')
    if password:
        DB_URL = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}'
    else:
        DB_URL = f'postgresql+psycopg2://{user}@{host}:{port}/{db}'

if not DB_URL:
    DB_URL = 'sqlite:///iot_temp.db'
    print('Using sqlite fallback at iot_temp.db')

engine = create_engine(DB_URL, echo=False, future=True)
Base = declarative_base()

class TemperatureReading(Base):
    __tablename__ = 'temperature_readings'
    id = Column(Integer, primary_key=True)
    source_id = Column(String, unique=True, index=True, nullable=False)
    room_id = Column(String)
    noted_date = Column(DateTime, nullable=False)
    temperature = Column(Float)
    in_out = Column(String)

def create_tables():
    Base.metadata.create_all(engine)

def read_and_prepare(csv_path):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={
        'id': 'source_id',
        'room_id/id': 'room_id',
        'noted_date': 'noted_date',
        'temp': 'temperature',
        'out/in': 'in_out'
    })
    df['noted_date'] = pd.to_datetime(df['noted_date'], dayfirst=True, errors='coerce', format='%d-%m-%Y %H:%M')
    df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
    df = df.dropna(subset=['source_id', 'noted_date'])
    df = df.drop_duplicates(subset=['source_id'])
    return df

def insert_records(df):
    Session = sessionmaker(bind=engine)
    session = Session()
    inserted = 0
    records = df.to_dict(orient='records')
    use_postgres_insert = engine.dialect.name == 'postgresql' and pg_insert is not None
    table = TemperatureReading.__table__
    if use_postgres_insert:
        with engine.begin() as conn:
            stmt = pg_insert(table).values(records)
            stmt = stmt.on_conflict_do_nothing(index_elements=['source_id'])
            conn.execute(stmt)
            print(f'Inserted {len(records)} records (postgres bulk insert on conflict do nothing).')
        return
    for rec in records:
        if isinstance(rec.get('noted_date'), pd.Timestamp):
            rec['noted_date'] = rec['noted_date'].to_pydatetime()
        obj = TemperatureReading(
            source_id=rec.get('source_id'),
            room_id=rec.get('room_id'),
            noted_date=rec.get('noted_date'),
            temperature=rec.get('temperature'),
            in_out=rec.get('in_out')
        )
        try:
            session.add(obj)
            session.commit()
            inserted += 1
        except IntegrityError:
            session.rollback()
            continue
    session.close()
    print(f'Inserted {inserted} new records (committed per-row).')

def main():
    here = os.path.dirname(__file__)
    csv_candidates = [
        os.path.join(here, '..', 'data', 'IOT-temp.csv'),
        os.path.join(here, 'IOT-temp.csv'),
    ]
    csv_path = next((p for p in csv_candidates if os.path.exists(p)), None)
    if not csv_path:
        print('CSV not found. Expected at data/IOT-temp.csv (preferred) or src/IOT-temp.csv.')
        return
    create_tables()
    df = read_and_prepare(csv_path)
    if df.empty:
        print('No valid rows to insert.')
        return
    insert_records(df)

if __name__ == '__main__':
    main()
