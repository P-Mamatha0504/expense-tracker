from openai import OpenAI
import os


class ExpenseChatbot:

    def __init__(self, database):

        self.database = database

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
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

        prompt = f"""
You are an AI Expense Analysis Assistant.

Your role is to help the user understand and analyze
their personal expense records.

Follow these rules:

1. Use only the expense data provided below.
2. Do not invent or assume expense information.
3. If the requested information is not available,
   clearly say that it is not available.
4. Give clear and concise answers.
5. Use Indian Rupees (₹) when discussing amounts.
6. When useful, provide simple spending insights.
7. Do not provide professional financial advice.
8. If the user asks something unrelated to expenses,
   politely explain that you are an expense analysis assistant.

Expense Data:
{expense_data}

User Question:
{user_question}

Provide the answer in a simple and understandable way.
"""

        return prompt


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

        for expense in expenses:

            expense_text = (
                f"ID: {expense[0]}, "
                f"Date: {expense[1]}, "
                f"Category: {expense[2]}, "
                f"Description: {expense[3]}, "
                f"Amount: ₹{expense[4]:.2f}"
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

            expense_data = self.format_expenses(
                expenses
            )

            response = self.get_response(
                expense_data,
                question
            )

            print("\nAI:", response)