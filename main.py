import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# Constants
CSV_FILE = "finance_data.csv"
COLUMNS = ["date", "amount", "category", "description"]
FORMAT = "%d-%m-%Y"
CATEGORIES = {"Income": "Income", "Expense": "Expense"}

# Dark Theme Styling
def set_dark_theme():
    st.markdown(
        """
        <style>
        .stApp { background-color: #121212; color: white; }
        .stSidebar { background-color: #1e1e1e !important; color: white; }
        .stButton>button { background-color: #4CAF50; color: white; border-radius: 10px; padding: 10px; }
        .stDataFrame { background-color: #1e1e1e; color: white; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Initialize CSV if not exists
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)

# Add a new transaction
def add_entry(date, amount, category, description):
    new_entry = pd.DataFrame([[date, amount, category, description]], columns=COLUMNS)
    df = pd.read_csv(CSV_FILE) if os.path.exists(CSV_FILE) else pd.DataFrame(columns=COLUMNS)
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)
    st.success("✅ Transaction added successfully!")

# Fetch transactions within a date range
def get_transactions(start_date, end_date):
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(columns=COLUMNS)
    
    df = pd.read_csv(CSV_FILE)
    df["date"] = pd.to_datetime(df["date"], format=FORMAT, errors='coerce')
    start_date = datetime.strptime(start_date, FORMAT)
    end_date = datetime.strptime(end_date, FORMAT)
    
    mask = (df["date"] >= start_date) & (df["date"] <= end_date)
    return df.loc[mask]

# Plot income vs. expense over time
def plot_transactions(df):
    if df.empty:
        st.warning("⚠️ No data available to plot.")
        return
    
    df["date"] = pd.to_datetime(df["date"], format=FORMAT, errors='coerce')
    income_df = df[df["category"] == "Income"].groupby("date")["amount"].sum()
    expense_df = df[df["category"] == "Expense"].groupby("date")["amount"].sum()
    
    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df.values, label="Income", color="g", marker="o")
    plt.plot(expense_df.index, expense_df.values, label="Expense", color="r", marker="s")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income & Expense Over Time")
    plt.legend()
    plt.grid()
    st.pyplot(plt)

# Main App
def main():
    set_dark_theme()
    st.title("💰 Personal Finance Tracker")
    initialize_csv()
    
    menu = ["Add Transaction", "View Transactions"]
    choice = st.sidebar.selectbox("📌 Menu", menu)
    
    if choice == "Add Transaction":
        st.subheader("📌 Add New Transaction")
        date = st.date_input("📅 Select Date", datetime.today()).strftime(FORMAT)
        amount = st.number_input("💰 Enter Amount", min_value=1.0, step=0.01)
        category = st.selectbox("📂 Select Category", list(CATEGORIES.values()))
        description = st.text_input("📝 Enter Description (Optional)")
        
        if st.button("➕ Add Transaction"):
            add_entry(date, amount, category, description)
    
    elif choice == "View Transactions":
        st.subheader("📊 View Transactions & Summary")
        start_date = st.date_input("📆 Start Date").strftime(FORMAT)
        end_date = st.date_input("📆 End Date").strftime(FORMAT)
        
        if st.button("🔍 Show Transactions"):
            df = get_transactions(start_date, end_date)
            if not df.empty:
                st.dataframe(df.style.set_properties(**{'background-color': '#1e1e1e', 'color': 'white'}))
                
                total_income = df[df["category"] == "Income"]["amount"].sum()
                total_expense = df[df["category"] == "Expense"]["amount"].sum()
                
                st.markdown(f"**💵 Total Income:** ₹{total_income:.2f}")
                st.markdown(f"**💸 Total Expense:** ₹{total_expense:.2f}")
                st.markdown(f"**💰 Net Savings:** ₹{(total_income - total_expense):.2f}")
                
                # Automatically show the plot
                plot_transactions(df)
            else:
                st.warning("⚠️ No transactions found in the given date range.")

if __name__ == "__main__":
    main()
