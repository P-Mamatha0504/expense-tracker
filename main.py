from chatbot import ExpenseChatbot
from database import Database
from analysis import ExpenseAnalyzer
from visualization import ExpenseVisualizer
from export import ExpenseExporter
from datetime import datetime


class ExpenseTracker:

    def __init__(self):

        self.database = Database()
        self.chatbot = ExpenseChatbot(self.database)

    def add_expense(self):

        print("\n========== ADD EXPENSE ==========")

        date = input(
            "Enter date (YYYY-MM-DD): "
        ).strip()

        try:

            datetime.strptime(
                date,
                "%Y-%m-%d"
            )

        except ValueError:

            print("Invalid date format.")
            print("Please use YYYY-MM-DD.")

            return

        category = input(
            "Enter category: "
        ).strip()

        description = input(
            "Enter description: "
        ).strip()

        try:

            amount = float(
                input("Enter amount: ")
            )

            if amount <= 0:

                print("Amount must be greater than zero.")

                return

        except ValueError:

            print("Please enter a valid amount.")

            return

        if not category or not description:

            print("Category and description cannot be empty.")

            return

        self.database.add_expense(
            date,
            category,
            description,
            amount
        )

        print("\nExpense added successfully!")

    # view expenses
    def view_expenses(self):

        print("\n========== ALL EXPENSES ==========")

        expenses = self.database.get_all_expenses()

        if not expenses:

            print("No expenses found.")

            return

        print(
            f"{'ID':<5}"
            f"{'Date':<15}"
            f"{'Category':<15}"
            f"{'Description':<25}"
            f"{'Amount':>10}"
        )

        print("-" * 70)

        for expense in expenses:

            print(
                f"{expense[0]:<5}"
                f"{expense[1]:<15}"
                f"{expense[2]:<15}"
                f"{expense[3]:<25}"
                f"₹{expense[4]:>9.2f}"
            )

    # update expenses
    def update_expense(self):

        print("\n========== UPDATE EXPENSE ==========")

        try:

            expense_id = int(
                input("Enter expense ID: ")
            )

        except ValueError:

            print("Invalid ID.")

            return

        expense = self.database.get_expense(
            expense_id
        )

        if not expense:

            print("Expense not found.")

            return

        print("\nCurrent Expense:")

        print(
            f"Date: {expense[1]}"
        )

        print(
            f"Category: {expense[2]}"
        )

        print(
            f"Description: {expense[3]}"
        )

        print(
            f"Amount: ₹{expense[4]:.2f}"
        )

        date = input(
            "Enter new date (YYYY-MM-DD): "
        ).strip()

        try:

            datetime.strptime(
                date,
                "%Y-%m-%d"
            )

        except ValueError:

            print("Invalid date.")

            return

        category = input(
            "Enter new category: "
        ).strip()

        description = input(
            "Enter new description: "
        ).strip()

        try:

            amount = float(
                input("Enter new amount: ")
            )

            if amount <= 0:

                print("Amount must be greater than zero.")

                return

        except ValueError:

            print("Invalid amount.")

            return

        updated = self.database.update_expense(
            expense_id,
            date,
            category,
            description,
            amount
        )

        if updated:

            print("\nExpense updated successfully!")

        else:

            print("\nUnable to update expense.")


    # delete an expenses
    def delete_expense(self):

        print("\n========== DELETE EXPENSE ==========")

        try:

            expense_id = int(
                input("Enter expense ID: ")
            )

        except ValueError:

            print("Invalid ID.")

            return

        expense = self.database.get_expense(
            expense_id
        )

        if not expense:

            print("Expense not found.")

            return

        print(
            f"\nExpense: {expense[3]}"
        )

        confirmation = input(
            "Are you sure you want to delete it? (y/n): "
        ).lower()

        if confirmation == "y":

            deleted = self.database.delete_expense(
                expense_id
            )

            if deleted:

                print(
                    "\nExpense deleted successfully!"
                )

        else:

            print("\nDelete operation cancelled.")

    # search an expenses
    def search_expenses(self):

        print("\n========== SEARCH EXPENSES ==========")

        keyword = input(
            "Enter search keyword: "
        ).strip()

        expenses = self.database.search_expenses(
            keyword
        )

        if not expenses:

            print("No matching expenses found.")

            return

        print()

        for expense in expenses:

            print(
                f"ID: {expense[0]} | "
                f"Date: {expense[1]} | "
                f"Category: {expense[2]} | "
                f"Description: {expense[3]} | "
                f"Amount: ₹{expense[4]:.2f}"
            )
    # Financial analysis
    def show_analysis(self):

        print("\n========== FINANCIAL ANALYSIS ==========")

        expenses = self.database.get_all_expenses()

        if not expenses:

            print("No expenses available for analysis.")

            return

        analyzer = ExpenseAnalyzer(
            expenses
        )

        total = analyzer.total_expense()

        average = analyzer.average_expense()

        print(
            f"\nTotal Expense: ₹{total:.2f}"
        )

        print(
            f"Average Expense: ₹{average:.2f}"
        )

        print("\nCategory-wise Expense:")

        category_data = analyzer.category_analysis()

        print(category_data)

        print("\nMonthly Expense:")

        monthly_data = analyzer.monthly_analysis()

        print(monthly_data)


    # Show charts
    def show_charts(self):

        print("\n========== EXPENSE CHARTS ==========")

        expenses = self.database.get_all_expenses()

        if not expenses:

            print("No data available.")

            return

        analyzer = ExpenseAnalyzer(
            expenses
        )

        category_data = analyzer.category_analysis()

        monthly_data = analyzer.monthly_analysis()

        print("\n1. Category-wise Chart")
        print("2. Monthly Expense Chart")

        choice = input(
            "Choose chart: "
        )

        if choice == "1":

            ExpenseVisualizer.category_chart(
                category_data
            )

        elif choice == "2":

            ExpenseVisualizer.monthly_chart(
                monthly_data
            )

        else:

            print("Invalid choice.")

    # export expenses
    def export_expenses(self):

        print("\n========== EXPORT EXPENSES ==========")

        expenses = self.database.get_all_expenses()

        if not expenses:

            print("No expenses available.")

            return

        ExpenseExporter.export_to_csv(
            expenses
        )


    def run(self):

        while True:

            print("\n")
            print("=" * 45)
            print("       EXPENSE TRACKER SYSTEM")
            print("=" * 45)



            print("1. Add Expense")
            print("2. View Expenses") 
            print("3. Search Expenses")
            print("4. Update Expense")
            print("5. Delete Expense")
            print("6. Financial Analysis")
            print("7. View Charts")
            print("8. Export Expenses")
            print("9. AI Expense Chatbot")
            print("10. Exit")

            
            print("=" * 45)

            choice = input(
                "Enter your choice: "
            ).strip()

            if choice == "1":

                self.add_expense()

            elif choice == "2":

                self.view_expenses()

            elif choice == "3":

                self.search_expenses()

            elif choice == "4":

                self.update_expense()

            elif choice == "5":

                self.delete_expense()

            elif choice == "6":

                self.show_analysis()

            elif choice == "7":

                self.show_charts()

            elif choice == "8":

                self.export_expenses()

            elif choice == "9":

                self.chatbot.chat()

            elif choice == "10":

                print(
                    "\nThank you for using Expense Tracker!"
                )

                break

            else:

                print(
                    "\nInvalid choice. Please try again."
                )


if __name__ == "__main__":

    application = ExpenseTracker()

    application.run()