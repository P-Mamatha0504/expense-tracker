
import os
import mysql.connector
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)


class Database:

    def connect(self):
        """Connect to the configured MySQL database."""

        config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "user": os.getenv("DB_USER", "root"),
            "password": os.getenv("DB_PASSWORD", ""),
            "database": os.getenv("DB_NAME", "defaultdb"),
            "port": int(os.getenv("DB_PORT", "3306")),
        }

        # Use Streamlit secrets when configured.
        try:
            if "DB_HOST" in st.secrets:
                config = {
                    "host": st.secrets["DB_HOST"],
                    "user": st.secrets["DB_USER"],
                    "password": st.secrets["DB_PASSWORD"],
                    "database": st.secrets.get(
                        "DB_NAME", "defaultdb"
                    ),
                    "port": int(st.secrets.get("DB_PORT", 3306)),
                }
        except (FileNotFoundError, KeyError):
            pass

        return mysql.connector.connect(**config)

    def add_expense(
        self, expense_date, category, description, amount
    ):
        """Add a new expense with the next sequential ID."""

        connection = self.connect()
        cursor = connection.cursor()

        try:
            cursor.execute(
                "SELECT COALESCE(MAX(id), 0) + 1 FROM expenses"
            )
            new_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO expenses
                (id, expense_date, category, description, amount)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    new_id,
                    expense_date,
                    category,
                    description,
                    amount,
                ),
            )

            connection.commit()
            return new_id

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_all_expenses(self):
        """Return expenses in ascending ID order."""

        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    id,
                    expense_date AS date,
                    category,
                    description,
                    amount
                FROM expenses
                ORDER BY id ASC
            """)
            return cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

    def get_expense(self, expense_id):
        """Get one expense by its ID."""

        connection = self.connect()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM expenses WHERE id = %s",
                (expense_id,),
            )
            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

    def update_expense(
        self,
        expense_id,
        expense_date,
        category,
        description,
        amount,
    ):
        """Update an existing expense."""

        connection = self.connect()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                UPDATE expenses
                SET expense_date = %s,
                    category = %s,
                    description = %s,
                    amount = %s
                WHERE id = %s
            """, (
                expense_date,
                category,
                description,
                amount,
                expense_id,
            ))

            connection.commit()
            return cursor.rowcount

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def delete_expense(self, expense_id):
        """Delete an expense and renumber remaining IDs from 1."""

        connection = self.connect()
        cursor = connection.cursor()

        try:
            # Delete the selected record.
            cursor.execute(
                "DELETE FROM expenses WHERE id = %s",
                (expense_id,),
            )

            deleted_count = cursor.rowcount

            if deleted_count == 0:
                connection.rollback()
                return 0

            # Get the remaining IDs in their current order.
            cursor.execute(
                "SELECT id FROM expenses ORDER BY id ASC"
            )
            existing_ids = [row[0] for row in cursor.fetchall()]

            if existing_ids:
                # Move all IDs to a temporary, non-overlapping range.
                offset = max(existing_ids) + len(existing_ids) + 1

                for old_id in existing_ids:
                    cursor.execute(
                        "UPDATE expenses SET id = %s WHERE id = %s",
                        (old_id + offset, old_id),
                    )

                # Assign consecutive IDs: 1, 2, 3, ...
                for new_id, old_id in enumerate(existing_ids, start=1):
                    cursor.execute(
                        "UPDATE expenses SET id = %s WHERE id = %s",
                        (new_id, old_id + offset),
                    )

            connection.commit()
            return deleted_count

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()
