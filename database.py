
import os
import mysql.connector

from dotenv import load_dotenv

load_dotenv()

class Database:

    def connect(self):
        try:
            import streamlit as st

            if "DB_HOST" in st.secrets:
                config = {
                    "host": st.secrets["DB_HOST"],
                    "user": st.secrets["DB_USER"],
                    "password": st.secrets["DB_PASSWORD"],
                    "database": st.secrets.get(
                        "DB_NAME", "expense_tracker"
                    ),
                    "port": int(
                        st.secrets.get("DB_PORT", 3306)
                    ),
                }
            else:
                raise KeyError("Use local environment settings")

        except (ImportError, KeyError, FileNotFoundError):
            config = {
                "host": os.getenv("DB_HOST", "localhost"),
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD", ""),
                "database": os.getenv(
                    "DB_NAME", "expense_tracker"
                ),
                "port": int(os.getenv("DB_PORT", "3306")),
            }

        return mysql.connector.connect(**config)

    def add_expense(self, expense_date, category, description, amount):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO expenses
                (expense_date, category, description, amount)
                VALUES (%s, %s, %s, %s)
            """, (expense_date, category, description, amount))
            connection.commit()
        finally:
            connection.close()

    def get_all_expenses(self):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id, expense_date, category, description, amount
                FROM expenses
                ORDER BY expense_date DESC
            """)
            return cursor.fetchall()
        finally:
            connection.close()

    def get_expense(self, expense_id):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT id, expense_date, category, description, amount
                FROM expenses
                WHERE id = %s
            """, (expense_id,))
            return cursor.fetchone()
        finally:
            connection.close()

    def update_expense(
        self, expense_id, expense_date, category, description, amount
    ):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE expenses
                SET expense_date = %s,
                    category = %s,
                    description = %s,
                    amount = %s
                WHERE id = %s
            """, (
                expense_date, category, description, amount, expense_id
            ))
            connection.commit()
            return cursor.rowcount
        finally:
            connection.close()

    def delete_expense(self, expense_id):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                DELETE FROM expenses
                WHERE id = %s
            """, (expense_id,))
            connection.commit()
            return cursor.rowcount
        finally:
            connection.close()

    def search_expenses(self, keyword):
        connection = self.connect()
        try:
            cursor = connection.cursor()
            keyword = f"%{keyword}%"
            cursor.execute("""
                SELECT id, expense_date, category, description, amount
                FROM expenses
                WHERE category LIKE %s
                   OR description LIKE %s
                   OR expense_date LIKE %s
                ORDER BY expense_date DESC
            """, (keyword, keyword, keyword))
            return cursor.fetchall()
        finally:
            connection.close()
