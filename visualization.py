import matplotlib.pyplot as plt


class ExpenseVisualizer:

    @staticmethod
    def category_chart(category_data):

        if category_data.empty:
            print("No data available for visualization.")
            return

        category_data.plot(
            kind="bar",
            figsize=(10, 6)
        )

        plt.title("Category-wise Expense")
        plt.xlabel("Category")
        plt.ylabel("Amount")

        plt.tight_layout()

        plt.show()

    @staticmethod
    def monthly_chart(monthly_data):

        if monthly_data.empty:
            print("No data available for visualization.")
            return

        monthly_data.plot(
            kind="line",
            marker="o",
            figsize=(10, 6)
        )

        plt.title("Monthly Expense Trend")
        plt.xlabel("Month")
        plt.ylabel("Amount")

        plt.tight_layout()

        plt.show()