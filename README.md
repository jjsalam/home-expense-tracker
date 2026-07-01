# 📊 Home Expense Tracker

A beautiful, feature-rich expense tracking application built with Streamlit and SQLite.

## ✨ Features

1. **🔐 User Authentication** - Secure login with multiple user accounts
2. **✏️ Edit/Delete Expenses** - Modify or remove transactions anytime
3. **📈 Advanced Analytics** - View spending trends, monthly summaries, and charts
4. **📥 Export Data** - Download expenses as CSV or Excel files
5. **💰 Budget Limits** - Set monthly budgets per category with alerts
6. **👥 Multi-User Support** - Different accounts for family members
7. **📅 Date Filtering** - Filter expenses by date range
8. **🔍 Search** - Search expenses by description or category
9. **👤 User-Specific Data** - View only your expenses or all users'
10. **📱 Mobile-Friendly** - Responsive design works on all devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/home-expense-tracker.git
cd home-expense-tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

4. Open your browser and go to: `http://localhost:8501`

## 👤 Default Users

| Username | Password |
|----------|----------|
| abdul | admin123 |
| kamar | user123 |
| salam | pass123 |
| fatima | pass456 |

## 📋 Usage

### Adding an Expense
1. Login with your username and password
2. Fill in the expense details in the sidebar
3. Click "Add Expense"

### Setting a Budget
1. Go to "Set Budget Limits" in the sidebar
2. Select a category
3. Enter your budget limit
4. Click "Set Budget"

### Filtering & Searching
1. Use the date range filters at the top
2. Use the search box to find specific expenses
3. Toggle "Show all users' expenses" to see family expenses

### Exporting Data
1. Choose CSV or Excel format
2. Click the download button
3. Open the file in your preferred application

## 🎨 Technologies Used

- **Streamlit** - Web framework
- **Pandas** - Data manipulation
- **SQLite** - Database
- **Python** - Backend

## 📝 License

MIT License - feel free to use this project!

## 💡 Tips

- Database is stored locally in `home_expenses.db`
- Data persists between sessions
- All users share the same database
- Monthly budgets reset each month

Enjoy tracking your expenses! 🎉
