from getpass import getpass
import hashlib
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import base64
import json
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
from datetime import datetime


# ----------------------------------------
# PASSWORD HASHING
# ----------------------------------------

def hash_password(password, salt):
    password_bytes = password.encode()

    hashed_password = hashlib.pbkdf2_hmac(
        "sha256",
        password_bytes,
        salt,
        100000
    )

    return hashed_password


# ----------------------------------------
# CREATE ENCRYPTION KEY
# ----------------------------------------

def create_encryption_key(password, salt):
    password_bytes = password.encode()

    key = hashlib.pbkdf2_hmac(
        "sha256",
        password_bytes,
        salt,
        100000,
        dklen=32
    )

    return base64.urlsafe_b64encode(key)


# ----------------------------------------
# CREATE ENCRYPTED VAULT
# ----------------------------------------

def create_vault(password, salt):
    key = create_encryption_key(password, salt)

    fernet = Fernet(key)

    vault_data = b"{}"

    encrypted_data = fernet.encrypt(vault_data)

    with open(os.path.join(BASE_DIR, "vault.enc"), "wb") as file:
        file.write(encrypted_data)

    print("\nEncrypted vault created successfully!")


# ----------------------------------------
# LOAD AND DECRYPT VAULT
# ----------------------------------------

def load_vault(password, salt):
    key = create_encryption_key(password, salt)

    fernet = Fernet(key)

    try:
        with open(os.path.join(BASE_DIR, "vault.enc"), "rb") as file:
            encrypted_data = file.read()

        decrypted_data = fernet.decrypt(encrypted_data)

        vault_data = json.loads(decrypted_data.decode())
        for service, account in vault_data.items():
            if "last_changed" not in account:
              account["last_changed"] = datetime.now().strftime("%Y-%m-%d")
        print("\nVault decrypted successfully!")

        return vault_data

    except FileNotFoundError:
        print("\nVault file not found!")
        return {}

    except Exception:
        print("\nUnable to decrypt vault!")
        return {}


# ----------------------------------------
# SAVE ENCRYPTED VAULT
# ----------------------------------------

def save_vault(vault, password, salt):
    key = create_encryption_key(password, salt)

    fernet = Fernet(key)

    vault_json = json.dumps(vault)

    vault_bytes = vault_json.encode()

    encrypted_data = fernet.encrypt(vault_bytes)

    with open(os.path.join(BASE_DIR, "vault.enc"), "wb") as file:
        file.write(encrypted_data)

    print("\nVault saved successfully! 🔐")


# ----------------------------------------
# ADD ACCOUNT
# ----------------------------------------

def add_account(vault):
    print("\n--- Add Account ---")

    service = input("Enter service name: ")
    username = input("Enter username/email: ")

    password = getpass("Enter password: ")
    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        print("\nPasswords do not match! ❌")
        return

    vault[service] = {
       "username": username,
       "password": password,
       "last_changed": datetime.now().strftime("%Y-%m-%d")
     }

    print("\nAccount added successfully! ✅")


# ----------------------------------------
# CREATE MASTER PASSWORD
# ----------------------------------------

def create_master_password():
    print("\n--- Create Master Password ---")

    password = getpass("Enter master password: ")
    confirm_password = getpass("Confirm master password: ")

    if password != confirm_password:
        print("\nPasswords do not match!")
        return

    salt = os.urandom(16)

    hashed_password = hash_password(password, salt)

    with open(os.path.join(BASE_DIR, "master.dat"), "wb") as file:
        file.write(salt)
        file.write(hashed_password)

    print("\nMaster password created successfully!")

    # Create encrypted vault
    create_vault(password, salt)


# ----------------------------------------
# LOGIN
# ----------------------------------------

def login():
    print("\n--- Login ---")

    password = getpass("Enter master password: ")

    try:
        with open(os.path.join(BASE_DIR, "master.dat"), "rb") as file:
            salt = file.read(16)
            saved_hash = file.read()

    except FileNotFoundError:
        print("\nNo master password found!")
        print("Please create a master password first.")
        return False

    entered_hash = hash_password(password, salt)

    if entered_hash == saved_hash:

        vault = load_vault(password, salt)

        print("\nLogin successful!")

        return vault, password, salt

    else:
        print("\nAccess denied! Incorrect password.")
        return False
