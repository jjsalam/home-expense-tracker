import streamlit as st
import pandas as pd
import sqlite3
import datetime
from io import BytesIO
import base64

# --- DATABASE SETUP ---
# check_same_thread=False is needed for Streamlit to handle concurrent users
conn = sqlite3.connect('home_expenses.db', check_same_thread=False)
c = conn.cursor()

# Create expenses table
c.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT,
        added_by TEXT
    )
''')

# Create budgets table
c.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT UNIQUE,
        budget_limit REAL
    )
''')
conn.commit()

# --- DATABASE FUNCTIONS ---
def add_expense(date, category, amount, description, added_by):
    c.execute('INSERT INTO expenses (date, category, amount, description, added_by) VALUES (?, ?, ?, ?, ?)',
              (date, category, amount, description, added_by))
    conn.commit()

def load_data():
    return pd.read_sql('SELECT * FROM expenses', conn)

def delete_expense(expense_id):
    c.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()

def update_expense(expense_id, date, category, amount, description):
    c.execute('UPDATE expenses SET date=?, category=?, amount=?, description=? WHERE id=?',
              (date, category, amount, description, expense_id))
    conn.commit()

def set_budget(category, budget_limit):
    c.execute('INSERT OR REPLACE INTO budgets (category, budget_limit) VALUES (?, ?)', (category, budget_limit))
    conn.commit()

def get_budgets():
    return pd.read_sql('SELECT * FROM budgets', conn)

def export_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def export_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Expenses', index=False)
    output.seek(0)
    return output.getvalue()

# --- LOGIN SYSTEM ---
# Basic dictionary for credentials (you can change passwords here)
USER_CREDENTIALS = {
    "abdul": "admin123",
    "kamar": "user123",
    "salam": "pass123",
    "fatima": "pass456"
}

