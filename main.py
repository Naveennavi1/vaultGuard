from getpass import getpass
import hashlib
import os
import base64
import json
from cryptography.fernet import Fernet
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

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

    with open("vault.enc", "wb") as file:
        file.write(encrypted_data)

    print("\nEncrypted vault created successfully!")


# ----------------------------------------
# LOAD AND DECRYPT VAULT
# ----------------------------------------

def load_vault(password, salt):
    key = create_encryption_key(password, salt)

    fernet = Fernet(key)

    try:
        with open("vault.enc", "rb") as file:
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

    with open("vault.enc", "wb") as file:
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

    with open("master.dat", "wb") as file:
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
        with open("master.dat", "rb") as file:
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
def login_window():

    root = tk.Tk()

    root.title("VaultGuard")
    root.geometry("400x450")
    root.resizable(False, False)

    title = tk.Label(
        root,
        text="🔐 VAULTGUARD",
        font=("Arial", 24, "bold")
    )

    title.pack(pady=40)

    subtitle = tk.Label(
        root,
        text="Secure Password Manager",
        font=("Arial", 12)
    )

    subtitle.pack()

    password_label = tk.Label(
        root,
        text="Master Password",
        font=("Arial", 11)
    )

    password_label.pack(pady=(40, 5))

    password_entry = tk.Entry(
        root,
        show="*",
        width=30,
        font=("Arial", 12)
    )

    password_entry.pack()

    login_button = tk.Button(
        root,
        text="LOGIN",
        width=15,
        font=("Arial", 11, "bold")
    )

    login_button.pack(pady=30)

    root.mainloop()

# ----------------------------------------
# MAIN MENU
# ----------------------------------------

print("========================================")
print("              VAULTGUARD")
print("       Secure Password Manager")
print("========================================")

print()
print("1. Create Master Password")
print("2. Login")
print("3. Exit")

choice = input("\nEnter your choice: ")


if choice == "1":

    create_master_password()

elif choice == "2":

    result = login()

    if result:
        vault, password, salt = result
        vault_menu(vault, password, salt)

    else:
        print("\n🔒 Vault remains locked.")

elif choice == "3":

    print("\nGoodbye!")

else:

    print("\nInvalid choice!")