
from chatbot import ExpenseChatbot
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database import Database

# ==================================================
# PAGE SETTINGS
# ==================================================
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Expense Tracker")
st.write("Manage, update, and analyze your personal expenses.")

db = Database()


# ==================================================
# HELPER: CONVERT DATABASE RECORDS TO A DATAFRAME
# ==================================================
def create_expense_dataframe(records):
    """Support dictionary records returned by Database.get_all_expenses()."""

    if not records:
        return pd.DataFrame(
            columns=["ID", "Date", "Category", "Description", "Amount"]
        )

    df = pd.DataFrame(records)

    # The database returns lowercase dictionary keys.
    rename_columns = {
        "id": "ID",
        "date": "Date",
        "expense_date": "Date",
        "category": "Category",
        "description": "Description",
        "amount": "Amount"
    }

    df = df.rename(columns=rename_columns)

    # Also support tuple/list records if returned by another database method.
    if not {"ID", "Date", "Category", "Description", "Amount"}.issubset(
        df.columns
    ):
        df = pd.DataFrame(
            records,
            columns=["ID", "Date", "Category", "Description", "Amount"]
        )

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


# ==================================================
# LOAD EXPENSES
# ==================================================
try:
    expenses = db.get_all_expenses()
    df = create_expense_dataframe(expenses)

except Exception as e:
    st.error(f"Unable to load expenses: {e}")
    st.stop()


# ==================================================
# TWO-COLUMN LAYOUT
# ==================================================
left, right = st.columns(2, gap="large")


# ==================================================
# LEFT SIDE: EXPENSE MANAGEMENT
# ==================================================
with left:

    st.header("🧾 Expense Management")

    # --------------------------------------------------
    # ADD EXPENSE
    # --------------------------------------------------
    st.subheader("➕ Add Expense")

    with st.form("add_expense_form"):

        expense_date = st.date_input(
            "Expense Date",
            value=date.today(),
            key="add_date"
        )

        category = st.text_input(
            "Category",
            placeholder="Food, Travel, Bills"
        )

        description = st.text_input(
            "Description",
            placeholder="Lunch, Bus ticket"
        )

        amount = st.number_input(
            "Amount (₹)",
            min_value=0.01,
            value=100.0,
            step=1.0
        )

        submitted = st.form_submit_button("Add Expense")

        if submitted:
            if not category.strip():
                st.error("Please enter a category.")

            elif not description.strip():
                st.error("Please enter a description.")

            else:
                try:
                    db.add_expense(
                        expense_date,
                        category.strip(),
                        description.strip(),
                        amount
                    )

                    st.success("Expense added successfully!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Unable to add expense: {e}")

    # --------------------------------------------------
    # EDIT EXPENSE
    # --------------------------------------------------
    st.divider()
    st.subheader("✏️ Edit Expense")

    if not df.empty:

        options = {
            (
                f"ID {row.ID} — {row.Category} — "
                f"₹{row.Amount:,.2f}"
            ): row
            for row in df.itertuples(index=False)
        }

        edit_label = st.selectbox(
            "Choose expense to edit",
            list(options.keys()),
            key="edit_selector"
        )

        selected = options[edit_label]

        # Date is a pandas Timestamp; convert it to a Python date.
        selected_date = (
            selected.Date.date()
            if pd.notna(selected.Date)
            else date.today()
        )

        with st.form("edit_expense_form"):

            new_date = st.date_input(
                "New date",
                value=selected_date,
                key="edit_date"
            )

            new_category = st.text_input(
                "New category",
                value=str(selected.Category),
                key="edit_category"
            )

            new_description = st.text_input(
                "New description",
                value=str(selected.Description or ""),
                key="edit_description"
            )

            new_amount = st.number_input(
                "New amount (₹)",
                min_value=0.01,
                value=max(float(selected.Amount), 0.01),
                step=1.0,
                key="edit_amount"
            )

            save_changes = st.form_submit_button("Save Changes")

            if save_changes:

                if (
                    not new_category.strip()
                    or not new_description.strip()
                ):
                    st.error(
                        "Category and description cannot be empty."
                    )

                else:
                    try:
                        changed = db.update_expense(
                            int(selected.ID),
                            new_date,
                            new_category.strip(),
                            new_description.strip(),
                            new_amount
                        )

                        if changed:
                            st.success("Expense updated successfully!")
                        else:
                            st.info(
                                "No database row was changed. "
                                "The values may be unchanged."
                            )

                        st.rerun()

                    except Exception as e:
                        st.error(f"Unable to update expense: {e}")

        # --------------------------------------------------
        # DELETE EXPENSE
        # --------------------------------------------------
        st.divider()
        st.subheader("🗑️ Delete Expense")

        delete_label = st.selectbox(
            "Choose expense to delete",
            list(options.keys()),
            key="delete_selector"
        )

        confirm_delete = st.checkbox(
            "Confirm permanent deletion",
            key="confirm_delete"
        )

        if st.button("Delete Selected Expense"):

            if not confirm_delete:
                st.warning(
                    "Please confirm before deleting the expense."
                )

            else:
                try:
                    deleted = db.delete_expense(
                        int(options[delete_label].ID)
                    )

                    if deleted:
                        st.success("Expense deleted successfully!")
                    else:
                        st.warning("Expense was not found.")

                    st.rerun()

                except Exception as e:
                    st.error(f"Unable to delete expense: {e}")

    else:
        st.info(
            "No expenses are available yet. "
            "Add an expense to enable editing and deletion."
        )

    # --------------------------------------------------
    # ALL EXPENSES TABLE
    # --------------------------------------------------
    st.divider()
    st.subheader("📋 All Expenses")

    try:
        latest = db.get_all_expenses()
        latest_df = create_expense_dataframe(latest)

        if not latest_df.empty:
            display_df = latest_df.copy()

            # Display continuous serial numbers after deletions.
            display_df = display_df.reset_index(drop=True)
         

            # Format dates for display.
            display_df["Date"] = display_df["Date"].dt.date

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No expenses found yet.")

    except Exception as e:
        st.error(f"Unable to display expenses: {e}")