st.set_page_config(page_title="Home Expense Tracker", page_icon="📊", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔒 Login")
    with st.form("login_form"):
        username = st.text_input("Username").lower()
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login")
        
        if submit_login:
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid Username or Password")
else:
    # --- MAIN APP ---
    st.title(f"📊 Home Expense Tracker")
    
    col1, col2 = st.columns([8, 1])
    with col1:
        st.write(f"Welcome back, **{st.session_state.username.capitalize()}**!")
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    df = load_data()
    
    # FEATURE 10: Mobile-friendly responsive design
    st.markdown("---")
    
    # FEATURE 6: Date filtering
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=30))
    with col_filter2:
        end_date = st.date_input("End Date", datetime.date.today())
    
    # FEATURE 7: Search functionality
    search_term = st.text_input("🔍 Search by description or category")

    # --- SIDEBAR: DATA ENTRY ---
    st.sidebar.header("📝 Add New Expense")
    with st.sidebar.form("expense_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.date.today())
        category = st.selectbox("Category", ["Groceries", "Education", "Utilities", "Fuel", "Medical", "Shopping", "Entertainment", "Transport", "Other"])
        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
        desc = st.text_input("Description (Optional)")
        submit = st.form_submit_button("Add Expense")

        if submit and amount > 0:
            add_expense(str(date), category, amount, desc, st.session_state.username)
            st.sidebar.success("✅ Expense added successfully!")
            st.rerun()
    
    # FEATURE 4: Budget limits management
    st.sidebar.header("💰 Set Budget Limits")
    with st.sidebar.form("budget_form"):
        budget_category = st.selectbox("Category", ["Groceries", "Education", "Utilities", "Fuel", "Medical", "Shopping", "Entertainment", "Transport", "Other"], key="budget_select")
        budget_limit = st.number_input("Budget Limit (₹)", min_value=0.0, format="%.2f")
        submit_budget = st.form_submit_button("Set Budget")
        
        if submit_budget and budget_limit > 0:
            set_budget(budget_category, budget_limit)
            st.sidebar.success("✅ Budget set successfully!")
            st.rerun()

    # Apply filters
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter by date range
        filtered_df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)].copy()
        
        # FEATURE 8: User-specific data
        show_all_users = st.checkbox("Show all users' expenses", value=False)
        if not show_all_users:
            filtered_df = filtered_df[filtered_df['added_by'] == st.session_state.username]
        
        # FEATURE 7: Search filter
        if search_term:
            filtered_df = filtered_df[
                (filtered_df['description'].str.contains(search_term, case=False, na=False)) |
                (filtered_df['category'].str.contains(search_term, case=False, na=False))
            ]
        
        # --- DASHBOARD ---
        st.markdown("### 📈 Dashboard")
        
        total_spent = filtered_df['amount'].sum()
        col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
        
        with col_metric1:
            st.metric(label="Total Expenses", value=f"₹ {total_spent:,.2f}")
        
        with col_metric2:
            st.metric(label="Number of Transactions", value=len(filtered_df))
        
        with col_metric3:
            avg_expense = filtered_df['amount'].mean() if len(filtered_df) > 0 else 0
            st.metric(label="Average Expense", value=f"₹ {avg_expense:,.2f}")
        
        with col_metric4:
            max_expense = filtered_df['amount'].max() if len(filtered_df) > 0 else 0
            st.metric(label="Highest Expense", value=f"₹ {max_expense:,.2f}")
        
        st.markdown("---")
        
        # FEATURE 2: Advanced analytics
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("💹 Spending by Category")
            category_grouped = filtered_df.groupby("category")["amount"].sum().reset_index()
            st.bar_chart(category_grouped.set_index("category"))
        
        with col_chart2:
            st.subheader("🥧 Category Distribution")
            if not category_grouped.empty:
                st.write(category_grouped)
        
        st.markdown("---")
        
        # Monthly summary
        st.subheader("📅 Monthly Summary")
        filtered_df['month'] = filtered_df['date'].dt.to_period('M')
        monthly_summary = filtered_df.groupby('month')['amount'].sum().reset_index()
        st.line_chart(monthly_summary.set_index('month'))
        
        st.markdown("---")
        
        # NEW: User comparison
        st.subheader("👥 User Comparison")
        user_category = filtered_df.groupby(['added_by', 'category'])['amount'].sum().reset_index()
        user_pivot = user_category.pivot(index='category', columns='added_by', values='amount').fillna(0)
        
        if not user_pivot.empty:
            st.bar_chart(user_pivot)
            st.write("**Detailed breakdown:**")
            st.dataframe(user_pivot)
        
        st.markdown("---")
        
        # FEATURE 4: Budget alerts
        st.subheader("💡 Budget Status")
        budgets_df = get_budgets()
        
        if not budgets_df.empty:
            for _, budget_row in budgets_df.iterrows():
                cat = budget_row['category']
                limit = budget_row['budget_limit']
                spent = filtered_df[filtered_df['category'] == cat]['amount'].sum()
                percentage = (spent / limit * 100) if limit > 0 else 0
                
                if percentage > 100:
                    st.error(f"🔴 **{cat}**: ₹{spent:.2f} / ₹{limit:.2f} ({percentage:.0f}%) - OVER BUDGET!")
                elif percentage > 80:
                    st.warning(f"🟡 **{cat}**: ₹{spent:.2f} / ₹{limit:.2f} ({percentage:.0f}%) - Warning")
                else:
                    st.success(f"🟢 **{cat}**: ₹{spent:.2f} / ₹{limit:.2f} ({percentage:.0f}%)")
        else:
            st.info("No budgets set yet. Set budget limits in the sidebar!")
        
        st.markdown("---")
        
        # FEATURE 1: Edit/Delete expenses
        st.subheader("📋 Transactions")
        
        # Show user summary at top
        if not filtered_df.empty:
            st.write("**Expenses by User:**")
            user_summary = filtered_df.groupby('added_by')['amount'].agg(['sum', 'count']).round(2)
            user_summary.columns = ['Total (₹)', 'Count']
            st.dataframe(user_summary)
            st.markdown("---")
        
        col_tab1, col_tab2, col_tab3 = st.columns([2, 1, 1])
        
        with col_tab1:
            st.write("**All Transactions**")
            display_df = filtered_df.sort_values(by="date", ascending=False).copy()
            
            for idx, row in display_df.iterrows():
                col_exp1, col_exp2, col_exp3 = st.columns([3, 1, 1])
                with col_exp1:
                    st.write(f"👤 **{row['added_by'].upper()}** | 📍 **{row['category']}** - ₹{row['amount']:.2f} | {row['date'].strftime('%Y-%m-%d')}")
                    st.write(f"   Description: {row['description'] if row['description'] else 'N/A'}")
                
                with col_exp2:
                    if st.button("✏️ Edit", key=f"edit_{row['id']}"):
                        st.session_state[f"edit_mode_{row['id']}"] = True
                
                with col_exp3:
                    if st.button("🗑️ Delete", key=f"delete_{row['id']}"):
                        delete_expense(row['id'])
                        st.success("Expense deleted!")
                        st.rerun()
                
                # FEATURE 1: Edit form
                if st.session_state.get(f"edit_mode_{row['id']}", False):
                    with st.form(f"edit_form_{row['id']}"):
                        edit_date = st.date_input("Date", row['date'].date(), key=f"edit_date_{row['id']}")
                        edit_category = st.selectbox("Category", ["Groceries", "Education", "Utilities", "Fuel", "Medical", "Shopping", "Entertainment", "Transport", "Other"], 
                                                     index=["Groceries", "Education", "Utilities", "Fuel", "Medical", "Shopping", "Entertainment", "Transport", "Other"].index(row['category']),
                                                     key=f"edit_category_{row['id']}")
                        edit_amount = st.number_input("Amount (₹)", value=float(row['amount']), format="%.2f", key=f"edit_amount_{row['id']}")
                        edit_desc = st.text_input("Description", value=row['description'], key=f"edit_desc_{row['id']}")
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("Save Changes"):
                                update_expense(row['id'], str(edit_date), edit_category, edit_amount, edit_desc)
                                st.success("Expense updated!")
                                st.session_state[f"edit_mode_{row['id']}"] = False
                                st.rerun()
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"edit_mode_{row['id']}"] = False
                                st.rerun()
                
                st.divider()
        
        st.markdown("---")
        
        # FEATURE 3: Export data
        st.subheader("📥 Export Data")
        export_format = st.radio("Choose format:", ["CSV", "Excel"], horizontal=True)
        
        if export_format == "CSV":
            csv_data = export_to_csv(filtered_df)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"expenses_{datetime.date.today()}.csv",
                mime="text/csv"
            )
        else:
            excel_data = export_to_excel(filtered_df)
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name=f"expenses_{datetime.date.today()}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No expenses recorded yet. Add your first expense using the sidebar menu!")