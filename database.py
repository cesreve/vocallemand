import psycopg2
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Get the database URL from environment variable
DATABASE_URL = st.secrets["my_database"]["DATABASE_URL"]

def connect_to_db():
    """Connects to PostgreSQL, creates a table, and queries it."""
    conn = None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def insert_answer(user_id, german_word, is_correct):
    """Inserts the user's answer into the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Create the answers table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL,
                german_word VARCHAR(255) NOT NULL,
                is_correct BOOLEAN,
                answer_date TIMESTAMP
            );
        """)

        # Insert the answer data
        cur.execute("""
            INSERT INTO answers (user_id, german_word, is_correct, answer_date)
            VALUES (%s, %s, %s, %s);
        """, (user_id, german_word, is_correct, datetime.now()))

        conn.commit()
        cur.close()
        conn.close()

    except psycopg2.Error as e:
        st.error(f"Database error: {e}")

def fetch_answers_from_db(user_id):
    """Récupère les réponses de l'utilisateur depuis la base de données."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT german_word, answer_date, is_correct
            FROM (
                SELECT 
                    german_word, 
                    answer_date, 
                    is_correct,
                    RANK() OVER (PARTITION BY german_word ORDER BY answer_date DESC) as rank_number
                FROM answers
                WHERE user_id = %s
            ) AS ranked_answers
            WHERE 1=1
                AND rank_number = 1
                AND is_correct;
                    """, (user_id,))
        answers_data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df_answers = pd.DataFrame(answers_data, columns=columns)
        cur.close()
        conn.close()
        return df_answers
    except psycopg2.Error as e:
        st.error(f"Erreur de base de données: {e}")
        return None
    
def fetch_answers(user_id, intervalle_revision):
    """Fetches correct answers for a specific user from the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM answers 
            WHERE user_id = %s AND is_correct = TRUE AND answer_date < %s;
        """, (user_id, datetime.now() - timedelta(days=intervalle_revision)))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(rows, columns=columns)
        cur.close()
        conn.close()
        return df
    except psycopg2.Error as e:
        st.error(f"Database error: {e}")
        return None