# ----------------------------------------
# GET PASSWORD
# ----------------------------------------

def get_password(vault):
    print("\n--- Get Password ---")

    service = input("Enter service name: ")

    if service in vault:

        account = vault[service]

        print("\nUsername:", account["username"])
        print("Password:", account["password"])

        # Get the date when password was last changed
        last_changed = datetime.strptime(
            account["last_changed"],
            "%Y-%m-%d"
        )

        # Get today's date
        today = datetime.now()

        # Calculate days passed
        days_passed = (today - last_changed).days

        # Calculate remaining days
        days_remaining = 120 - days_passed

        print("\nPassword changed:", days_passed, "days ago")

        if days_remaining > 0:
            print("Days remaining:", days_remaining)

        elif days_remaining == 0:
            print("\n⚠️ Your password must be changed today!")

        else:
            print("\n🚨 Password change overdue!")
            print("Days overdue:", abs(days_remaining))

    else:
        print("\nAccount not found!")
# ----------------------------------------
# PASSWORD REMINDER
# ----------------------------------------

def password_reminder(vault):

    print("\n--- Password Reminder ---")

    if not vault:
        print("\nNo accounts found!")
        return

    for service, account in vault.items():

        last_changed = datetime.strptime(
            account["last_changed"],
            "%Y-%m-%d"
        )

        today = datetime.now()

        days_passed = (today - last_changed).days

        days_remaining = 120 - days_passed

        print("\nService:", service)
        print("Changed:", days_passed, "days ago")

        if days_remaining > 0:

            print("Days remaining:", days_remaining)

        elif days_remaining == 0:

            print("⚠️ Password must be changed today!")

        else:

            print("🚨 Password change overdue!")
            print("Days overdue:", abs(days_remaining))
# ----------------------------------------
# VAULT MENU
# ----------------------------------------

def vault_menu(vault, password, salt):

    while True:

        print("\n========================================")
        print("              VAULTGUARD")
        print("========================================")
        print("🔓 Vault Unlocked")
        print()
        print("1. Add Account")
        print("2. Get Password")
        print("3. Password Reminder")
        print("4. Lock Vault")
        print("5. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            add_account(vault)
            save_vault(vault, password, salt)

        elif choice == "2":
            get_password(vault)

        elif choice == "3":
            password_reminder(vault)

        elif choice == "4":
            print("\n🔒 Vault locked!")
            break

        elif choice == "5":
            print("\nGoodbye!")
            break

        else:
            print("\nInvalid choice!")

# ----------------------------------------
# ADD ACCOUNT WINDOW
# ----------------------------------------

def add_account_window(vault, password, salt):

    window = tk.Toplevel()

    window.title("Add Account")
    window.geometry("400x450")
    window.resizable(False, False)

    # TITLE
    title = tk.Label(
        window,
        text="➕ Add Account",
        font=("Arial", 22, "bold")
    )

    title.pack(pady=30)

    # SERVICE
    service_label = tk.Label(
        window,
        text="Service Name"
    )

    service_label.pack(pady=(10, 5))

    service_entry = tk.Entry(
        window,
        width=30,
        font=("Arial", 12)
    )

    service_entry.pack()

    # USERNAME
    username_label = tk.Label(
        window,
        text="Username / Email"
    )

    username_label.pack(pady=(20, 5))

    username_entry = tk.Entry(
        window,
        width=30,
        font=("Arial", 12)
    )

    username_entry.pack()

    # PASSWORD
    password_label = tk.Label(
        window,
        text="Password"
    )

    password_label.pack(pady=(20, 5))

    password_entry = tk.Entry(
        window,
        show="*",
        width=30,
        font=("Arial", 12)
    )

    password_entry.pack()

    # CONFIRM PASSWORD
    confirm_label = tk.Label(
        window,
        text="Confirm Password"
    )

    confirm_label.pack(pady=(20, 5))

    confirm_entry = tk.Entry(
        window,
        show="*",
        width=30,
        font=("Arial", 12)
    )

    confirm_entry.pack()

    # SAVE FUNCTION
    def save_account():

        service = service_entry.get().strip()
        username = username_entry.get().strip()
        account_password = password_entry.get()
        confirm_password = confirm_entry.get()

        # EMPTY CHECK
        if service == "" or username == "" or account_password == "":
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all fields."
            )
            return

        # PASSWORD MATCH
        if account_password != confirm_password:
            messagebox.showerror(
                "Password Error",
                "Passwords do not match!"
            )
            return

        # DUPLICATE CHECK
        if service in vault:
            messagebox.showerror(
                "Account Exists",
                "This service already exists!"
            )
            return

        # SAVE ACCOUNT
        vault[service] = {
            "username": username,
            "password": account_password,
            "last_changed": datetime.now().strftime("%Y-%m-%d")
        }

        # SAVE ENCRYPTED VAULT
        save_vault(vault, password, salt)

        messagebox.showinfo(
            "Success",
            "Account added successfully! ✅"
        )

        window.destroy()

    # SAVE BUTTON
    save_button = tk.Button(
        window,
        text="SAVE ACCOUNT",
        width=20,
        font=("Arial", 11, "bold"),
        command=save_account
    )

    save_button.pack(pady=30)
