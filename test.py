#!/usr/bin/env python3
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

def test_connection():
    # Replace with your actual credentials
    engine = create_engine('postgresql+psycopg2://postgres:1234@127.0.0.1:5432/ai_code_editor')

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()
            print("Connected to PostgreSQL version:", version[0])
    except OperationalError as e:
        print("Error connecting to PostgreSQL:", e)

if __name__ == '__main__':
    test_connection()