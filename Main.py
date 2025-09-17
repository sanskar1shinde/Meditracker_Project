import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from PIL import Image, ImageTk
from fpdf import FPDF
from tkcalendar import DateEntry
import mysql.connector
from datetime import date, datetime
import threading
import time
import requests
import random
import string
import atexit
import signal
import sys

def get_connection():
    try:
        # Connect to MySQL server without specifying a database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Change this to your MySQL username
            password="root",  # Change this to your MySQL password
            port=3306,
        )

        cursor = conn.cursor()

        # Create the database if it does not exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS meditrackerDB")
        conn.commit()

        # Close the cursor and connection to reconnect with the new database
        cursor.close()
        conn.close()

        # Reconnect using the created database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Change this to your MySQL username
            password="root",  # Change this to your MySQL password
            port=3306,
            database="meditrackerDB",
        )

        return conn

    except mysql.connector.Error as err:
        print("❌ MySQL Error during connection:", err)
        return None


def initialize_database():
    conn = get_connection()
    if conn is None:
        print("❌ Could not establish database connection.")
        return

    try:
        cursor = conn.cursor()

        # USERS TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL,
                fullname VARCHAR(150),
                age INT,
                phone VARCHAR(15),
                gmail VARCHAR(100),
                gender VARCHAR(10),
                birthdate DATE,
                flag INT DEFAULT 1,
                sys_creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """)

        # ADMIN TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL,
                phone VARCHAR(15),
                flag INT DEFAULT 1,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # MEDICINES TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(100),
                quantity INT,
                cost FLOAT,
                purpose VARCHAR(200),
                start_date DATE,
                expiry_date DATE,
                rack VARCHAR(50),
                manufacturer VARCHAR(100),
                flag INT DEFAULT 1,
                sys_creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """)

        # BILLING TABLE
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing_tb (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(255),
                username VARCHAR(255),
                phone VARCHAR(20),
                gender VARCHAR(10),
                age INT,
                email VARCHAR(100),
                address TEXT,
                medicine_name VARCHAR(255),
                type VARCHAR(100),
                quantity INT,
                cost FLOAT,
                purpose VARCHAR(255),
                manufacturer VARCHAR(255),
                gst FLOAT,
                total_price FLOAT,
                flag VARCHAR(10) DEFAULT '1',
                sys_creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """)

        # Default admin insert
        cursor.execute("""
            INSERT IGNORE INTO admin (username, password, phone, flag) 
            VALUES ('admin', 'admin123', '9604875972', 1);
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database and all tables initialized successfully.")

    except mysql.connector.Error as err:
        print("❌ MySQL Error during initialization:", err)

# Run Initialization
initialize_database()





# ----------------- GLOBAL VARIABLES -----------------
attempt_count = 0
root = None
username_entry = None
password_entry = None
STOP_URL = "http://localhost:8080/scheduler/stop"

# -------------------------------------------
# TKINTER UI SETUP
# -------------------------------------------

# --- Registration Page ---
def register_page(username="", password=""):
    root.withdraw()
    reg_win = tk.Toplevel()
    reg_win.title("Meditracker Registration")
    reg_win.geometry("800x700")
    reg_win.resizable(False, False)
    reg_win.configure(bg='white')

    reg_frame = tk.Frame(reg_win, bg='white', bd=5, relief='solid')
    reg_frame.pack(padx=30, pady=30, fill='both', expand=True)

    tk.Label(reg_frame, text="Meditracker Registration", font=('Helvetica', 18, 'bold'), bg='white').pack(pady=10)

    left_frame = tk.Frame(reg_frame, bg='white')
    left_frame.pack(side=tk.LEFT, padx=20, pady=20)

    tk.Label(left_frame, text="Full Name", bg='white', anchor='w').pack(fill='x', pady=5)
    fullname_entry = tk.Entry(left_frame)
    fullname_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="Username", bg='white', anchor='w').pack(fill='x', pady=5)
    username_entry = tk.Entry(left_frame)
    username_entry.insert(0, username)
    username_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="Password", bg='white', anchor='w').pack(fill='x', pady=5)
    password_entry = tk.Entry(left_frame, show='*')
    password_entry.insert(0, password)
    password_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="Phone Number", bg='white', anchor='w').pack(fill='x', pady=5)
    phone_entry = tk.Entry(left_frame)
    phone_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="Gmail", bg='white', anchor='w').pack(fill='x', pady=5)
    gmail_entry = tk.Entry(left_frame)
    gmail_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="Birthdate", bg='white', anchor='w').pack(fill='x', pady=5)
    birthdate_entry = DateEntry(left_frame, date_pattern='yyyy-mm-dd', background='darkblue', foreground='white', borderwidth=2)
    birthdate_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="Age", bg='white', anchor='w').pack(fill='x', pady=5)
    age_var = tk.StringVar()
    age_label = tk.Label(left_frame, textvariable=age_var, bg='white')
    age_label.pack(fill='x', pady=5)

    def update_age(*args):
        try:
            birth_date = datetime.strptime(birthdate_entry.get(), '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            age_var.set(str(age))
        except ValueError:
            age_var.set('')

    birthdate_entry.bind("<FocusOut>", update_age)

    # --- Gender Section ---
    tk.Label(left_frame, text="Gender", bg='white', anchor='w').pack(fill='x', pady=5)
    gender_var = tk.StringVar()
    gender_frame = tk.Frame(left_frame, bg='white')
    gender_frame.pack(fill='x', pady=5)
    tk.Radiobutton(gender_frame, text="Male", variable=gender_var, value="Male", bg='white').pack(side='left', padx=5)
    tk.Radiobutton(gender_frame, text="Female", variable=gender_var, value="Female", bg='white').pack(side='left', padx=5)
    tk.Radiobutton(gender_frame, text="Other", variable=gender_var, value="Other", bg='white').pack(side='left', padx=5)

    # --- Right Button Panel ---
    right_frame = tk.Frame(reg_frame, bg='white')
    right_frame.pack(side=tk.RIGHT, padx=20, pady=20)

    def submit_registration():
        fullname = fullname_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        phone = phone_entry.get().strip()
        gmail = gmail_entry.get().strip()
        birthdate = birthdate_entry.get()
        age = age_var.get()
        gender = gender_var.get()

        if not fullname or not username or not password or not phone or not gmail or not birthdate or not gender:
            messagebox.showerror("Error", "All fields are mandatory, including gender.")
            return

        if username.lower() == "admin":
            messagebox.showerror("Error", "Username 'admin' is reserved. Please choose a different username.")
            return

        if not re.match(r"^[A-Za-z\s]+$", fullname):
            messagebox.showerror("Error", "Full Name must consist of alphabets and spaces only.")
            return

        if not re.match(r"^[A-Za-z0-9]+$", username):
            messagebox.showerror("Error", "Username must consist of alphabets and numbers only.")
            return

        if not phone.isdigit() or len(phone) != 10:
            messagebox.showerror("Error", "Phone number must be at least 10 digits long.")
            return

        if not age:
            messagebox.showerror("Error", "Age cannot be empty.")
            return

        if int(age) < 18:
            messagebox.showerror("Error", "You must be at least 18 years old to register.")
            return

        if not gmail.endswith('@gmail.com'):
            messagebox.showerror("Error", "Gmail must end with @gmail.com")
            return

        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,12}$", password):
            messagebox.showerror("Error", "Password must be 8-12 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE flag NOT IN (0, -1) and username=%s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists. Please choose a different one.")
                return

            cursor.execute(
                "INSERT INTO users (username, password, fullname, birthdate, age, phone, gmail, gender, sys_creation_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())",
                (username, password, fullname, birthdate, age, phone, gmail, gender)
            )
            conn.commit()
            messagebox.showinfo("Success", "Registration successful")
            reg_win.destroy()
            root.deiconify()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Registration failed: {e}")

    tk.Button(right_frame, text="Register", command=submit_registration, bg='green', fg='white').pack(pady=20)
    tk.Button(right_frame, text="Cancel", command=lambda: [reg_win.destroy(), root.deiconify()], bg='red', fg='white').pack(pady=20)

    show_password_var = tk.BooleanVar()

    def show_password():
        if show_password_var.get():
            password_entry.config(show='')  # Show the password
        else:
            password_entry.config(show='*')  # Hide the password

    tk.Checkbutton(right_frame, text="Show Password", variable=show_password_var, command=show_password).pack(pady=5)


