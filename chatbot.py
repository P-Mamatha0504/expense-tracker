import streamlit as st
from openai import OpenAI
import os


class ExpenseChatbot:

    def __init__(self, database):
        self.database = database

        # Read Gemini API key from environment or Streamlit secrets.
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            try:
                api_key = st.secrets.get("GEMINI_API_KEY")
            except (NameError, FileNotFoundError, KeyError):
                api_key = None

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=(
                "https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        )

    def ask_ai(self, prompt):
        response = self.client.chat.completions.create(
            model="gemini-3.5-flash",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    def create_prompt(self, expense_data, user_question):
        return f"""
You are an AI Expense Analysis Assistant.

Help the user understand and analyze their personal expense records.

Rules:
1. Use only the expense data provided below.
2. Do not invent or assume expense information.
3. If information is unavailable, say so clearly.
4. Give clear, concise answers.
5. Use Indian Rupees (₹) for amounts.
6. Provide simple spending insights when useful.
7. Do not provide professional financial advice.
8. For unrelated questions, politely explain your role.

Expense Data:
{expense_data}

User Question:
{user_question}

Provide your answer in a simple and understandable way.
"""

    def get_response(self, expense_data, user_question):
        prompt = self.create_prompt(
            expense_data,
            user_question
        )
        return self.ask_ai(prompt)

    def format_expenses(self, expenses):
        if not expenses:
            return "No expense records are available."

        formatted_data = []

        for index, expense in enumerate(expenses, start=1):

            if isinstance(expense, dict):
                expense_id = expense.get("id", index)
                expense_date = expense.get(
                    "date",
                    expense.get("expense_date", "Unknown")
                )
                category = expense.get("category", "Unknown")
                description = expense.get("description", "")
                amount = expense.get("amount", 0)

            else:
                expense_id = expense[0]
                expense_date = expense[1]
                category = expense[2]
                description = expense[3]
                amount = expense[4]

            expense_text = (
                f"ID: {expense_id}, "
                f"Date: {expense_date}, "
                f"Category: {category}, "
                f"Description: {description}, "
                f"Amount: ₹{float(amount):.2f}"
            )

            formatted_data.append(expense_text)

        return "\n".join(formatted_data)

    def chat(self):
        print("\n========== AI EXPENSE CHATBOT ==========")
        print("Type 'exit' to return to the main menu.")

        while True:
            question = input("\nYou: ").strip()

            if question.lower() == "exit":
                print("Exiting chatbot...")
                break

            if not question:
                print("Please enter a question.")
                continue

            expenses = self.database.get_all_expenses()
            expense_data = self.format_expenses(expenses)

            response = self.get_response(
                expense_data,
                question
            )

            print("\nAI:", response)