# ----------------------------------------
# GET PASSWORD WINDOW
# ----------------------------------------

def get_password_window(vault):

    window = tk.Toplevel()

    window.title("Get Password")
    window.geometry("400x450")
    window.resizable(False, False)

    # TITLE
    title = tk.Label(
        window,
        text="🔑 Get Password",
        font=("Arial", 22, "bold")
    )

    title.pack(pady=30)

    # SERVICE LABEL
    service_label = tk.Label(
        window,
        text="Enter Service Name",
        font=("Arial", 11)
    )

    service_label.pack(pady=(20, 5))

    # SERVICE ENTRY
    service_entry = tk.Entry(
        window,
        width=30,
        font=("Arial", 12)
    )

    service_entry.pack()

    # RESULT LABEL
    result_label = tk.Label(
        window,
        text="",
        font=("Arial", 11),
        justify="left"
    )

    result_label.pack(pady=25)

    # BACK BUTTON
    # We create it now but keep it hidden
    back_button = tk.Button(
        window,
        text="BACK",
        width=20,
        font=("Arial", 11, "bold"),
        command=lambda: back_to_search()
    )

    # SEARCH FUNCTION
    def search_account():

        service = service_entry.get().strip()

        if service == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter a service name."
            )
            return

        if service not in vault:
            messagebox.showerror(
                "Not Found",
                "Account not found!"
            )
            return

        account = vault[service]

        last_changed = datetime.strptime(
            account["last_changed"],
            "%Y-%m-%d"
        )

        today = datetime.now()

        days_passed = (today - last_changed).days

        days_remaining = 120 - days_passed

        result = (
            "Service: " + service +
            "\nUsername: " + account["username"] +
            "\nPassword: " + account["password"] +
            "\n\nPassword changed: " +
            str(days_passed) + " days ago"
        )

        if days_remaining > 0:

            result += (
                "\nDays remaining: " +
                str(days_remaining)
            )

        elif days_remaining == 0:

            result += "\n⚠️ Password must be changed today!"

        else:

            result += (
                "\n🚨 Password change overdue!" +
                "\nDays overdue: " +
                str(abs(days_remaining))
            )

        result_label.config(text=result)

        # SHOW BACK BUTTON AFTER PASSWORD IS FOUND
        back_button.pack(pady=10)

    # BACK FUNCTION
    def back_to_search():

        # Clear service name
        service_entry.delete(0, tk.END)

        # Clear password/result
        result_label.config(text="")

        # Hide BACK button
        back_button.pack_forget()

        # Put cursor back in service box
        service_entry.focus()

    # SEARCH BUTTON
    search_button = tk.Button(
        window,
        text="GET PASSWORD",
        width=20,
        font=("Arial", 11, "bold"),
        command=search_account
    )

    search_button.pack(pady=10)
 # BACK TO VAULT BUTTON
    close_button = tk.Button(
    window,
    text="BACK TO VAULT",
    width=20,
    font=("Arial", 11, "bold"),
    command=window.destroy
)

    close_button.pack(pady=10)   
    
# ----------------------------------------
# PASSWORD REMINDER WINDOW
# ----------------------------------------

