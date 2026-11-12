
import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime

# Store products temporarily
products = []
def initialize_database():

    connection = sqlite3.connect("expiryguard.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            expiry TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


initialize_database()

# Main window
root = tk.Tk()
root.title("ExpiryGuard - Smart Expiry Tracker")
root.geometry("1000x600")
root.configure(bg="#F4F6F9")

# Main content area
main_area = tk.Frame(root, bg="#F4F6F9")
main_area.pack(side="right", fill="both", expand=True)

# Sidebar
sidebar = tk.Frame(root, bg="#1E293B", width=220)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

app_name = tk.Label(
    sidebar,
    text="ExpiryGuard",
    font=("Arial", 20, "bold"),
    bg="#1E293B",
    fg="white"
)
app_name.pack(pady=30)

# Page navigation
def clear_page():
    for widget in main_area.winfo_children():
        widget.destroy()


# Dashboard page
def show_dashboard():
    clear_page()

    today = datetime.today().date()

    connection = sqlite3.connect("expiryguard.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT quantity, expiry FROM products
    """)

    records = cursor.fetchall()
    connection.close()

    total_products = len(records)
    expiring_soon = 0
    expired_products = 0
    total_stock = 0

    for quantity, expiry in records:

        total_stock += quantity

        expiry_date = datetime.strptime(
            expiry, "%Y-%m-%d"
        ).date()

        days_left = (expiry_date - today).days

        if days_left < 0:
            expired_products += 1

        elif days_left <= 7:
            expiring_soon += 1

    heading = tk.Label(
        main_area,
        text="Dashboard",
        font=("Arial", 22, "bold"),
        bg="#F4F6F9",
        fg="#1E293B"
    )
    heading.pack(anchor="w", pady=20)

    stats = [
        ("Total Products", total_products),
        ("Expiring Soon", expiring_soon),
        ("Expired Products", expired_products),
        ("Available Stock", total_stock)
    ]

    for title, value in stats:

        card = tk.Frame(
            main_area,
            bg="white",
            padx=25,
            pady=20
        )
        card.pack(fill="x", pady=8)

        tk.Label(
            card,
            text=title,
            font=("Arial", 12),
            bg="white",
            fg="#64748B"
        ).pack(anchor="w")

        tk.Label(
            card,
            text=str(value),
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#1E293B"
        ).pack(anchor="w")
        
        

# Add Product page
def show_add_product():
    clear_page()

    tk.Label(
        main_area,
        text="Add New Product",
        font=("Arial", 24, "bold"),
        bg="#F4F6F9",
        fg="#1E293B"
    ).pack(anchor="w", padx=30, pady=25)

    form = tk.Frame(main_area, bg="white", padx=30, pady=25)
    form.pack(fill="x", padx=30)

    # Product name
    tk.Label(form, text="Product Name", bg="white").pack(anchor="w")

    name_entry = tk.Entry(form, font=("Arial", 12))
    name_entry.pack(fill="x", pady=8)

    # Category
    tk.Label(form, text="Category", bg="white").pack(anchor="w")

    category_entry = tk.Entry(form, font=("Arial", 12))
    category_entry.pack(fill="x", pady=8)

    # Quantity
    tk.Label(form, text="Quantity", bg="white").pack(anchor="w")

    quantity_entry = tk.Entry(form, font=("Arial", 12))
    quantity_entry.pack(fill="x", pady=8)

    # Expiry date
    tk.Label(
        form,
        text="Expiry Date (YYYY-MM-DD)",
        bg="white"
    ).pack(anchor="w")

    expiry_entry = tk.Entry(form, font=("Arial", 12))
    expiry_entry.pack(fill="x", pady=8)

    # Save product function
    def save_product():

        name = name_entry.get().strip()
        category = category_entry.get().strip()
        quantity = quantity_entry.get().strip()
        expiry = expiry_entry.get().strip()

        if not name or not category or not quantity or not expiry:
            messagebox.showerror("Error", "Please fill all fields!")
            return

        try:
            quantity_value = int(quantity)

            if quantity_value <= 0:
                messagebox.showerror("Error", "Quantity must be greater than zero!")
                return

        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number!")
            return

        try:
            datetime.strptime(expiry, "%Y-%m-%d")

        except ValueError:
            messagebox.showerror("Error", "Enter date in YYYY-MM-DD format!")
            return

        connection = sqlite3.connect("expiryguard.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO products (name, category, quantity, expiry)
            VALUES (?, ?, ?, ?)
        """, (name, category, quantity_value, expiry))

        connection.commit()
        connection.close()

        messagebox.showinfo("Success", "Product saved successfully!")

        show_add_product()
        
    # Save button
    tk.Button(
        form,
        text="Save Product",
        command=save_product,
        bg="#2563EB",
        fg="white",
        font=("Arial", 12, "bold"),
        relief="flat",
        padx=20,
        pady=10
    ).pack(pady=20)

    
    columns = ("Name", "Category", "Quantity", "Expiry Date")

    table = ttk.Treeview(
        main_area,
        columns=columns,
        show="headings"
    )

def show_products():
    clear_page()

    heading = tk.Label(
        main_area,
        text="View Products",
        font=("Arial", 22, "bold"),
        bg="#F4F6F9",
        fg="#1E293B"
    )
    heading.pack(anchor="w", pady=20)

    # Get products from database
    connection = sqlite3.connect("expiryguard.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, category, quantity, expiry
        FROM products
    """)

    records = cursor.fetchall()
    connection.close()

    # Create product table
    columns = ("ID", "Name", "Category", "Quantity", "Expiry Date")

    table = ttk.Treeview(
        main_area,
        columns=columns,
        show="headings",
        height=10
    )

    for column in columns:
        table.heading(column, text=column)
        table.column(column, width=130)

    for record in records:
        table.insert("", "end", values=record)

    # Search and filter section
    search_frame = tk.Frame(main_area, bg="#F4F6F9")
    search_frame.pack(fill="x", pady=10)

    search_entry = tk.Entry(
        search_frame,
        font=("Arial", 12),
        width=20
    )
    search_entry.pack(side="left", padx=5)

    # Search products
    def search_product():
        search_text = search_entry.get().strip()

        for item in table.get_children():
            table.delete(item)

        connection = sqlite3.connect("expiryguard.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, category, quantity, expiry
            FROM products
            WHERE name LIKE ?
        """, ("%" + search_text + "%",))

        results = cursor.fetchall()
        connection.close()

        for record in results:
            table.insert("", "end", values=record)

    # Show all products
    def show_all_products():
        for item in table.get_children():
            table.delete(item)

        for record in records:
            table.insert("", "end", values=record)

    # Category filter
    category_filter = tk.StringVar(value="All Categories")

    category_dropdown = ttk.Combobox(
        search_frame,
        textvariable=category_filter,
        values=["All Categories", "Dairy", "Bakery", "Grocery"],
        state="readonly",
        width=15
    )
    category_dropdown.pack(side="left", padx=5)

    def filter_category():
        selected_category = category_filter.get()

        for item in table.get_children():
            table.delete(item)

        connection = sqlite3.connect("expiryguard.db")
        cursor = connection.cursor()

        if selected_category == "All Categories":
            cursor.execute("""
                SELECT id, name, category, quantity, expiry
                FROM products
            """)
        else:
            cursor.execute("""
                SELECT id, name, category, quantity, expiry
                FROM products
                WHERE category = ?
            """, (selected_category,))

        results = cursor.fetchall()
        connection.close()

        for record in results:
            table.insert("", "end", values=record)

    # Expiry filter
    expiry_filter = tk.StringVar(value="All Products")

    expiry_dropdown = ttk.Combobox(
        search_frame,
        textvariable=expiry_filter,
        values=["All Products", "Expired", "Expiring Soon"],
        state="readonly",
        width=15
    )
    expiry_dropdown.pack(side="left", padx=5)

    def filter_expiry():
        selected_status = expiry_filter.get()
        today = datetime.today().date()

        for item in table.get_children():
            table.delete(item)

        connection = sqlite3.connect("expiryguard.db")
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, category, quantity, expiry
            FROM products
        """)

        results = cursor.fetchall()
        connection.close()

        for record in results:
            expiry_date = datetime.strptime(
                record[4], "%Y-%m-%d"
            ).date()

            days_left = (expiry_date - today).days

            if selected_status == "All Products":
                table.insert("", "end", values=record)

            elif selected_status == "Expired" and days_left < 0:
                table.insert("", "end", values=record)

            elif selected_status == "Expiring Soon" and 0 <= days_left <= 7:
                table.insert("", "end", values=record)

    # Buttons
    tk.Button(
        search_frame,
        text="Search",
        command=search_product,
        bg="#2563EB",
        fg="white"
    ).pack(side="left", padx=5)

    tk.Button(
        search_frame,
        text="Show All",
        command=show_all_products,
        bg="#64748B",
        fg="white"
    ).pack(side="left", padx=5)

    tk.Button(
        search_frame,
        text="Filter Category",
        command=filter_category,
        bg="#0F766E",
        fg="white"
    ).pack(side="left", padx=5)

    tk.Button(
        search_frame,
        text="Filter Expiry",
        command=filter_expiry,
        bg="#D97706",
        fg="white"
    ).pack(side="left", padx=5)

    # Display table
    table.pack(fill="both", expand=True, pady=15)

    


def edit_product():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a product to edit!"
            )
            return

        product_data = table.item(selected[0])
        values = product_data["values"]

        product_id = values[0]

        clear_page()

        tk.Label(
            main_area,
            text="Edit Product",
            font=("Arial", 22, "bold"),
            bg="#F4F6F9"
        ).pack(pady=20)

        fields = ["Product Name", "Category", "Quantity", "Expiry Date"]
        entries = []

        for index, field in enumerate(fields):

            tk.Label(
                main_area,
                text=field,
                bg="#F4F6F9",
                font=("Arial", 11)
            ).pack(anchor="w", padx=50)

            entry = tk.Entry(main_area, font=("Arial", 12), width=35)
            entry.pack(padx=50, pady=5, anchor="w")

            entry.insert(0, str(values[index + 1]))

            entries.append(entry)

        def update_product():

            name = entries[0].get().strip()
            category = entries[1].get().strip()
            quantity = entries[2].get().strip()
            expiry = entries[3].get().strip()

            if not name or not category or not quantity or not expiry:
                messagebox.showerror("Error", "Please fill all fields!")
                return

            try:
                quantity_value = int(quantity)

                if quantity_value <= 0:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Quantity must be a positive number!"
                )
                return

            try:
                datetime.strptime(expiry, "%Y-%m-%d")

            except ValueError:
                messagebox.showerror(
                    "Error",
                    "Enter expiry date in YYYY-MM-DD format!"
                )
                return

            connection = sqlite3.connect("expiryguard.db")
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE products
                SET name = ?, category = ?, quantity = ?, expiry = ?
                WHERE id = ?
            """, (name, category, quantity_value, expiry, product_id))

            connection.commit()
            connection.close()

            messagebox.showinfo(
                "Success",
                "Product updated successfully!"
            )

            show_products()

        tk.Button(
            main_area,
            text="Update Product",
            command=update_product,
            bg="#2563EB",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=8
        ).pack(pady=20)

