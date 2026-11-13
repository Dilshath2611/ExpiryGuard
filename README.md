# ExpiryGuard – Smart Expiry & Waste Tracker

A Flask-based web application that helps users manage product expiry dates, monitor expiring items, and reduce unnecessary waste.

## Overview

ExpiryGuard is a multi-user product expiry management system developed using Python and Flask. It allows users to securely manage products, track expiry dates, and identify expired and soon-to-expire items through an interactive dashboard.

## Features

- User registration and secure login
- Personalized dashboard with product statistics
- Add, edit, and delete products
- Automatic expiry status tracking
- Alerts for expired and soon-to-expire products
- Search products by name
- Filter products by category and expiry status
- Separate product data for each user
- CSRF protection for forms

## Technologies Used

| Category | Technology |
|---|---|
| Programming Language | Python |
| Backend | Flask |
| Frontend | HTML, CSS, Bootstrap 5 |
| Database | SQLite |
| ORM | Flask-SQLAlchemy |
| Authentication | Flask-Login |
| Password Security | Flask-Bcrypt |
| Form Security | Flask-WTF |

## Project Structure

```text
ExpiryGuard/
├── main.py
├── .gitignore
└── web_app/
    ├── app.py
    ├── requirements.txt
    ├── .env.example
    ├── templates/
    │   ├── base.html
    │   ├── login.html
    │   ├── register.html
    │   ├── dashboard.html
    │   ├── add_product.html
    │   ├── edit_product.html
    │   └── alerts.html
    └── static/
        └── style.css
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Dilshath2611/ExpiryGuard.git
cd ExpiryGuard
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment (Windows)

```powershell
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r web_app/requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root directory and add:

```env
SECRET_KEY=your-secure-secret-key
```

Generate your own secret key. Never publish your actual `.env` file.

### 6. Run the application

```bash
python web_app/app.py
```

Open your browser and visit:

```text
https://expiryguard-j1ow.onrender.com
```

## Future Enhancements

- PostgreSQL cloud database integration
- Online deployment
- Email notifications for upcoming expiry dates
- Enhanced reporting and analytics

## Author

**Dilshath M**

MCA Student | Python & Web Development

GitHub: https://github.com/Dilshath2611

---

*ExpiryGuard – Track Smart. Reduce Waste. Stay Organized.*
