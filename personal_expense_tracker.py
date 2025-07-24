!pip install --upgrade plotly ipywidgets

import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import ipywidgets as widgets
from IPython.display import display, clear_output

def init_db():
    try:
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS expenses
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, amount FLOAT, category TEXT, date TEXT)''')
        c.execute("SELECT COUNT(*) FROM expenses")
        if c.fetchone()[0] == 0:
            sample_data = [
                (20.0, 'Food', '2025-06-01'),
                (15.0, 'Travel', '2025-06-05'),
                (30.0, 'Shopping', '2025-06-10'),
                (25.0, 'Food', '2025-07-15'),
                (10.0, 'Bills', '2025-07-20')
            ]
            c.executemany("INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)", sample_data)
        conn.commit()
        conn.close()
        print("Database initialized with sample data.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        
def add_expense(amount, category, date):
    try:
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
                  (amount, category, date))
        conn.commit()
        conn.close()
        print(f"Added expense: ${amount:.2f} in {category} on {date}")
    except Exception as e:
        print(f"Error adding expense: {e}")

# load analyze expenses
def analyze_expenses():
    try:
        conn = sqlite3.connect('expenses.db')
        df = pd.read_sql_query("SELECT * FROM expenses", conn)
        conn.close()
        if not df.empty:
            print("Current Expenses:")
            print(df[['amount', 'category', 'date']])
        return df
    except Exception as e:
        print(f"Error loading expenses: {e}")
        return pd.DataFrame()

def show_visualizations():
    df = analyze_expenses()
    if df.empty:
        print("No expenses to visualize! Please add expenses.")
        return

    try:
        # Pie chart: Spending by category
        fig_pie = px.pie(df, values='amount', names='category', title='Spending by Category',
                         color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_pie.update_layout(width=600, height=400)
        fig_pie.show()

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['month'] = df['date'].dt.to_period('M').astype(str)
        monthly_spending = df.groupby('month')['amount'].sum().reset_index()
        fig_bar = px.bar(monthly_spending, x='month', y='amount', title='Monthly Spending',
                         color='month', color_discrete_sequence=px.colors.qualitative.Plotly)
        fig_bar.update_layout(width=600, height=400)
        fig_bar.show()

        total = df['amount'].sum()
        avg_daily = df['amount'].mean()
        print(f"Total Spending: ${total:.2f}")
        print(f"Average Daily Expense: ${avg_daily:.2f}")
    except Exception as e:
        print(f"Error generating visualizations: {e}")

amount_input = widgets.FloatText(description="Amount ($):", style={'description_width': 'initial'})
category_input = widgets.Dropdown(
    options=['Food', 'Travel', 'Shopping', 'Bills', 'Other'],
    description="Category:",
    style={'description_width': 'initial'}
)
date_input = widgets.DatePicker(description="Date:", style={'description_width': 'initial'})
submit_button = widgets.Button(description="Add Expense", button_style='success')
viz_button = widgets.Button(description="Show Visualizations", button_style='info')

def on_submit_clicked(b):
    clear_output()
    display(amount_input, category_input, date_input, submit_button, viz_button)
    if amount_input.value and category_input.value and date_input.value:
        add_expense(amount_input.value, category_input.value, date_input.value.strftime('%Y-%m-%d'))
    else:
        print("Please fill all fields (Amount, Category, Date)!")

def on_viz_clicked(b):
    clear_output()
    display(amount_input, category_input, date_input, submit_button, viz_button)
    show_visualizations()

submit_button.on_click(on_submit_clicked)
viz_button.on_click(on_viz_clicked)

init_db()
display(amount_input, category_input, date_input, submit_button, viz_button)