# --- Forgot Password Page for Users ---
def forgot_password_user_page(username):
    root.withdraw()
    forgot_win = tk.Toplevel()
    forgot_win.title("User  Forgot Password")
    forgot_win.geometry("600x600")
    forgot_win.resizable(False, False)
    forgot_win.configure(bg='white')

    forgot_frame = tk.Frame(forgot_win, bg='white', bd=5, relief='solid')
    forgot_frame.pack(padx=30, pady=30, fill='both', expand=True)

    tk.Label(forgot_frame, text="User  Forgot Password", font=('Helvetica', 18, 'bold'), bg='white').pack(pady=10)

    # Left side for title
    left_frame = tk.Frame(forgot_frame, bg='white')
    left_frame.pack(side=tk.LEFT, padx=20, pady=20)

    tk.Label(left_frame, text="Username", bg='white', anchor='w').pack(fill='x', pady=5)
    username_entry = tk.Entry(left_frame)
    username_entry.insert(0, username)
    username_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="Phone Number", bg='white', anchor='w').pack(fill='x', pady=5)
    phone_entry = tk.Entry(left_frame)
    phone_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="New Password", bg='white', anchor='w').pack(fill='x', pady=5)
    new_password_entry = tk.Entry(left_frame, show='*')
    new_password_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="Confirm Password", bg='white', anchor='w').pack(fill='x', pady=5)
    confirm_password_entry = tk.Entry(left_frame, show='*')
    confirm_password_entry.pack(fill='x', pady=5)

    # Right side for buttons
    right_frame = tk.Frame(forgot_frame, bg='white')
    right_frame.pack(side=tk.RIGHT, padx=20, pady=20)

    def submit_forgot_password():
        username = username_entry.get()
        phone = phone_entry.get()
        new_password = new_password_entry.get()
        confirm_password = confirm_password_entry.get()

        if not username or not phone or not new_password or not confirm_password:
            messagebox.showerror("Error", "All fields are mandatory.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,12}$", new_password):
            messagebox.showerror("Error", "Password must be 8-12 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE flag NOT IN (0, -1) and username=%s AND phone=%s", (username, phone))
            user = cursor.fetchone()
            if user:
                cursor.execute("UPDATE users SET password=%s WHERE flag NOT IN (0, -1) and username=%s AND phone=%s", (new_password, username, phone))
                conn.commit()
                messagebox.showinfo("Success", "Password updated successfully")
                forgot_win.destroy()
                root.deiconify()  # Show the login window again
            else:
                messagebox.showerror("Error", "Invalid username or phone number")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Password update failed: {e}")

    tk.Button(right_frame, text="Update Password", command=submit_forgot_password, bg='blue', fg='white').pack(pady=20)
    tk.Button(right_frame, text="Cancel", command=lambda: [forgot_win.destroy(), root.deiconify()], bg='red', fg='white').pack(pady=20)

    # Show Password Functionality
    show_password_var = tk.BooleanVar()

    def show_password():
        if show_password_var.get():
            new_password_entry.config(show='')  # Show the password
            confirm_password_entry.config(show='')  # Show the password
        else:
            new_password_entry.config(show='*')  # Hide the password
            confirm_password_entry.config(show='*')  # Hide the password

    tk.Checkbutton(right_frame, text="Show Password", variable=show_password_var, command=show_password).pack(pady=5)


# --- Forgot Password Page for Admin ---
def forgot_password_admin_page():
    root.withdraw()
    forgot_win = tk.Toplevel()
    forgot_win.title("Admin Forgot Password")
    forgot_win.geometry("600x600")
    forgot_win.resizable(False, False)
    forgot_win.configure(bg='white')

    forgot_frame = tk.Frame(forgot_win, bg='white', bd=5, relief='solid')
    forgot_frame.pack(padx=30, pady=30, fill='both', expand=True)

    tk.Label(forgot_frame, text="Admin Forgot Password", font=('Helvetica', 18, 'bold'), bg='white').pack(pady=10)

    # Left side for title
    left_frame = tk.Frame(forgot_frame, bg='white')
    left_frame.pack(side=tk.LEFT, padx=20, pady=20)

    tk.Label(left_frame, text="Phone Number", bg='white', anchor='w').pack(fill='x', pady=5)
    phone_entry = tk.Entry(left_frame)
    phone_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="New Password", bg='white', anchor='w').pack(fill='x', pady=5)
    new_password_entry = tk.Entry(left_frame, show='*')
    new_password_entry.pack(fill='x', pady=5)

    tk.Label(left_frame, text="Confirm Password", bg='white', anchor='w').pack(fill='x', pady=5)
    confirm_password_entry = tk.Entry(left_frame, show='*')
    confirm_password_entry.pack(fill='x', pady=5)

    # Right side for buttons
    right_frame = tk.Frame(forgot_frame, bg='white')
    right_frame.pack(side=tk.RIGHT, padx=20, pady=20)

    def submit_forgot_password():
        phone = phone_entry.get()
        new_password = new_password_entry.get()
        confirm_password = confirm_password_entry.get()

        if not phone or not new_password or not confirm_password:
            messagebox.showerror("Error", "All fields are mandatory.")
            return

        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,12}$", new_password):
            messagebox.showerror("Error", "Password must be 8-12 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE flag NOT IN (0, -1) and  phone=%s", (phone,))
            admin = cursor.fetchone()
            if admin:
                cursor.execute("UPDATE admin SET password=%s WHERE flag NOT IN (0, -1) and  phone=%s", (new_password, phone))
                conn.commit()
                messagebox.showinfo("Success", "Password updated successfully")
                forgot_win.destroy()
                root.deiconify()  # Show the login window again
            else:
                messagebox.showerror("Error", "Invalid phone number")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Password update failed: {e}")

    tk.Button(right_frame, text="Update Password", command=submit_forgot_password, bg='blue', fg='white').pack(pady=20)
    tk.Button(right_frame, text="Cancel", command=lambda: [forgot_win.destroy(), root.deiconify()], bg='red', fg='white').pack(pady=20)

    # Show Password Functionality
    show_password_var = tk.BooleanVar()

    def show_password():
        if show_password_var.get():
            new_password_entry.config(show='')  # Show the password
            confirm_password_entry.config(show='')  # Show the password
        else:
            new_password_entry.config(show='*')  # Hide the password
            confirm_password_entry.config(show='*')  # Hide the password

    tk.Checkbutton(right_frame, text="Show Password", variable=show_password_var, command=show_password).pack(pady=5)

