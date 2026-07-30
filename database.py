from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "rag_history.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            timestamp TEXT,

            user_name TEXT,

            question TEXT,

            action TEXT,

            answer TEXT,

            sources TEXT,

            retrieval_time REAL,

            llm_time REAL,

            total_time REAL
        )
        """
    )

    conn.commit()
    conn.close()


def save_history(
    user_name: str,
    question: str,
    action: str,
    answer: str,
    sources: str,
    retrieval_time: float,
    llm_time: float,
    total_time: float,
):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO history (

            timestamp,
            user_name,
            question,
            action,
            answer,
            sources,
            retrieval_time,
            llm_time,
            total_time

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_name,
            question,
            action,
            answer,
            sources,
            retrieval_time,
            llm_time,
            total_time,
        ),
    )

    conn.commit()
    conn.close()


def load_history():

    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT
            timestamp,
            user_name,
            question,
            action,
            total_time

        FROM history

        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows