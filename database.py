import mysql.connector


class Database:

    def connect(self):
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Mamatha@1@2@",
            database="expense_tracker"
        )

    def add_expense(self, expense_date, category, description, amount):

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO expenses
            (expense_date, category, description, amount)
            VALUES (%s, %s, %s, %s)
        """, (expense_date, category, description, amount))

        connection.commit()
        connection.close()

    def get_all_expenses(self):

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, expense_date, category, description, amount
            FROM expenses
            ORDER BY expense_date DESC
        """)

        expenses = cursor.fetchall()

        connection.close()

        return expenses

    def get_expense(self, expense_id):

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, expense_date, category, description, amount
            FROM expenses
            WHERE id = %s
        """, (expense_id,))

        expense = cursor.fetchone()

        connection.close()

        return expense

    def update_expense(
        self,
        expense_id,
        expense_date,
        category,
        description,
        amount
    ):

        connection = self.connect()
        cursor = connection.cursor()

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
            expense_id
        ))

        connection.commit()

        updated_rows = cursor.rowcount

        connection.close()

        return updated_rows

    def delete_expense(self, expense_id):

        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM expenses
            WHERE id = %s
        """, (expense_id,))

        connection.commit()

        deleted_rows = cursor.rowcount

        connection.close()

        return deleted_rows

    def search_expenses(self, keyword):

        connection = self.connect()
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

        expenses = cursor.fetchall()

        connection.close()

        return expenses