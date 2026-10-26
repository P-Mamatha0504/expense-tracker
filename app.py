from chatbot import ExpenseChatbot
import streamlit as st
import pandas as pd
from datetime import date
from database import Database

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Expense Tracker")
st.write("Manage, update, and analyze your personal expenses.")

db = Database()

# Split the page into two halves
left, right = st.columns(2, gap="large")

# Load the latest expenses
try:
    expenses = db.get_all_expenses()
except Exception as e:
    st.error(f"Unable to load expenses: {e}")
    st.stop()

# Convert records into a DataFrame
df = pd.DataFrame(
    expenses,
    columns=["ID", "Date", "Category", "Description", "Amount"]
)

if not df.empty:
    df["Amount"] = pd.to_numeric(df["Amount"])
    df["Date"] = pd.to_datetime(df["Date"])

# ==================================================
# LEFT HALF: ADD, EDIT, DELETE, AND EXPENSES TABLE
# ==================================================
with left:

    st.header("🧾 Expense Management")

    # ---------------- ADD EXPENSE ----------------
    st.subheader("➕ Add Expense")

    with st.form("add_expense_form"):
        expense_date = st.date_input("Expense Date", value=date.today())
        category = st.text_input("Category", placeholder="Food, Travel, Bills")
        description = st.text_input("Description", placeholder="Lunch, Bus ticket")
        amount = st.number_input(
            "Amount (₹)", min_value=0.01, value=100.0, step=1.0
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

    # ---------------- EDIT EXPENSE ----------------
    st.divider()
    st.subheader("✏️ Edit Expense")

    if not df.empty:
        options = {
            f"ID {row.ID} — {row.Category} — ₹{row.Amount:,.2f}": row
            for row in df.itertuples(index=False)
        }

        edit_label = st.selectbox(
            "Choose expense to edit",
            list(options.keys()),
            key="edit_selector"
        )

        selected = options[edit_label]

        with st.form("edit_expense_form"):
            new_date = st.date_input(
                "New date",
                value=selected.Date.date(),
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
                value=float(selected.Amount),
                step=1.0,
                key="edit_amount"
            )

            save_changes = st.form_submit_button("Save Changes")

            if save_changes:
                if not new_category.strip() or not new_description.strip():
                    st.error("Category and description cannot be empty.")
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
                            st.success("Expense updated!")
                        else:
                            st.info("No database row was changed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Unable to update expense: {e}")

        # ---------------- DELETE EXPENSE ----------------
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
                st.warning("Please confirm before deleting.")
            else:
                try:
                    deleted = db.delete_expense(int(options[delete_label].ID))
                    if deleted:
                        st.success("Expense deleted!")
                    else:
                        st.warning("Expense was not found.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Unable to delete expense: {e}")

    else:
        st.info("Add an expense to enable editing and deletion.")

    # ---------------- TABLE AT THE BOTTOM OF LEFT HALF ----------------
    st.divider()
    st.subheader("📋 All Expenses")

    # Fetch again so the table shows current database records
    latest = db.get_all_expenses()

    if latest:
        latest_df = pd.DataFrame(
            latest,
            columns=["ID", "Date", "Category", "Description", "Amount"]
        )
        st.dataframe(latest_df, use_container_width=True, hide_index=True)
    else:
        st.info("No expenses found yet.")

# ==================================================
# RIGHT HALF: CHARTS AND ANALYSIS
# ==================================================
with right:

    st.header("📊 Spending Dashboard")

    # Fetch current data for the charts
    chart_expenses = db.get_all_expenses()

    if chart_expenses:
        chart_df = pd.DataFrame(
            chart_expenses,
            columns=["ID", "Date", "Category", "Description", "Amount"]
        )

        chart_df["Amount"] = pd.to_numeric(chart_df["Amount"])
        chart_df["Date"] = pd.to_datetime(chart_df["Date"])

        total_spending = chart_df["Amount"].sum()
        expense_count = len(chart_df)

        metric1, metric2 = st.columns(2)
        metric1.metric("Total Spent", f"₹{total_spending:,.2f}")
        metric2.metric("Transactions", expense_count)

        # ---------------- CATEGORY PIE CHART ----------------
        st.subheader("Spending by Category")

        category_totals = (
            chart_df.groupby("Category")["Amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.write("Category-wise spending distribution")
        st.plotly_chart(
            # Streamlit's built-in chart uses Altair; this pie chart uses Plotly
            __import__("plotly.express", fromlist=["pie"]).pie(
                category_totals.reset_index(),
                names="Category",
                values="Amount",
                title="Expenses by Category"
            ),
            use_container_width=True
        )

        # ---------------- MONTHLY BAR CHART ----------------
        st.subheader("Monthly Spending")

        chart_df["Month"] = chart_df["Date"].dt.to_period("M").astype(str)

        monthly_totals = (
            chart_df.groupby("Month", as_index=False)["Amount"]
            .sum()
            .sort_values("Month")
        )

        st.bar_chart(
            monthly_totals.set_index("Month")["Amount"],
            y_label="Amount (₹)"
        )

        # ---------------- ANALYSIS ----------------
        st.subheader("💡 Expense Analysis")

        highest_category = category_totals.idxmax()
        highest_amount = category_totals.max()

        st.write(
            f"Your highest spending category is **{highest_category}**, "
            f"with ₹{highest_amount:,.2f} spent."
        )

        average_expense = total_spending / expense_count
        st.write(f"Your average expense is **₹{average_expense:,.2f}**.")

        chart_df["Month"] = chart_df["Date"].dt.to_period("M").astype(str)
        monthly_summary = chart_df.groupby("Month")["Amount"].sum()

        st.write("Monthly totals:")
        st.dataframe(
            monthly_summary.rename("Total (₹)").reset_index(),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Add expenses to see charts and spending analysis.")


    
    st.divider()
    st.subheader("AI Expense Assistant")
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

                st.session_state.ai_chat_history.append(
                    {
                        "question": question.strip(),
                        "answer": answer
                    }
                )

            except ValueError:
                st.error(
                    "Gemini API key is missing. "
                    "Please configure GEMINI_API_KEY."
                )

            except Exception as e:
                st.error(f"AI error: {type(e).__name__}: {e}")

    for message in st.session_state.ai_chat_history:
        st.markdown("**You:** " + message["question"])
        st.markdown("**AI:** " + message["answer"])
        st.divider()

