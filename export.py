import csv


class ExpenseExporter:

    @staticmethod
    def export_to_csv(expenses, filename="expenses.csv"):

        headers = [
            "ID",
            "Date",
            "Category",
            "Description",
            "Amount"
        ]

        with open(
            filename,
            mode="w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow(headers)

            writer.writerows(expenses)

        print(f"\nExpenses exported successfully to {filename}")