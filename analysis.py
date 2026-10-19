import pandas as pd
import numpy as np


class ExpenseAnalyzer:

    def __init__(self, expenses):

        self.expenses = expenses

        self.columns = [
            "id",
            "date",
            "category",
            "description",
            "amount"
        ]

    def create_dataframe(self):

        df = pd.DataFrame(
            self.expenses,
            columns=self.columns
        )

        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df["amount"] = pd.to_numeric(df["amount"])

        return df

    def total_expense(self):

        df = self.create_dataframe()

        if df.empty:
            return 0

        return np.sum(df["amount"])

    def average_expense(self):

        df = self.create_dataframe()

        if df.empty:
            return 0

        return np.mean(df["amount"])

    def category_analysis(self):

        df = self.create_dataframe()

        if df.empty:
            return pd.DataFrame()

        result = (
            df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        return result

    def monthly_analysis(self):

        df = self.create_dataframe()

        if df.empty:
            return pd.DataFrame()

        df["month"] = df["date"].dt.to_period("M")

        result = (
            df.groupby("month")["amount"]
            .sum()
        )

        return result