
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, date
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env", override=True)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)
from flask_bcrypt import Bcrypt


app = Flask(__name__)

# Application configuration
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Database configuration
database_url = os.getenv("DATABASE_URL", "sqlite:///expiryguard_web.db")

# Support Render PostgreSQL URLs
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

csrf = CSRFProtect(app)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



# User database model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Product database model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    expiry = db.Column(db.String(10), nullable=False)

    # Connect every product to its owner
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )



# Load logged-in user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Calculate product expiry status
def get_expiry_status(expiry):

    expiry_date = datetime.strptime(
        expiry, "%Y-%m-%d"
    ).date()

    today = date.today()

    days_left = (expiry_date - today).days

    if days_left < 0:
        return "Expired"

    elif days_left <= 7:
        return "Expiring Soon"

    else:
        return "Fresh"



# Home page
@app.route("/")
def home():
    return redirect(url_for("login"))


# Registration
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must contain at least 8 characters.")
            return redirect(url_for("register"))

        existing_user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if existing_user:
            flash("This email is already registered.")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = db.session.execute(
            db.select(User).filter_by(email=email)
        ).scalar_one_or_none()

        if user and bcrypt.check_password_hash(
            user.password, password
        ):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")

    return render_template("login.html")


# Personal dashboard


@app.route("/dashboard")
@login_required
def dashboard():

    search_query = request.args.get("search", "").strip()
    selected_category = request.args.get("category", "").strip()
    selected_status = request.args.get("status", "").strip()

    # Get all products belonging to the logged-in user
    all_products = db.session.execute(
        db.select(Product).filter_by(
            user_id=current_user.id
        )
    ).scalars().all()

    # Calculate status for every product
    for product in all_products:
        product.status = get_expiry_status(product.expiry)

    # Summary counts use all products
    total_products = len(all_products)

    expired_count = sum(
        1 for product in all_products
        if product.status == "Expired"
    )

    expiring_soon_count = sum(
        1 for product in all_products
        if product.status == "Expiring Soon"
    )

    fresh_count = sum(
        1 for product in all_products
        if product.status == "Fresh"
    )

    # Apply filters only to the displayed product list
    products = all_products

    if search_query:
        products = [
            product for product in products
            if search_query.lower() in product.name.lower()
        ]

    if selected_category:
        products = [
            product for product in products
            if product.category == selected_category
        ]

    if selected_status:
        products = [
            product for product in products
            if product.status == selected_status
        ]

    return render_template(
        "dashboard.html",
        name=current_user.name,
        products=products,
        total_products=total_products,
        expired_count=expired_count,
        expiring_soon_count=expiring_soon_count,
        fresh_count=fresh_count,
        search_query=search_query,
        selected_category=selected_category,
        selected_status=selected_status
    )

@app.route("/alerts")
@login_required
def alerts():

    all_products = db.session.execute(
        db.select(Product).filter_by(
            user_id=current_user.id
        )
    ).scalars().all()

    alert_products = []

    for product in all_products:

        status = get_expiry_status(product.expiry)

        if status in ["Expired", "Expiring Soon"]:
            expiry_date = datetime.strptime(
                product.expiry, "%Y-%m-%d"
            ).date()

            days_left = (expiry_date - date.today()).days

            alert_products.append({
                "product": product,
                "status": status,
                "days_left": days_left
            })

    return render_template(
        "alerts.html",
        alerts=alert_products
    )
# Add Product
@app.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", "").strip()
        expiry = request.form.get("expiry", "").strip()

        if not name or not category or not quantity or not expiry:
            flash("Please fill in all fields.")
            return redirect(url_for("add_product"))

        try:
            quantity = int(quantity)

            if quantity <= 0:
                raise ValueError

            expiry_date = datetime.strptime(
                expiry, "%Y-%m-%d"
            ).date()

        except ValueError:
            flash("Enter a valid positive quantity and expiry date.")
            return redirect(url_for("add_product"))

        new_product = Product(
            name=name,
            category=category,
            quantity=quantity,
            expiry=expiry,
            user_id=current_user.id
        )

        db.session.add(new_product)
        db.session.commit()

        flash("Product added successfully!")
        return redirect(url_for("dashboard"))

    return render_template("add_product.html")

# Delete Product
@app.route("/delete_product/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):

    product = db.session.execute(
        db.select(Product).filter_by(
            id=product_id,
            user_id=current_user.id
        )
    ).scalar_one_or_none()

    if product is None:
        flash("Product not found.")
        return redirect(url_for("dashboard"))

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully!")
    return redirect(url_for("dashboard"))

# Edit Product
@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):

    product = db.session.execute(
        db.select(Product).filter_by(
            id=product_id,
            user_id=current_user.id
        )
    ).scalar_one_or_none()

    if product is None:
        flash("Product not found.")
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", "").strip()
        expiry = request.form.get("expiry", "").strip()

        if not name or not category or not quantity or not expiry:
            flash("Please fill in all fields.")
            return redirect(url_for("edit_product", product_id=product.id))

        try:
            quantity = int(quantity)

            if quantity <= 0:
                raise ValueError

            datetime.strptime(expiry, "%Y-%m-%d")

        except ValueError:
            flash("Enter a valid quantity and expiry date.")
            return redirect(url_for("edit_product", product_id=product.id))

        product.name = name
        product.category = category
        product.quantity = quantity
        product.expiry = expiry

        db.session.commit()

        flash("Product updated successfully!")
        return redirect(url_for("dashboard"))

    return render_template("edit_product.html", product=product)



# Logout
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully.")
    return redirect(url_for("login"))


# Create database tables
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=False)