def password_reminder_window(vault):

    window = tk.Toplevel()

    window.title("Password Reminder")
    window.geometry("500x500")
    window.resizable(False, False)

    # TITLE
    title = tk.Label(
        window,
        text="🔔 Password Reminder",
        font=("Arial", 22, "bold")
    )

    title.pack(pady=30)

    # FRAME FOR RESULTS
    frame = tk.Frame(window)
    frame.pack(pady=10)

    if not vault:

        no_accounts = tk.Label(
            frame,
            text="No accounts found!",
            font=("Arial", 12)
        )

        no_accounts.pack()

        return

    for service, account in vault.items():

        last_changed = datetime.strptime(
            account["last_changed"],
            "%Y-%m-%d"
        )

        today = datetime.now()

        days_passed = (today - last_changed).days

        days_remaining = 120 - days_passed

        # SERVICE
        service_label = tk.Label(
            frame,
            text="Service: " + service,
            font=("Arial", 12, "bold")
        )

        service_label.pack(pady=(10, 2))

        # DAYS PASSED
        changed_label = tk.Label(
            frame,
            text="Changed: " + str(days_passed) + " days ago",
            font=("Arial", 11)
        )

        changed_label.pack()

        # REMINDER
        if days_remaining > 0:

            reminder_label = tk.Label(
                frame,
                text="Days remaining: " + str(days_remaining),
                font=("Arial", 11)
            )

        elif days_remaining == 0:

            reminder_label = tk.Label(
                frame,
                text="⚠️ Password must be changed today!",
                font=("Arial", 11)
            )

        else:

            reminder_label = tk.Label(
                frame,
                text="🚨 Password change overdue!\nDays overdue: "
                     + str(abs(days_remaining)),
                font=("Arial", 11)
            )

        reminder_label.pack()

    # CLOSE BUTTON
    close_button = tk.Button(
        window,
        text="CLOSE",
        width=15,
        command=window.destroy
    )

    close_button.pack(pady=25)

def update_account_window(vault, password, salt):

    window = tk.Toplevel()

    window.title("Update Account")
    window.geometry("400x500")
    window.resizable(False, False)

    # TITLE
    title = tk.Label(
        window,
        text="✏️ Update Account",
        font=("Arial", 22, "bold")
    )
    title.pack(pady=30)

    # SERVICE
    service_label = tk.Label(
        window,
        text="Service Name"
    )
    service_label.pack(pady=(10, 5))

    service_entry = tk.Entry(
        window,
        width=30,
        font=("Arial", 12)
    )
    service_entry.pack()

    # USERNAME
    username_label = tk.Label(
        window,
        text="New Username / Email"
    )
    username_label.pack(pady=(20, 5))

    username_entry = tk.Entry(
        window,
        width=30,
        font=("Arial", 12)
    )
    username_entry.pack()

    # PASSWORD
    password_label = tk.Label(
        window,
        text="New Password"
    )
    password_label.pack(pady=(20, 5))

    password_entry = tk.Entry(
        window,
        show="*",
        width=30,
        font=("Arial", 12)
    )
    password_entry.pack()

    # CONFIRM PASSWORD
    confirm_label = tk.Label(
        window,
        text="Confirm New Password"
    )
    confirm_label.pack(pady=(20, 5))

    confirm_entry = tk.Entry(
        window,
        show="*",
        width=30,
        font=("Arial", 12)
    )
    confirm_entry.pack()

    # UPDATE FUNCTION
    def update_account():

        service = service_entry.get().strip()
        username = username_entry.get().strip()
        new_password = password_entry.get()
        confirm_password = confirm_entry.get()

        # CHECK SERVICE
        if service == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter a service name."
            )
            return

        # CHECK ACCOUNT
        if service not in vault:
            messagebox.showerror(
                "Not Found",
                "Account not found!"
            )
            return

        # CHECK EMPTY FIELDS
        if username == "" or new_password == "":
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all fields."
            )
            return

        # CHECK PASSWORD
        if new_password != confirm_password:
            messagebox.showerror(
                "Password Error",
                "Passwords do not match!"
            )
            return

        # UPDATE ACCOUNT
        vault[service] = {
            "username": username,
            "password": new_password,
            "last_changed": datetime.now().strftime("%Y-%m-%d")
        }

        # SAVE ENCRYPTED VAULT
        save_vault(vault, password, salt)

        messagebox.showinfo(
            "Success",
            "Account updated successfully! ✅"
        )

        window.destroy()

    # UPDATE BUTTON
    update_button = tk.Button(
        window,
        text="UPDATE ACCOUNT",
        width=20,
        font=("Arial", 11, "bold"),
        command=update_account
    )
    update_button.pack(pady=30)

    # BACK BUTTON
    back_button = tk.Button(
        window,
        text="BACK",
        width=20,
        command=window.destroy
    )
    back_button.pack()