# Add product to the store
def open_add_product_window():
    root.withdraw()  # Hide the main window
    add_win = tk.Toplevel()
    add_win.title("Add Product to Stock")
    add_win.geometry("1100x650")
    add_win.resizable(False, False)

    # ---------- Background Image ----------
    bg_image = Image.open("resources/img2.png")
    bg_image = bg_image.resize((2000, 1000))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(add_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # ---------- Form Frame ----------
    form_frame = tk.Frame(add_win, bg="white", bd=2, relief="groove")
    form_frame.place(x=30, y=30, width=450, height=500)

    tk.Label(form_frame, text="ENTER NEW PRODUCT DATA TO THE STOCK", font=("Arial", 11, "bold"), bg="white").pack(
        pady=10)

    # ---------- Form Variables ----------
    name_var = tk.StringVar()
    type_var = tk.StringVar()
    quantity_var = tk.StringVar()
    cost_var = tk.StringVar()
    purpose_var = tk.StringVar()
    rack_var = tk.StringVar()
    manufacturer_var = tk.StringVar()

    # ---------- Form Fields ----------
    tk.Label(form_frame, text="Name:", anchor="w", bg="white", font=("Arial", 10)).place(x=10, y=50, width=120)
    tk.Entry(form_frame, textvariable=name_var).place(x=140, y=50)

    tk.Label(form_frame, text="Type:", anchor="w", bg="white", font=("Arial", 10)).place(x=10, y=80, width=120)
    tk.Entry(form_frame, textvariable=type_var).place(x=140, y=80)

    tk.Label(form_frame, text="Quantity:", anchor="w", bg="white", font=("Arial", 10)).place(x=10, y=110, width=120)
    tk.Entry(form_frame, textvariable=quantity_var).place(x=140, y=110)

    tk.Label(form_frame, text="Cost:", anchor="w", bg="white", font=("Arial", 10)).place(x=10, y=140, width=120)
    tk.Entry(form_frame, textvariable=cost_var).place(x=140, y=140)

    tk.Label(form_frame, text="Purpose:", anchor="w", bg="white", font=("Arial", 10)).place(x=10, y=170, width=120)
    tk.Entry(form_frame, textvariable=purpose_var).place(x=140, y=170)

    tk.Label(form_frame, text="Start Date:", anchor="w", bg="white", font=("Arial", 10)).place(x=10, y=200, width=120)
    start_date = DateEntry(form_frame, width=18, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    start_date.place(x=140, y=200)

    tk.Label(form_frame, text="Expiry Date:", anchor="w", bg="white", font=("Arial", 10)).place(x=10, y=230, width=120)
    expiry_date = DateEntry(form_frame, width=18, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    expiry_date.place(x=140, y=230)

    tk.Label(form_frame, text="Rack:", anchor="w", bg="white", font=("Arial", 10)).place(x=10, y=260, width=120)
    tk.Entry(form_frame, textvariable=rack_var).place(x=140, y=260)

    tk.Label(form_frame, text="Manufacturer:", anchor="w", bg="white", font=("Arial", 10)).place(x=10, y=290, width=120)
    tk.Entry(form_frame, textvariable=manufacturer_var).place(x=140, y=290)

    # ---------- Submit Logic ----------
    def submit_data():
        try:
            quantity = int(quantity_var.get().strip())
            cost = float(cost_var.get().strip())
            rack = int(rack_var.get().strip())
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity, Cost, and Rack must be numeric values.")
            return

        values = {
            "name": name_var.get().strip(),
            "type": type_var.get().strip(),
            "quantity": quantity,
            "cost": cost,
            "purpose": purpose_var.get().strip(),
            "start": start_date.get_date(),
            "expiry": expiry_date.get_date(),
            "rack": rack,
            "manufacturer": manufacturer_var.get().strip()
        }

        # Empty check
        if any(str(v) == "" for v in values.values()):
            messagebox.showerror("Validation Error", "All fields are required.")
            return

        # Date validation
        today = datetime.today().date()
        if values["start"] > today:
            messagebox.showerror("Date Error", "Start date cannot be in the future.")
            return
        if values["expiry"] <= today:
            messagebox.showerror("Date Error", "Expiry date must be after today.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Check if the product name already exists
            cursor.execute("SELECT COUNT(*) FROM medicines WHERE flag NOT IN (0, -1) and name = %s", (values["name"],))
            exists = cursor.fetchone()[0]

            if exists > 0:
                messagebox.showinfo("Product Exists",
                                    "Please update the product details from the update tab if you want to update.")
                return

            # Insert the new product
            cursor.execute('''
                INSERT INTO medicines 
                (name, type, quantity, cost, purpose, start_date, expiry_date, rack, manufacturer)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (values["name"], values["type"], values["quantity"], values["cost"],
                  values["purpose"], values["start"], values["expiry"], values["rack"], values["manufacturer"]))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Medicine data added successfully!")
            refresh_data()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ---------- Reset Logic ----------
    def reset_form():
        name_var.set("")
        type_var.set("")
        quantity_var.set("")
        cost_var.set("")
        purpose_var.set("")
        rack_var.set("")
        manufacturer_var.set("")
        start_date.set_date(datetime.today())
        expiry_date.set_date(datetime.today())

    # ---------- Refresh Table ----------
    def refresh_data():
        for row in table.get_children():
            table.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, type, quantity, cost, purpose, expiry_date, rack, manufacturer FROM medicines WHERE flag NOT IN (0, -1) ")
            for row in cursor.fetchall():
                table.insert("", "end", values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Buttons ----------
    tk.Button(form_frame, text="Submit", bg="green", fg="white", font=("Arial", 10, "bold"), command=submit_data).place(
        x=80, y=430, width=100)
    tk.Button(form_frame, text="Reset", bg="gray", fg="white", font=("Arial", 10, "bold"), command=reset_form).place(
        x=200, y=430, width=100)

    # ---------- Table Frame ----------
    table_frame = tk.Frame(add_win)
    table_frame.place(x=500, y=30, width=570, height=500)

    x_scroll = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
    y_scroll = tk.Scrollbar(table_frame, orient=tk.VERTICAL)
    table = ttk.Treeview(table_frame, columns=("Name", "Type", "Qty", "Cost", "Purpose", "Exp", "Rack", "Manufacturer"),
                         show="headings", xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
    x_scroll.config(command=table.xview)
    y_scroll.config(command=table.yview)
    x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    table.pack(fill=tk.BOTH, expand=True)

    for col in table["columns"]:
        table.heading(col, text=col)
        table.column(col, width=100)

    # ---------- Refresh and Main Menu Buttons ----------
    tk.Button(add_win, text="Refresh Stock", command=refresh_data, bg="#007BFF", fg="white",
              font=("Arial", 10, "bold")).place(x=550, y=550, width=150)

    # Modify the command to show the main window again
    tk.Button(add_win, text="Main Menu", command=lambda: [add_win.destroy()], bg="red", fg="white",
              font=("Arial", 10, "bold")).place(x=720, y=550, width=150)

    refresh_data()


# ---------- For update products. ----------
def open_update_product():
    def fetch_product_details():
        name = entry_name.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter the medicine name.")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT type, quantity, cost, purpose, start_date, expiry_date, rack, manufacturer FROM medicines WHERE flag NOT IN (0, -1) and name=%s", (name,))
            result = cursor.fetchone()
            conn.close()
            if result:
                entry_type.delete(0, tk.END)
                entry_type.insert(0, result[0])
                entry_quantity.delete(0, tk.END)
                entry_quantity.insert(0, result[1])
                entry_cost.delete(0, tk.END)
                entry_cost.insert(0, result[2])
                entry_purpose.delete(0, tk.END)
                entry_purpose.insert(0, result[3])
                entry_start_date.set_date(result[4])
                entry_expiry_date.set_date(result[5])
                entry_rack.delete(0, tk.END)
                entry_rack.insert(0, result[6])
                entry_manufacturer.delete(0, tk.END)
                entry_manufacturer.insert(0, result[7])
            else:
                messagebox.showinfo("Not Found", "No medicine found with that name.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_product():
        name = entry_name.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Medicine name cannot be empty.")
            return

        # Validate all fields
        if not entry_type.get() or not entry_quantity.get() or not entry_cost.get() or not entry_purpose.get() or not entry_rack.get() or not entry_manufacturer.get():
            messagebox.showwarning("Input Error", "All fields are mandatory.")
            return

        try:
            quantity = int(entry_quantity.get())
            cost = float(entry_cost.get())
            rack = int(entry_rack.get())
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity, Cost, and Rack must be numeric values.")
            return

        # Validate dates
        start_date = entry_start_date.get_date()
        expiry_date = entry_expiry_date.get_date()
        today = datetime.today().date()

        if start_date >= today:
            messagebox.showerror("Date Error", "Start date must be a past date.")
            return
        if expiry_date <= today:
            messagebox.showerror("Date Error", "Expiry date must be a future date.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            update_query = """
                UPDATE medicines 
                SET type=%s, quantity=%s, cost=%s, purpose=%s, start_date=%s, expiry_date=%s, 
                    rack=%s, manufacturer=%s, update_time=%s 
                WHERE flag NOT IN (0, -1) and name=%s
            """
            data = (
                entry_type.get(),
                quantity,
                cost,
                entry_purpose.get(),
                start_date,
                expiry_date,
                rack,
                entry_manufacturer.get(),
                datetime.now(),
                name
            )
            cursor.execute(update_query, data)
            conn.commit()
            conn.close()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Product details updated successfully.")
                add_win.destroy()
            else:
                messagebox.showwarning("Not Found", "No product found with that name.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ------------------ UI Setup ------------------
    root.withdraw()
    add_win = tk.Toplevel()
    add_win.title("Update Product Details")
    add_win.geometry("800x600")
    add_win.resizable(False, False)

    # Background Image
    bg_image = Image.open("resources/img2.png")
    bg_image = bg_image.resize((1500, 1000))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(add_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Frame for form
    form_frame = tk.Frame(add_win, bg="white", bd=2, relief=tk.RIDGE)
    form_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # ------------------ Fields ------------------
    labels = [
        "Medicine Name", "Type", "Quantity", "Cost", "Purpose",
        "Start Date", "Expiry Date", "Rack", "Manufacturer"
    ]
    entries = []

    for i, text in enumerate(labels):
        lbl = tk.Label(form_frame, text=text, bg="white", font=("Arial", 12, "bold"))
        lbl.grid(row=i, column=0, padx=10, pady=5, sticky='e')

    entry_name = tk.Entry(form_frame, width=30, font=("Arial", 12))
    entry_type = tk.Entry(form_frame, width=30, font=("Arial", 12))
    entry_quantity = tk.Entry(form_frame, width=30, font=("Arial", 12))
    entry_cost = tk.Entry(form_frame, width=30, font=("Arial", 12))
    entry_purpose = tk.Entry(form_frame, width=30, font=("Arial", 12))
    entry_start_date = DateEntry(form_frame, width=27, font=("Arial", 12))
    entry_expiry_date = DateEntry(form_frame, width=27, font=("Arial", 12))
    entry_rack = tk.Entry(form_frame, width=30, font=("Arial", 12))
    entry_manufacturer = tk.Entry(form_frame, width=30, font=("Arial", 12))

    widgets = [
        entry_name, entry_type, entry_quantity, entry_cost, entry_purpose,
        entry_start_date, entry_expiry_date, entry_rack, entry_manufacturer
    ]

    for i, widget in enumerate(widgets):
        widget.grid(row=i, column=1, padx=10, pady=5)

    # ------------------ Buttons ------------------
    btn_fetch = tk.Button(form_frame, text="Fetch", command=fetch_product_details, bg="#28a745", fg="white",
                          font=("Arial", 11, "bold"))
    btn_fetch.grid(row=0, column=2, padx=10, pady=5)

    # Place both buttons in the same row
    btn_update = tk.Button(form_frame, text="Update", command=update_product, bg="#007bff", fg="white",
                           font=("Arial", 12, "bold"))
    btn_update.grid(row=len(labels), column=0, padx=10, pady=20)

    # Main Menu button to close the current window and show the main window
    btn_main_menu = tk.Button(form_frame, text="Main Menu", command=lambda: [add_win.destroy()],
                              bg="red", fg="white",
                              font=("Arial", 10, "bold"))
    btn_main_menu.grid(row=len(labels), column=1, padx=10, pady=20)

def generate_random_username():
    return "newuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

def is_valid_email(email):
    return re.fullmatch(r"[^@\s]+@gmail\.com", email)

def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10

def is_valid_age(age):
    return age.isdigit() and 0 < int(age) < 120

def is_valid_float(val):
    try:
        float(val)
        return True
    except:
        return False

def is_valid_int(val):
    return val.isdigit()

def generate_random_username():
    return "newuser_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

def is_valid_email(email):
    return re.fullmatch(r"[^@\s]+@gmail\.com", email)

def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10

def is_valid_age_billing(age):
    return age.isdigit() and 0 < int(age) < 100

def is_valid_float(val):
    try:
        float(val)
        return True
    except:
        return False

def is_valid_int(val):
    return val.isdigit()

def open_billing():
    def fetch_user_details():
        phone = phone_entry.get()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, fullname, age, gmail, gender FROM users WHERE flag NOT IN (0,-1) and phone=%s", (phone,))
        row = cursor.fetchone()
        if row:
            username_entry.delete(0, tk.END)
            username_entry.insert(0, row[0])
            name_entry.delete(0, tk.END)
            name_entry.insert(0, row[1])
            age_entry.delete(0, tk.END)
            age_entry.insert(0, row[2])
            email_entry.delete(0, tk.END)
            email_entry.insert(0, row[3])
            gender_entry.delete(0, tk.END)
            gender_entry.insert(0, row[4])
        else:
            new_username = generate_random_username()
            username_entry.delete(0, tk.END)
            username_entry.insert(0, new_username)
            messagebox.showinfo("Info", "User not found. Please fill in the details manually.")
        conn.close()

    def reset_fields():
        for entry in [username_entry, name_entry, phone_entry, gender_entry, age_entry, email_entry]:
            entry.delete(0, tk.END)
        address_entry.delete("1.0", tk.END)
        med_search_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
        med_dropdown.set('')
        med_info_var.set("")
        final_tree.delete(*final_tree.get_children())

    def search_medicines():
        query = med_search_entry.get()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM medicines WHERE flag NOT IN (0, -1) and name LIKE %s", (f"%{query}%",))
        medicines = [row[0] for row in cursor.fetchall()]
        med_dropdown['values'] = medicines
        conn.close()

    def update_medicine_info(event):
        med_name = med_dropdown.get()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, type, quantity, cost, purpose, manufacturer, start_date, expiry_date FROM medicines WHERE quantity NOT IN (0) and flag NOT IN (0, -1) and name=%s", (med_name,))
        med_info = cursor.fetchone()
        cursor.fetchall()
        conn.close()
        if med_info:
            med_info_var.set(f"Name: {med_info[0]}, Type: {med_info[1]}, Cost: Rs.{med_info[3]}, MFD: {med_info[6]}, Exp: {med_info[7]}")

    temp_stock_updates = []  # Global list to track deducted stock

    def add_medicine_to_bill():
        med_name = med_dropdown.get()
        quantity = quantity_entry.get()
        if not med_name:
            messagebox.showerror("Error", "Please select a medicine.")
            return
        if not is_valid_int(quantity):
            messagebox.showerror("Validation Error", "Quantity must be a valid integer")
            return

        quantity = int(quantity)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, type, quantity, cost, purpose, manufacturer FROM medicines WHERE flag NOT IN (0, -1) and name=%s",
                       (med_name,))
        row = cursor.fetchone()
        cursor.fetchall()

        if not row:
            messagebox.showerror("Error", "Medicine not found.")
            return

        name, mtype, stock, cost, purpose, mfr = row
        if quantity > stock:
            messagebox.showerror("Stock Error", f"Only {stock} units available.")
            return

        if not is_valid_float(str(cost)):
            messagebox.showerror("Validation Error", "Cost must be a valid float")
            return

        total_cost = round(cost * quantity, 2)
        gst = round(0.18 * total_cost, 2)
        total = round(total_cost + gst, 2)

        final_tree.insert("", tk.END, values=(name, mtype, quantity, cost, purpose, mfr, gst, total))

        cursor.execute("UPDATE medicines SET quantity=%s WHERE flag NOT IN (0, -1) and name=%s", (stock - quantity, med_name))
        conn.commit()
        conn.close()

        # Track this update for possible rollback
        temp_stock_updates.append((med_name, quantity))

    def restore_stock():
        if not temp_stock_updates:
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            for med_name, qty in temp_stock_updates:
                cursor.execute("UPDATE medicines SET quantity = quantity + %s WHERE flag NOT IN (0, -1) and name = %s", (qty, med_name))
            conn.commit()
            conn.close()
            temp_stock_updates.clear()
            messagebox.showinfo("Stock Restored", "Uncommitted stock changes have been rolled back.")
        except Exception as e:
            messagebox.showerror("DB Error", f"Could not restore stock: {e}")

    def generate_pdf_and_save():
        items = final_tree.get_children()
        if not items:
            messagebox.showwarning("Empty", "No medicine added to bill.")
            return

        if not validate_user_fields():
            return

        customer_name = name_entry.get()
        username = username_entry.get()
        phone = phone_entry.get()
        gender = gender_entry.get()
        age = age_entry.get()
        email = email_entry.get()
        address = address_entry.get("1.0", tk.END).strip()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(190, 10, "Pharmacy Billing Invoice", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", "", 12)
        pdf.cell(100, 10, f"Customer Name: {customer_name}", ln=True)
        pdf.cell(100, 10, f"Phone: {phone} | Gender: {gender} | Age: {age}", ln=True)
        pdf.multi_cell(0, 10, f"Email: {email}\nAddress: {address}")
        pdf.ln(5)

        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 10, "Medicines", ln=True)
        pdf.set_font("Arial", "", 10)

        total_price = 0
        try:
            for item in items:
                values = final_tree.item(item, "values")
                med_name, mtype, qty, cost, purpose, mfr, gst, total = values
                pdf.cell(0, 8, f"{med_name} ({mtype}), Qty: {qty}, Cost: {cost}, GST: {gst}, Total: {total}", ln=True,
                         border=1)
                total_price += float(total)

                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO billing_tb (customer_name, username, phone, gender, age, email, address, medicine_name, type, quantity, cost, purpose, manufacturer, gst, total_price)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                customer_name, username, phone, gender, age, email, address, med_name, mtype, qty, cost, purpose, mfr,
                gst, total))
                conn.commit()
                conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not save billing data: {e}")
            restore_stock()  # Rollback on failure
            return

        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Grand Total: Rs. {round(total_price, 2)}", ln=True, border=1)
        try:
            pdf.output("final_bill.pdf")
        except Exception as e:
            messagebox.showerror("PDF Error", f"Could not generate PDF: {e}")
            restore_stock()  # Rollback if PDF generation fails
            return

        temp_stock_updates.clear()  # Clear after successful save
        messagebox.showinfo("Success", "PDF generated and billing saved.")
        billing_win.destroy()

    def validate_user_fields():
        phone = phone_entry.get()
        email = email_entry.get()
        age = age_entry.get()

        if not is_valid_phone(phone):
            messagebox.showerror("Validation Error", "Phone must be a 10-digit number")
            return False
        if not is_valid_email(email):
            messagebox.showerror("Validation Error", "Email must end with @gmail.com")
            return False
        if not is_valid_age(age):
            messagebox.showerror("Validation Error", "Age must be a valid number")
            return False

        age = int(age)
        if 18 < age > 100:
            messagebox.showerror("Validation Error", "User must be 18 years old or elder.")
            return False

        return True

    # GUI setup
    root.withdraw()
    billing_win = tk.Toplevel()
    billing_win.title("Pharmacy Billing")
    billing_win.geometry("1350x850")
    billing_win.config(bg="#f0f4f7")

    tk.Label(billing_win, text="Pharmacy Billing Panel", font=("Helvetica", 20, "bold"), bg="#f0f4f7", fg="#333").pack(
        pady=10)

    user_frame = tk.LabelFrame(billing_win, text="Customer Details", font=("Arial", 12, "bold"), bg="#ffffff", padx=10,
                               pady=10, relief="solid", bd=2)
    user_frame.place(x=20, y=60, width=620, height=320)

    username_entry = tk.Entry(user_frame, font=("Arial", 12), width=30)
    name_entry = tk.Entry(user_frame, font=("Arial", 12), width=30)
    phone_entry = tk.Entry(user_frame, font=("Arial", 12), width=30)
    gender_entry = tk.Entry(user_frame, font=("Arial", 12), width=30)
    age_entry = tk.Entry(user_frame, font=("Arial", 12), width=30)
    email_entry = tk.Entry(user_frame, font=("Arial", 12), width=30)
    address_entry = tk.Text(user_frame, font=("Arial", 12), width=30, height=3)

    fields = ["Username", "Customer Name", "Phone", "Gender", "Age", "Gmail", "Address"]
    entries = [username_entry, name_entry, phone_entry, gender_entry, age_entry, email_entry, address_entry]
    for i, (label, entry) in enumerate(zip(fields, entries)):
        tk.Label(user_frame, text=label + ":", font=("Arial", 12), bg="#ffffff").grid(row=i, column=0, sticky="w")
        entry.grid(row=i, column=1, pady=5)

    tk.Button(user_frame, text="Fetch", command=fetch_user_details, bg="#3498db", fg="white").grid(row=2, column=2)
    tk.Button(user_frame, text="Reset", command=reset_fields, bg="#e67e22", fg="white").grid(row=7, column=1,
                                                                                             sticky="e")

    med_frame = tk.LabelFrame(billing_win, text="Medicine Info", font=("Arial", 12, "bold"), bg="#ffffff", padx=10,
                              pady=10, relief="solid", bd=2)
    med_frame.place(x=20, y=400, width=620, height=200)

    med_search_entry = tk.Entry(med_frame, font=("Arial", 12), width=25)
    tk.Button(med_frame, text="Search", command=search_medicines, bg="#007acc", fg="white").grid(row=0, column=2)

    med_dropdown = ttk.Combobox(med_frame, font=("Arial", 12), width=25)
    med_dropdown.bind("<<ComboboxSelected>>", update_medicine_info)
    quantity_entry = tk.Entry(med_frame, font=("Arial", 12), width=10)
    med_info_var = tk.StringVar()
    med_info_label = tk.Label(med_frame, textvariable=med_info_var, font=("Arial", 10), bg="#ffffff")

    tk.Label(med_frame, text="Medicine Name:", font=("Arial", 12), bg="#ffffff").grid(row=0, column=0)
    med_search_entry.grid(row=0, column=1)
    med_dropdown.grid(row=1, column=0, padx=5, pady=5)
    tk.Label(med_frame, text="Quantity:", font=("Arial", 12), bg="#ffffff").grid(row=1, column=1)
    quantity_entry.grid(row=1, column=2)
    med_info_label.grid(row=2, column=0, columnspan=3, sticky="w")

    tk.Button(med_frame, text="Add", command=add_medicine_to_bill, bg="#2ecc71", fg="white").grid(row=3, column=1)

    info_preview = tk.LabelFrame(billing_win, text="Customer Preview", font=("Arial", 12, "bold"), bg="#ffffff",
                                 padx=10, pady=10, relief="solid", bd=2)
    info_preview.place(x=660, y=60, width=660, height=230)

    labels = [
        ("Name", name_entry),
        ("Username", username_entry),
        ("Phone", phone_entry),
        ("Gender", gender_entry),
        ("Age", age_entry),
        ("Email", email_entry),
        ("Address", address_entry)
    ]

    preview_values = {}
    for idx, (label_text, widget) in enumerate(labels):
        value = widget.get("1.0", "end-1c") if isinstance(widget, tk.Text) else widget.get()
        preview_values[label_text] = tk.StringVar(value=value)
        tk.Label(info_preview, text=f"{label_text}:", font=("Arial", 11, "bold"), bg="#ffffff").grid(row=idx, column=0,
                                                                                                     sticky="w")
        tk.Label(info_preview, textvariable=preview_values[label_text], font=("Arial", 11), bg="#ffffff").grid(row=idx,
                                                                                                               column=1,
                                                                                                               sticky="w")

    def update_preview():
        for label_text, widget in labels:
            val = widget.get("1.0", "end-1c") if isinstance(widget, tk.Text) else widget.get()
            preview_values[label_text].set(val)

    tk.Button(info_preview, text="Add to Preview", command=update_preview, bg="#2980b9", fg="white").grid(
        row=len(labels), column=1, pady=10, sticky="e")

    final_frame = tk.LabelFrame(billing_win, text="Billing Summary", font=("Arial", 12, "bold"), bg="#ffffff",
                                relief="solid", bd=2)
    final_frame.place(x=660, y=300, width=660, height=400)

    final_tree = ttk.Treeview(final_frame, columns=("Name", "Type", "Qty", "Cost", "Purpose", "MFR", "GST", "Total"),
                              show="headings")
    for col in final_tree["columns"]:
        final_tree.heading(col, text=col)
    final_tree.pack(side="left", expand=True, fill="both")

    scrollbar = ttk.Scrollbar(final_frame, orient="vertical", command=final_tree.yview)
    final_tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Create a frame to hold both buttons in the same row
    button_frame = tk.Frame(billing_win, bg="#f0f4f7")
    button_frame.place(x=850, y=720)

    # Button to save data and generate PDF bill
    tk.Button(button_frame, text="Save & Generate Bill", command=generate_pdf_and_save,
              bg="#1abc9c", fg="white", font=("Arial", 12), width=25).grid(row=0, column=0, padx=10)

    # Cancel button to close window and restore stock
    tk.Button(button_frame, text="Cancel", command=lambda: [billing_win.destroy()],
              bg="#e74c3c", fg="white", font=("Arial", 12), width=15).grid(row=0, column=1)

    # Start the billing UI event loop
    billing_win.mainloop()


# Delete product
def open_delete_product():
    # Create a new window for deleting a product
    root.withdraw()
    delete_win = tk.Toplevel()
    delete_win.title("Delete Product from Stock")
    delete_win.geometry("800x550")
    delete_win.resizable(False, False)

    # ---------- Background Image ----------
    bg_image = Image.open("resources/img2.png")
    bg_image = bg_image.resize((1500, 1000))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(delete_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    search_frame = tk.Frame(delete_win, bg="white", bd=2, relief=tk.RIDGE)
    search_frame.place(x=150, y=30, width=500, height=100)

    tk.Label(search_frame, text="Enter Medicine Name:", bg="white", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)

    entry_name = tk.Entry(search_frame, width=30, font=("Arial", 12))
    entry_name.grid(row=1, column=0, padx=10, pady=5)

    def fetch_product_details():
        prefix = entry_name.get().strip()
        if not prefix:
            messagebox.showwarning("Input Error", "Please enter the starting characters of the medicine name.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Use LIKE to fetch medicines starting with the specified characters
            cursor.execute(
                "SELECT name, type, quantity, cost, purpose, start_date, expiry_date, rack, manufacturer FROM medicines WHERE name LIKE %s AND flag NOT IN (0, -1)",
                (prefix + '%',))  # Adding '%' to match any characters after the prefix
            results = cursor.fetchall()
            conn.close()

            # Clear previous entries in the table
            for row in table.get_children():
                table.delete(row)

            if results:
                for result in results:
                    table.insert("", "end", values=result)  # Insert each result into the table
            else:
                messagebox.showinfo("Not Found", "No medicines found starting with those characters.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn_fetch = tk.Button(search_frame, text="Fetch Details", command=fetch_product_details, bg="#28a745", fg="white",
                          font=("Arial", 12))
    btn_fetch.grid(row=1, column=1, padx=10, pady=5)

    table_frame = tk.Frame(delete_win)
    table_frame.place(x=30, y=150, width=750, height=300)

    # Remove "Select" column from the columns definition
    columns = ("Name", "Type", "Quantity", "Cost", "Purpose", "Start Date", "Expiry Date", "Rack", "Manufacturer")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=100)

    # Create a vertical scrollbar
    v_scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
    table.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a horizontal scrollbar
    h_scrollbar = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=table.xview)
    table.configure(xscrollcommand=h_scrollbar.set)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Pack the Treeview
    table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def delete_product():
        selected_items = table.selection()
        if not selected_items:
            messagebox.showwarning("Selection Error", "Please select a product to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected product?")
        if confirm:
            try:
                # Get the name from the selected item
                name = table.item(selected_items[0])['values'][0]  # Get the name from the first column
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE medicines SET flag = -1 WHERE name = %s", (name,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Product deleted successfully.")
                for item in selected_items:
                    table.delete(item)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    btn_delete = tk.Button(delete_win, text="Delete Product", command=delete_product, bg="red", fg="white",
                           font=("Arial", 12))
    btn_delete.place(x=200, y=480, width=150, height=40)

    btn_main_menu = tk.Button(delete_win, text="Main Menu", command=lambda: [delete_win.destroy()],
                              bg="#007bff", fg="white", font=("Arial", 12))
    btn_main_menu.place(x=370, y=480, width=150, height=40)


# To search the Medicines from database
def open_search():
    # Create a new window for searching medicines
    search_win = tk.Toplevel()
    search_win.title("Search Medicines")
    search_win.geometry("900x700")
    search_win.resizable(False, False)  # Make the window not resizable

    # ---------- Background Image ----------
    bg_image = Image.open("resources/img2.png")
    bg_image = bg_image.resize((1500, 1000))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(search_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Frame for product search
    search_frame = tk.Frame(search_win, bg="white", bd=2, relief=tk.RIDGE)
    search_frame.place(x=30, y=30, width=500, height=100)

    tk.Label(search_frame, text="Enter Medicine Name:", bg="white", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)

    entry_name = tk.Entry(search_frame, width=30, font=("Arial", 12))
    entry_name.grid(row=1, column=0, padx=10, pady=5)

    def fetch_product_details():
        name = entry_name.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter the medicine name.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            # Use LIKE to find names starting with the entered characters
            cursor.execute(
                "SELECT name, type, quantity, cost, purpose, start_date, expiry_date, rack, manufacturer FROM medicines WHERE name LIKE %s AND flag not in (0, -1)",
                (name + '%',))  # Append '%' to match names starting with the input
            results = cursor.fetchall()
            conn.close()

            # Clear previous data in the table
            for row in table.get_children():
                table.delete(row)

            if results:
                for result in results:
                    table.insert("", "end", values=result)  # Insert all columns
            else:
                messagebox.showinfo("Not Found", "No medicines found starting with that name.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn_fetch = tk.Button(search_frame, text="Fetch Details", command=fetch_product_details, bg="#28a745", fg="white",
                          font=("Arial", 12))
    btn_fetch.grid(row=1, column=1, padx=10, pady=5)

    # Table Frame
    table_frame = tk.Frame(search_win)
    table_frame.place(x=30, y=150, width=800, height=400)

    columns = (
        "Name", "Type", "Quantity", "Cost", "Purpose", "Start Date", "Expiry Date", "Rack", "Manufacturer")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")

    # Configure column headings and widths
    for col in columns:
        table.heading(col, text=col)
        table.column(col, anchor="center", width=100)  # Center align and set width

    # Create a vertical scrollbar
    v_scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
    table.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a horizontal scrollbar
    h_scrollbar = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=table.xview)
    table.configure(xscrollcommand=h_scrollbar.set)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Pack the Treeview
    table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Main Menu Button
    btn_main_menu = tk.Button(search_win, text="Main Menu", command=lambda: [search_win.destroy()],
                              bg="red", fg="white", font=("Arial", 12))
    btn_main_menu.place(x=30, y=570, width=150, height=40)

def open_check_revenue():
    def show_revenue(start_date, end_date):
        try:
            # Format date for MySQL query
            s_date = datetime.strptime(start_date, "%m/%d/%y").strftime("%Y-%m-%d 00:00:00")
            e_date = datetime.strptime(end_date, "%m/%d/%y").strftime("%Y-%m-%d 23:59:59")

            conn = get_connection()
            cursor = conn.cursor()
            query = """
            SELECT SUM(total_price) FROM billing_tb 
            WHERE flag NOT IN (0,-1) and sys_creation_time BETWEEN %s AND %s
            """
            cursor.execute(query, (s_date, e_date))
            revenue = cursor.fetchone()[0] or 0
            conn.close()

            # Format revenue in Indian currency
            formatted_revenue = f"₹{revenue:,.2f}"
            revenue_var.set(f"Total Revenue: {formatted_revenue}")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def reset_dates():
        today = datetime.today()
        start_date_entry.set_date(today)
        end_date_entry.set_date(today)
        revenue_var.set("Total Revenue: ₹0.00")

    def close_window():
        add_win.destroy()

    # Main Window
    add_win = tk.Toplevel()
    add_win.title("Check Revenue")
    add_win.geometry("600x450")
    add_win.resizable(False, False)

    # Background image
    bg_image = Image.open("resources/img2.png")
    bg_image = bg_image.resize((600, 450))
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(add_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Main frame with border
    frame = tk.Frame(add_win, bg='lightblue', bd=3, relief="ridge")
    frame.place(x=70, y=70, width=460, height=300)

    # Start Date
    tk.Label(frame, text="Start Date:", font=("Helvetica", 12), bg='lightblue').grid(row=0, column=0, padx=10, pady=15, sticky="e")
    start_date_entry = DateEntry(frame, width=18, background='darkblue', foreground='white', borderwidth=2)
    start_date_entry.grid(row=0, column=1, padx=10, pady=15)

    # End Date
    tk.Label(frame, text="End Date:", font=("Helvetica", 12), bg='lightblue').grid(row=1, column=0, padx=10, pady=5, sticky="e")
    end_date_entry = DateEntry(frame, width=18, background='darkblue', foreground='white', borderwidth=2)
    end_date_entry.grid(row=1, column=1, padx=10, pady=5)

    # Revenue Label
    revenue_var = tk.StringVar(value="Total Revenue: ₹0.00")
    revenue_label = tk.Label(frame, textvariable=revenue_var, font=("Helvetica", 14, "bold"), bg='lightblue')
    revenue_label.grid(row=2, column=0, columnspan=2, pady=20)

    # Buttons in one row
    show_btn = tk.Button(frame, text="Show Revenue", width=14, bg="#4CAF50", fg="white",
                         command=lambda: show_revenue(start_date_entry.get(), end_date_entry.get()))
    reset_btn = tk.Button(frame, text="Reset Dates", width=14, bg="#2196F3", fg="white", command=reset_dates)
    close_btn = tk.Button(frame, text="Close", width=14, bg="#f44336", fg="white", command=close_window)

    show_btn.grid(row=3, column=0, pady=10)
    reset_btn.grid(row=3, column=1, pady=10)
    close_btn.grid(row=3, column=2, pady=10)


# To check the expired products from the database
def open_expiry_check():
    expiry_win = tk.Toplevel()
    expiry_win.title("Expiry Check")
    expiry_win.geometry("800x600")
    expiry_win.resizable(False, False)
    # ---------- Background Image ----------
    bg_image = Image.open("resources/img2.png")
    bg_image = bg_image.resize((1500, 1000))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(expiry_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # ---------- Date Selection Frame ----------
    date_frame = tk.Frame(expiry_win, bg="white", bd=2, relief=tk.RIDGE)
    date_frame.place(x=30, y=30, width=740, height=100)

    tk.Label(date_frame, text="Select Expiry Date:", bg="white", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)

    # Default to today's date
    today = datetime.today().date()
    expiry_date_entry = DateEntry(date_frame, width=18, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
    expiry_date_entry.set_date(today)
    expiry_date_entry.grid(row=1, column=0, padx=10, pady=5)

    def fetch_expired_products():
        selected_date = expiry_date_entry.get_date()
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, type, quantity, cost, purpose, start_date, expiry_date, rack, manufacturer FROM medicines WHERE expiry_date < %s AND flag NOT IN (0, -1)",
                (selected_date,))
            results = cursor.fetchall()
            conn.close()

            # Clear previous entries in the table
            for row in table.get_children():
                table.delete(row)

            if results:
                for result in results:
                    table.insert("", "end", values=result)  # Insert each result into the table
            else:
                messagebox.showinfo("Not Found", "No expired medicines found.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    btn_fetch = tk.Button(date_frame, text="Fetch Expired Products", command=fetch_expired_products, bg="#28a745", fg="white",
                          font=("Arial", 12))
    btn_fetch.grid(row=1, column=1, padx=10, pady=5)

    # ---------- Table Frame ----------
    table_frame = tk.Frame(expiry_win)
    table_frame.place(x=30, y=150, width=740, height=350)

    columns = ("Name", "Type", "Quantity", "Cost", "Purpose", "Start Date", "Expiry Date", "Rack", "Manufacturer")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=100)

    # Create a vertical scrollbar
    v_scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
    table.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a horizontal scrollbar
    h_scrollbar = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=table.xview)
    table.configure(xscrollcommand=h_scrollbar.set)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    # Pack the Treeview
    table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def delete_expired_products():
        selected_items = table.selection()
        if not selected_items:
            messagebox.showwarning("Selection Error", "Please select at least one expired product to delete.")
            return

        confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected expired products?")
        if confirm:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                for item in selected_items:
                    name = table.item(item)['values'][0]  # Get the name from the first column
                    cursor.execute("UPDATE medicines SET flag = -1 WHERE name = %s", (name,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Selected expired products deleted successfully.")
                # Refresh the table
                fetch_expired_products()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    btn_delete = tk.Button(expiry_win, text="Delete Selected Expired Product", command=delete_expired_products, bg="red", fg="white",
                           font=("Arial", 12))
    btn_delete.place(x=250, y=520, width=250, height=40)

    # Optional: Add a button to close the window
    btn_close = tk.Button(expiry_win, text="Main Menu", command=expiry_win.destroy, bg="#007bff", fg="white",
                          font=("Arial", 12))
    btn_close.place(x=550, y=520, width=200, height=40)

# ---------- Admin Dashboard ----------
def admin_dashboard(admin_data):
    root.withdraw()
    admin_win = tk.Toplevel()
    admin_win.title("Admin Dashboard")
    admin_win.geometry("600x400")
    admin_win.resizable(False, False)

    bg_image = Image.open("resources/img2.png")
    bg_image = bg_image.resize((600, 400))
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(admin_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    top_frame = tk.Frame(admin_win, bg="#ffffff")
    top_frame.pack(fill=tk.X)

    tk.Label(top_frame, text=f"👤 {admin_data[1]}", font=("Arial", 12, 'bold'), bg="#ffffff").pack(side=tk.LEFT, padx=10)
    tk.Label(top_frame, text=f"📞 {admin_data[3]}", font=("Arial", 12, 'bold'), bg="#ffffff").pack(side=tk.RIGHT, padx=10)

    tk.Label(admin_win, text="MEDI TRACKER CHEMIST AND DRUGSHOP", font=("Helvetica", 16, 'bold'), bg="#ffffff").pack(pady=(10, 0))

    header_frame = tk.Frame(admin_win, bg="#ffffff")
    header_frame.pack(pady=10)
    for text in ["Stock Maintenance", "Access Database", "Handle Cash Flows"]:
        tk.Label(header_frame, text=text, font=("Arial", 10, 'bold'), bg="#ffffff", padx=20).pack(side=tk.LEFT, padx=10)

    button_frame = tk.Frame(admin_win, bg="#ffffff")
    button_frame.pack(pady=10)

    btn_specs = [
        ("Add product to Stock", open_add_product_window),
        ("Update product Details", open_update_product),
        ("Billing", open_billing),
        ("Delete product from Stock", open_delete_product),
        ("Search", open_search),
        ("Check Today's Revenue", open_check_revenue),
        ("Expiry Check", open_expiry_check)
    ]

    positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 1)]
    for ((text, cmd), (r, c)) in zip(btn_specs, positions):
        tk.Button(button_frame, text=text, width=22, height=2, bg="#007BFF", fg="white",
                  font=('Arial', 9, 'bold'), command=cmd).grid(row=r, column=c, padx=5, pady=5)

    tk.Button(admin_win, text="Logout", command=lambda: [admin_win.destroy(), root.deiconify()], bg='red', fg='white',
              font=('Helvetica', 12, 'bold')).pack(side=tk.BOTTOM, pady=10)


# --- User Dashboard ---
def user_dashboard(user_data):
    root.withdraw()
    user_win = tk.Toplevel()
    user_win.title("User Dashboard")
    user_win.geometry("600x400")
    user_win.resizable(False, False)
    user_win.configure(bg='#e9ecef')

    bg_image = Image.open("resources/img2.png").resize((600, 400))
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(user_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    top_frame = tk.Frame(user_win, bg="#ffffff")
    top_frame.pack(fill=tk.X)

    tk.Label(top_frame, text=f"👤 {user_data[1]}", font=("Arial", 12, 'bold'), bg="#ffffff").pack(side=tk.LEFT, padx=10)
    tk.Label(top_frame, text=f"📞 {user_data[5]}", font=("Arial", 12, 'bold'), bg="#ffffff").pack(side=tk.RIGHT, padx=10)

    tk.Label(user_win, text="MEDI TRACKER CHEMIST AND DRUGSHOP", font=("Helvetica", 16, 'bold'), bg="#ffffff").pack(pady=(10, 0))

    button_frame = tk.Frame(user_win, bg="#ffffff")
    button_frame.pack(pady=10)

    btn_specs = [
        ("View Medicines", lambda: view_medicine_user_window(user_data[1], user_data[5])),
        ("View History", lambda: view_history_data_user_window(user_data[1], user_data[5])),
        ("View Personal Details", lambda: view_personal_data_user_window(user_data[1], user_data[5])),
    ]

    positions = [(0, 0), (0, 1), (0, 2)]
    for ((text, cmd), (r, c)) in zip(btn_specs, positions):
        tk.Button(button_frame, text=text, width=22, height=2, bg="#007BFF", fg="white",
                  font=('Arial', 9, 'bold'), command=cmd).grid(row=r, column=c, padx=5, pady=5)

    tk.Button(user_win, text="Logout", command=lambda: [user_win.destroy(), root.deiconify()],
              bg='red', fg='white', font=('Helvetica', 12, 'bold')).pack(side=tk.BOTTOM, pady=10)

# --- Personal Data Viewer ---
def view_personal_data_user_window(uname, phone):
    root.withdraw()
    personal_win = tk.Toplevel()
    personal_win.title("User Details")
    personal_win.geometry("600x400")
    personal_win.resizable(False, False)

    bg_image = Image.open("resources/img2.png").resize((600, 400))
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = tk.Label(personal_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    tk.Label(personal_win, text="Your Personal Details", font=("Helvetica", 16, 'bold'), bg="white").pack(pady=10)

    frame = tk.Frame(personal_win, bg="white", bd=2, relief=tk.RIDGE)
    frame.place(x=100, y=80, width=400, height=250)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fullname, username, phone, gender, age, gmail
            FROM users
            WHERE username = %s AND phone = %s AND flag NOT IN (0, -1)
            LIMIT 1
        """, (uname, phone))
        data = cursor.fetchone()
        conn.close()

        if data:
            labels = ["Name", "Username", "Phone", "Gender", "Age", "Email", "Address"]
            for i, value in enumerate(data):
                tk.Label(frame, text=f"{labels[i]}:", font=("Arial", 12, "bold"), anchor='w', bg="white").grid(row=i, column=0, sticky='w', padx=10, pady=5)
                tk.Label(frame, text=value, font=("Arial", 12), anchor='w', bg="white").grid(row=i, column=1, sticky='w', padx=10, pady=5)
        else:
            messagebox.showinfo("No Data", "No personal data found.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

    tk.Button(personal_win, text="Main Menu", command=personal_win.destroy,
              bg="red", fg="white", font=("Arial", 12)).place(x=30, y=340, width=150, height=40)


# Create new window
def view_medicine_user_window(uname,phone):
    root.withdraw()
    search_win = tk.Toplevel()
    search_win.title("Search Medicines")
    search_win.geometry("900x700")
    search_win.resizable(False, False)

    # ---------- Background Image ----------
    bg_image = Image.open("resources/img2.png")
    bg_image = bg_image.resize((1500, 1000))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(search_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    top_frame = tk.Frame(search_win, bg="#ffffff")
    top_frame.pack(fill=tk.X)

    tk.Label(top_frame, text=f"👤 {uname}", font=("Arial", 12, 'bold'), bg="#ffffff").pack(side=tk.LEFT, padx=10)
    tk.Label(top_frame, text=f"📞 {phone}", font=("Arial", 12, 'bold'), bg="#ffffff").pack(side=tk.RIGHT,
                                                                                                 padx=10)

    # ---------- Search Frame ----------
    search_frame = tk.Frame(search_win, bg="white", bd=2, relief=tk.RIDGE)
    search_frame.place(x=30, y=30, width=500, height=120)

    tk.Label(search_frame, text="Enter Medicine Name:", bg="white", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)

    entry_name = tk.Entry(search_frame, width=30, font=("Arial", 12))
    entry_name.grid(row=1, column=0, padx=10, pady=5)

    # Label to show count of results
    lbl_count = tk.Label(search_frame, text="Total Medicines: 0", bg="white", font=("Arial", 12, "bold"), fg="blue")
    lbl_count.grid(row=2, column=0, columnspan=2, pady=5)

    # ---------- Table Frame ----------
    table_frame = tk.Frame(search_win)
    table_frame.place(x=30, y=150, width=800, height=400)

    columns = ("Name", "Type", "Quantity", "Cost", "Purpose", "Start Date", "Expiry Date", "Manufacturer")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, anchor="center", width=100)

    v_scrollbar = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
    h_scrollbar = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=table.xview)
    table.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ---------- Load All Medicines Initially ----------
    def load_all_medicines():
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, type, quantity, cost, purpose, start_date, expiry_date, manufacturer
                FROM medicines
                WHERE flag NOT IN (0, -1)
                AND quantity NOT IN (0)
            """)
            results = cursor.fetchall()
            conn.close()

            table.delete(*table.get_children())
            for result in results:
                table.insert("", "end", values=result)

            lbl_count.config(text=f"Total Medicines: {len(results)}")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ---------- Fetch Filtered Medicines ----------
    def fetch_product_details():
        name = entry_name.get().strip()
        if not name:
            load_all_medicines()
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, type, quantity, cost, purpose, start_date, expiry_date, manufacturer
                FROM medicines
                WHERE name LIKE %s AND flag NOT IN (0, -1
                AND quantity NOT IN (0))
            """, (name + '%',))
            results = cursor.fetchall()
            conn.close()

            table.delete(*table.get_children())
            if results:
                for result in results:
                    table.insert("", "end", values=result)
                lbl_count.config(text=f"Total Medicines: {len(results)}")
            else:
                lbl_count.config(text="Total Medicines: 0")
                messagebox.showinfo("Not Found", "No medicines found starting with that name.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------- Buttons ----------
    btn_fetch = tk.Button(search_frame, text="Fetch Details", command=fetch_product_details,
                          bg="#28a745", fg="white", font=("Arial", 12))
    btn_fetch.grid(row=1, column=1, padx=10, pady=5)

    btn_main_menu = tk.Button(search_win, text="Main Menu", command=search_win.destroy,
                              bg="red", fg="white", font=("Arial", 12))
    btn_main_menu.place(x=30, y=570, width=150, height=40)

    # Load all medicines on window open
    load_all_medicines()

def view_history_data_user_window(uname, phone):

    root.withdraw()
    history_win = tk.Toplevel()
    history_win.title("View Purchase History")
    history_win.geometry("950x750")
    history_win.resizable(False, False)

    # ---------- Background Image ----------
    bg_image = Image.open("resources/img2.png")
    bg_image = bg_image.resize((1500, 1000))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(history_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    top_frame = tk.Frame(history_win, bg="#ffffff")
    top_frame.pack(fill=tk.X)

    tk.Label(top_frame, text=f"👤 {uname}", font=("Arial", 12, 'bold'), bg="#ffffff").pack(side=tk.LEFT, padx=10)
    tk.Label(top_frame, text=f"📞 {phone}", font=("Arial", 12, 'bold'), bg="#ffffff").pack(side=tk.RIGHT,
                                                                                                 padx=10)

    tk.Label(history_win, text="MEDI TRACKER CHEMIST AND DRUGSHOP", font=("Helvetica", 16, 'bold'), bg="#ffffff").pack(
        pady=(10, 0))

    # ---------- Filters Frame ----------
    filter_frame = tk.Frame(history_win, bg="white", bd=2, relief=tk.RIDGE)
    filter_frame.place(x=30, y=30, width=850, height=100)

    tk.Label(filter_frame, text="Start Date:", bg="white", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
    start_date_entry = DateEntry(filter_frame, width=12, font=("Arial", 12), date_pattern='yyyy-mm-dd')
    start_date_entry.grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="End Date:", bg="white", font=("Arial", 12)).grid(row=0, column=2, padx=10)
    end_date_entry = DateEntry(filter_frame, width=12, font=("Arial", 12), date_pattern='yyyy-mm-dd')
    end_date_entry.grid(row=0, column=3, padx=5)

    lbl_total_spent = tk.Label(filter_frame, text="Total Spent: ₹0.00", bg="white", fg="blue", font=("Arial", 12, "bold"))
    lbl_total_spent.grid(row=1, column=0, columnspan=4, pady=10)

    # ---------- Table Frame ----------
    table_frame = tk.Frame(history_win)
    table_frame.place(x=30, y=150, width=850, height=450)

    columns = ("Medicine", "Type", "Quantity", "Cost", "Purpose", "Manufacturer", "GST", "Total", "Date")
    table = ttk.Treeview(table_frame, columns=columns, show="headings")

    for col in columns:
        table.heading(col, text=col)
        table.column(col, anchor="center", width=100)

    v_scroll = tk.Scrollbar(table_frame, orient=tk.VERTICAL, command=table.yview)
    h_scroll = tk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=table.xview)
    table.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ---------- Load History Data ----------
    def load_history(start_date=None, end_date=None):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                SELECT medicine_name, type, quantity, cost, purpose, manufacturer, gst, total_price, sys_creation_time
                FROM billing_tb
                WHERE username = %s AND phone = %s AND flag NOT IN (0, -1)
                AND quantity NOT IN (0)
            """
            params = [uname, phone]

            if start_date and end_date:
                query += " AND DATE(update_time) BETWEEN %s AND %s"
                params.extend([start_date, end_date])

            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            table.delete(*table.get_children())
            total_spent = 0.0

            for row in results:
                table.insert("", "end", values=row)
                total_spent += float(row[7])

            lbl_total_spent.config(text=f"Total Spent: ₹{total_spent:.2f}")
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ---------- Button Actions ----------
    def fetch_with_dates():
        s_date = start_date_entry.get_date().strftime('%Y-%m-%d')
        e_date = end_date_entry.get_date().strftime('%Y-%m-%d')
        load_history(start_date=s_date, end_date=e_date)

    def reset_filters():
        today = datetime.today()
        start_date_entry.set_date(today)
        end_date_entry.set_date(today)
        load_history()

    # ---------- Buttons ----------
    btn_fetch = tk.Button(filter_frame, text="Filter History", command=fetch_with_dates,
                          bg="#007bff", fg="white", font=("Arial", 12))
    btn_fetch.grid(row=0, column=4, padx=10)

    btn_reset = tk.Button(filter_frame, text="Reset", command=reset_filters,
                          bg="#ffc107", fg="black", font=("Arial", 12))
    btn_reset.grid(row=0, column=5, padx=10)

    btn_main_menu = tk.Button(history_win, text="Main Menu", command=history_win.destroy,
                              bg="red", fg="white", font=("Arial", 12))
    btn_main_menu.place(x=30, y=630, width=150, height=40)

    # ---------- Load data initially ----------
    reset_filters()

# ----------------- Random Password Generator -----------------
def generate_random_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))

# ----------------- User Creation Logic -----------------
def create_users_from_billing():
    new_user_count = 0
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT username, phone FROM billing_tb WHERE flag NOT IN (0, -1) """)
        billing_users = cursor.fetchall()

        for username, phone in billing_users:
            cursor.execute("SELECT COUNT(*) FROM users WHERE flag NOT IN (0, -1) and username = %s AND phone = %s", (username, phone))
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    SELECT customer_name, age, phone, email, gender
                    FROM billing_tb WHERE username = %s AND phone = %s AND flag NOT IN (0, -1) LIMIT 1
                """, (username, phone))
                user_info = cursor.fetchone()
                if user_info:
                    fullname, age, phone, gmail, gender = user_info
                    password = generate_random_password()
                    cursor.execute("""
                        INSERT INTO users (username, password, fullname, age, phone, gmail, gender, flag)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                    """, (username, password, fullname, age, phone, gmail, gender))
                    new_user_count += 1

        conn.commit()
        conn.close()

        print(f"[INFO] {new_user_count} new user(s) created." if new_user_count else "[INFO] No new users found.")
    except Exception as e:
        print("[ERROR] User creation from billing failed:", str(e))

def repeat_user_creation_check():
    def loop():
        while True:
            create_users_from_billing()
            time.sleep(60)
    threading.Thread(target=loop, daemon=True).start()

def run_scheduler_automation():
    def loop():
        while True:
            # Check API availability
            api_up = False
            print("🌐 Checking scheduler API status...")

            for _ in range(30):  # Retry every 10 seconds for up to 300 seconds
                try:
                    r = requests.get("http://localhost:8080/scheduler/status")
                    if r.status_code == 200:
                        print(f"[{time.strftime('%X')}] ✅ API is UP: {r.status_code} - {r.text.strip()}")
                        api_up = True
                        break
                except requests.exceptions.RequestException as e:
                    print(f"[{time.strftime('%X')}] ❌ API DOWN. Retrying in 10s... ({e})")
                time.sleep(10)

            if not api_up:
                print("⚠️ API is still not reachable after multiple attempts. Waiting 30s before retry...")
                time.sleep(30)
                continue  # Restart the loop from the top

            # Proceed with scheduling flow
            try:
                r = requests.post("http://localhost:8080/scheduler/start?delayInSeconds=15")
                print(f"[{time.strftime('%X')}] 🚀 START: {r.status_code} - {r.text.strip()}")
            except Exception as e:
                print(f"[{time.strftime('%X')}] ❌ START error: {e}")

            time.sleep(15)

            try:
                r = requests.post(STOP_URL)
                print(f"[{time.strftime('%X')}] 🛑 STOP: {r.status_code} - {r.text.strip()}")
            except Exception as e:
                print(f"[{time.strftime('%X')}] ❌ STOP error: {e}")

            time.sleep(60)  # 1 minute sleep

            try:
                r = requests.post("http://localhost:8080/scheduler/update?delayInSeconds=16")
                print(f"[{time.strftime('%X')}] 🔄 UPDATE: {r.status_code} - {r.text.strip()}")
            except Exception as e:
                print(f"[{time.strftime('%X')}] ❌ UPDATE error: {e}")

            time.sleep(16)

    threading.Thread(target=loop, daemon=True).start()

def start_background_tasks():
    print("🚀 Starting background automation...")
    run_scheduler_automation()
    repeat_user_creation_check()

def stop_scheduler_on_exit():
    try:
        response = requests.post(STOP_URL)
        print(f"🛑 Scheduler stopped: {response.status_code} - {response.text.strip()}")
    except Exception as e:
        print(f"❌ Could not stop scheduler on exit: {e}")

atexit.register(stop_scheduler_on_exit)
signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))

# ----------------- Login Function -----------------
def login():
    global attempt_count
    uname = username_entry.get()
    pwd = password_entry.get()

    if not uname or not pwd:
        messagebox.showerror("Error", "Username and Password cannot be empty.")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE flag NOT IN (0, -1) and username=%s", (uname,))
        user = cursor.fetchone()

        if user:
            if user[2] == pwd:
                messagebox.showinfo("Login Success", f"Welcome {user[3]}!")
                user_dashboard(user)
                attempt_count = 0
            else:
                attempt_count += 1
                if attempt_count >= 3:
                    messagebox.showwarning("Redirect", "3 incorrect attempts. Redirecting to forgot password.")
                    forgot_password_user_page(uname)
                else:
                    messagebox.showerror("Error", f"Incorrect password. {3 - attempt_count} attempts left")
        else:
            cursor.execute("SELECT * FROM admin WHERE flag NOT IN (0, -1) and username=%s", (uname,))
            admin = cursor.fetchone()
            if admin:
                if admin[2] == pwd:
                    messagebox.showinfo("Login Success", "Welcome Admin!")
                    admin_dashboard(admin)
                    attempt_count = 0
                else:
                    attempt_count += 1
                    if attempt_count >= 3:
                        messagebox.showwarning("Redirect", "3 incorrect attempts. Redirecting to forgot password.")
                        forgot_password_admin_page()
                    else:
                        messagebox.showerror("Error", f"Incorrect password. {3 - attempt_count} attempts left")
            else:
                messagebox.showinfo("Info", "Username does not exist. Redirecting to registration.")
                register_page(uname, pwd)
    except Exception as e:
        messagebox.showerror("Error", str(e))

# ----------------- Login Window -----------------
def launch_login_window():
    global root, username_entry, password_entry
    root = tk.Tk()
    root.title("Meditracker Login")
    root.geometry("600x400")
    root.resizable(False, False)

    # Background
    bg_image = Image.open("resources/img1.png").resize((900, 900))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Frame
    frame = tk.Frame(root, bg='#f8f9fa', bd=5, relief='ridge', width=400, height=350)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    frame.pack_propagate(False)

    tk.Label(frame, text="Login to Meditracker", font=('Helvetica', 18, 'bold'), bg='#f8f9fa').pack(pady=15)
    tk.Label(frame, text="Username", bg='#f8f9fa').pack(pady=(10, 0))
    username_entry = tk.Entry(frame, font=('Helvetica', 12))
    username_entry.pack(ipadx=20, ipady=5)

    tk.Label(frame, text="Password", bg='#f8f9fa').pack(pady=(10, 0))
    password_entry = tk.Entry(frame, show='*', font=('Helvetica', 12))
    password_entry.pack(ipadx=20, ipady=5)

    show_password_var = tk.BooleanVar()

    def show_password():
        password_entry.config(show='' if show_password_var.get() else '*')

    tk.Checkbutton(frame, text="Show Password", variable=show_password_var,
                   command=show_password).pack(pady=5)

    # Buttons
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Login", command=login, bg='#28a745', fg='white',
              font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="Register",
              command=lambda: register_page(username_entry.get(), password_entry.get()),
              bg='#007bff', fg='white', font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT, padx=10)

    tk.Button(button_frame, text="Cancel", bg='red', fg='white', font=('Helvetica', 12, 'bold'),
              command=root.destroy).pack(side=tk.LEFT, padx=10)

    # Start background after 2s
    root.after(2000, start_background_tasks)
    root.mainloop()
launch_login_window()