def delete_product():

        selected = table.selection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a product to delete!"
            )
            return

        values = table.item(selected[0])["values"]
        product_id = values[0]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this product?"
        )

        if confirm:
            connection = sqlite3.connect("expiryguard.db")
            cursor = connection.cursor()

            cursor.execute(
                "DELETE FROM products WHERE id = ?",
                (product_id,)
            )

            connection.commit()
            connection.close()

            messagebox.showinfo(
                "Success",
                "Product deleted successfully!"
            )

            show_products()

tk.Button(
        main_area,
        text="Edit Selected Product",
        command=edit_product,
        bg="#2563EB",
        fg="white",
        font=("Arial", 11, "bold"),
        padx=15,
        pady=8
    ).pack(pady=5)

tk.Button(
        main_area,
        text="Delete Selected Product",
        command=delete_product,
        bg="#DC2626",
        fg="white",
        font=("Arial", 11, "bold"),
        padx=15,
        pady=8
    ).pack(pady=5)
def show_expiry_alerts():
    clear_page()

    today = datetime.today().date()

    heading = tk.Label(
        main_area,
        text="Expiry Alerts",
        font=("Arial", 22, "bold"),
        bg="#F4F6F9",
        fg="#1E293B"
    )
    heading.pack(anchor="w", pady=20)

    connection = sqlite3.connect("expiryguard.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name, expiry FROM products
    """)

    records = cursor.fetchall()
    connection.close()

    expired_count = 0
    expiring_count = 0

    for name, expiry in records:

        expiry_date = datetime.strptime(
            expiry, "%Y-%m-%d"
        ).date()

        days_left = (expiry_date - today).days

        if days_left < 0:
            status = "EXPIRED"
            expired_count += 1

        elif days_left <= 7:
            status = f"Expires in {days_left} days"
            expiring_count += 1

        else:
            continue

        tk.Label(
            main_area,
            text=f"{name} | {status}",
            font=("Arial", 13),
            bg="#F4F6F9",
            fg="#DC2626" if days_left < 0 else "#D97706"
        ).pack(anchor="w", pady=8)

    if expired_count == 0 and expiring_count == 0:
        tk.Label(
            main_area,
            text="No expiry alerts. All products are safe!",
            font=("Arial", 13),
            bg="#F4F6F9",
            fg="#16A34A"
        ).pack(pady=30)

# Sidebar navigation buttons
menu_items = [
    ("Dashboard", show_dashboard),
    ("Add Product", show_add_product),
    ("View Products", show_products),
    ("Expiry Alerts", show_expiry_alerts)
]

for item, function in menu_items:
    tk.Button(
        sidebar,
        text=item,
        command=function,
        font=("Arial", 12),
        bg="#334155",
        fg="white",
        activebackground="#475569",
        activeforeground="white",
        relief="flat",
        width=20,
        pady=10
    ).pack(pady=5)

# Open dashboard initially
show_dashboard()

# Run application
root.mainloop()