# ----------------------------------------
# VAULT WINDOW
# ----------------------------------------   
def vault_window(vault, password, salt):

    window = tk.Tk()

    window.title("VaultGuard - Vault")
    window.geometry("500x500")
    window.resizable(False, False)

    title = tk.Label(
        window,
        text="🔓 VAULT UNLOCKED",
        font=("Arial", 22, "bold")
    )

    title.pack(pady=30)

    # --------------------------------
    # GET PASSWORD
    # --------------------------------

    get_button = tk.Button(
    window,
    text="🔑 Get Password",
    width=25,
    command=lambda: get_password_window(vault)
)

    get_button.pack(pady=10)

    # --------------------------------
    # ADD ACCOUNT
    # --------------------------------

    add_button = tk.Button(
    window,
    text="➕ Add Account",
    width=25,
    command=lambda: add_account_window(vault, password, salt)
)

    add_button.pack(pady=10)

    # --------------------------------
    # PASSWORD REMINDER
    # --------------------------------

    reminder_button = tk.Button(
    window,
    text="🔔 Password Reminder",
    width=25,
    command=lambda: password_reminder_window(vault)
)
    reminder_button.pack(pady=10)

    # --------------------------------
    # UPDATE ACCOUNT
    # --------------------------------

    update_button = tk.Button(
    window,
    text="✏️ Update Account",
    width=25,
    command=lambda: update_account_window(vault, password, salt)
)

    update_button.pack(pady=10)

    # --------------------------------
    # LOCK
    # --------------------------------

    lock_button = tk.Button(
        window,
        text="🔒 Lock Vault",
        width=25,
        command=window.destroy
    )

    lock_button.pack(pady=30)

    window.mainloop()

def login_window():

    root = tk.Tk()

    root.title("VaultGuard")
    root.geometry("400x450")
    root.resizable(False, False)

    # TITLE
    title = tk.Label(
        root,
        text="🔐 VAULTGUARD",
        font=("Arial", 24, "bold")
    )

    title.pack(pady=(50, 10))

    # SUBTITLE
    subtitle = tk.Label(
        root,
        text="Secure Password Manager",
        font=("Arial", 12)
    )

    subtitle.pack()

    # PASSWORD LABEL
    password_label = tk.Label(
        root,
        text="Master Password",
        font=("Arial", 11)
    )

    password_label.pack(pady=(50, 5))

    # PASSWORD BOX
    password_entry = tk.Entry(
        root,
        show="*",
        width=30,
        font=("Arial", 12)
    )

    password_entry.pack()

    # LOGIN FUNCTION
    def login_button_clicked():

        password = password_entry.get()

        if password == "":
            messagebox.showwarning(
                "Warning",
                "Please enter your master password."
            )
            return

        try:

            with open(os.path.join(BASE_DIR, "master.dat"), "rb") as file:
                salt = file.read(16)
                saved_hash = file.read()

        except FileNotFoundError:

            messagebox.showerror(
                "Error",
                "No master password found!\nPlease create one first."
            )
            return

        entered_hash = hash_password(password, salt)

        if entered_hash == saved_hash:

            vault = load_vault(password, salt)

            messagebox.showinfo(
                "Success",
                "Login successful! 🔓"
            )

            root.destroy()

            vault_window(vault, password, salt)

        else:

            messagebox.showerror(
                "Access Denied",
                "Incorrect master password!"
            )

    # LOGIN BUTTON
    login_button = tk.Button(
        root,
        text="LOGIN",
        width=15,
        font=("Arial", 11, "bold"),
        command=login_button_clicked
    )

    login_button.pack(pady=30)

    root.mainloop()
# ----------------------------------------
# START PROGRAM
# ----------------------------------------
login_window()