# ==================================================
# RIGHT SIDE: SPENDING DASHBOARD
# ==================================================
with right:

    st.header("📊 Spending Dashboard")

    try:
        chart_expenses = db.get_all_expenses()
        chart_df = create_expense_dataframe(chart_expenses)

    except Exception as e:
        st.error(f"Unable to load spending analysis: {e}")
        chart_df = pd.DataFrame()

    if not chart_df.empty:

        chart_df = chart_df.dropna(
            subset=["Date", "Amount", "Category"]
        )

        if not chart_df.empty:

            # --------------------------------------------------
            # SUMMARY METRICS
            # --------------------------------------------------
            total_spending = chart_df["Amount"].sum()
            expense_count = len(chart_df)

            metric1, metric2 = st.columns(2)

            metric1.metric(
                "Total Spent",
                f"₹{total_spending:,.2f}"
            )

            metric2.metric(
                "Transactions",
                expense_count
            )

            # --------------------------------------------------
            # CATEGORY PIE CHART
            # --------------------------------------------------
            st.subheader("Spending by Category")

            category_totals = (
                chart_df.groupby("Category")["Amount"]
                .sum()
                .sort_values(ascending=False)
            )

            category_chart_df = (
                category_totals
                .rename_axis("Category")
                .reset_index(name="Amount")
            )

            fig_pie = px.pie(
                category_chart_df,
                names="Category",
                values="Amount",
                title="Expenses by Category",
                hole=0.3
            )

            st.plotly_chart(
                fig_pie,
                use_container_width=True
            )

            # --------------------------------------------------
            # MONTHLY SPENDING BAR CHART
            # --------------------------------------------------
            st.subheader("Monthly Spending")

            chart_df["Month"] = (
                chart_df["Date"]
                .dt.to_period("M")
                .astype(str)
            )

            monthly_totals = (
                chart_df.groupby("Month", as_index=False)["Amount"]
                .sum()
                .sort_values("Month")
            )

            st.bar_chart(
                monthly_totals.set_index("Month")["Amount"],
                y_label="Amount (₹)"
            )

            # --------------------------------------------------
            # EXPENSE ANALYSIS
            # --------------------------------------------------
            st.subheader("💡 Expense Analysis")

            highest_category = category_totals.idxmax()
            highest_amount = category_totals.max()

            st.write(
                f"Your highest spending category is "
                f"**{highest_category}**, with "
                f"**₹{highest_amount:,.2f}** spent."
            )

            average_expense = total_spending / expense_count

            st.write(
                f"Your average expense is "
                f"**₹{average_expense:,.2f}**."
            )

            st.write("Monthly totals:")

            st.dataframe(
                monthly_totals.rename(
                    columns={"Amount": "Total (₹)"}
                ),
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info(
                "Expense records do not contain valid dates, "
                "categories, or amounts for analysis."
            )

    else:
        st.info(
            "Add expenses to see charts and spending analysis."
        )

    # ==================================================
    # AI EXPENSE ASSISTANT
    # ==================================================
    st.divider()
    st.subheader("🤖 AI Expense Assistant")

    st.write("Ask questions about your spending and expenses.")

    if "ai_chat_history" not in st.session_state:
        st.session_state.ai_chat_history = []

    question = st.text_input(
        "Your question",
        placeholder="Example: How much did I spend on food?",
        key="ai_expense_question"
    )

    if st.button("Ask AI", key="ask_expense_ai"):

        if not question.strip():
            st.warning("Please enter a question.")

        else:
            try:
                chatbot = ExpenseChatbot(db)

                current_expenses = db.get_all_expenses()

                expense_data = chatbot.format_expenses(
                    current_expenses
                )

                answer = chatbot.get_response(
                    expense_data,
                    question.strip()
                )

                st.session_state.ai_chat_history.append({
                    "question": question.strip(),
                    "answer": answer
                })

            except ValueError:
                st.error(
                    "The Gemini API key may be missing. "
                    "Please check your GEMINI_API_KEY configuration."
                )

            except Exception as e:
                st.error(
                    f"AI error: {type(e).__name__}: {e}"
                )

    for message in st.session_state.ai_chat_history:
        st.markdown("**You:** " + message["question"])
        st.markdown("**AI:** " + message["answer"])
        st.divider()
