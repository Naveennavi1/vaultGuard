# 🔐 VaultGuard – Secure Password Manager

VaultGuard is a Python-based password manager designed to securely store and manage account credentials. It provides a simple Tkinter graphical interface with encrypted local storage, master-password authentication, account management, and password reminders.

## ✨ Features

- 🔐 Master password authentication
- ➕ Add new accounts
- 🔑 Retrieve saved passwords
- ✏️ Update account credentials
- 🔔 Password change reminders
- 🔒 Encrypted vault storage
- 💾 Persistent local storage
- 🖥️ Tkinter graphical user interface
- 🐙 Git and GitHub version control

## 🛠️ Technologies Used

- **Python**
- **Tkinter** – GUI
- **Cryptography / Fernet** – Vault encryption
- **Hashlib** – Password hashing
- **JSON** – Data handling
- **Git & GitHub** – Version control

## 🔐 Security

VaultGuard uses **PBKDF2-HMAC-SHA256** to hash the master password and **Fernet symmetric encryption** to encrypt the password vault.

A randomly generated salt is used when creating the master password.

The application's sensitive local files are:

```text
master.dat
vault.enc
```

These files are excluded from GitHub using `.gitignore`.

## 🚀 Features in Detail

### 🔐 Master Password

The application requires a master password to unlock the vault. The password is securely hashed using PBKDF2-HMAC-SHA256 with a randomly generated salt.

### ➕ Add Account

Users can add an account by providing:

- Service name
- Username / Email
- Password
- Password confirmation

The account is then stored in the encrypted vault.

### 🔑 Get Password

Users can search for a saved service and retrieve its stored username and password.

The application also displays how many days have passed since the password was changed.

### ✏️ Update Account

Existing account credentials can be updated through the Update Account interface.

When a password is updated, the password change date is automatically updated.

### 🔔 Password Reminder

VaultGuard tracks password age and provides a **120-day password reminder period**.

It displays:

- Days since the password was changed
- Days remaining
- Password change notification when the period expires

## 🔄 Application Workflow

```text
              VAULTGUARD
                   │
                   ▼
          Enter Master Password
                   │
                   ▼
            🔓 Vault Unlocked
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   Add Account  Get Password  Password Reminder
        │          │          │
        └──────────┼──────────┘
                   ▼
            Update Account
                   │
                   ▼
          Encrypted Vault Saved
```

## 📂 Project Structure

```text
VaultGuard/
│
├── ex.py
├── main.py
├── .gitignore
└── README.md
```

### 🔒 Local Sensitive Files

The following files are generated locally and are **not uploaded to GitHub**:

```text
master.dat
vault.enc
```

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Naveennavi1/vaultGuard.git
```

### 2. Open the Project

```bash
cd vaultGuard
```

### 3. Install the Required Package

```bash
pip install cryptography
```

### 4. Run VaultGuard

```bash
python ex.py
```

## 💻 Requirements

- Python 3.x
- Tkinter
- Cryptography

## ⚠️ Security Notice

This project is intended for educational and portfolio purposes.

Do not use real production passwords or sensitive credentials while testing.

Never upload:

```text
master.dat
vault.enc
```

to a public GitHub repository.

## 👨‍💻 Author

### Naveen Raj

**Email:** naveenrajnavi4@gmail.com  
**LinkedIn:** linkedin.com/in/naveenraj  
**Location:** Kerala, India

## 📌 Project Purpose

VaultGuard was developed to demonstrate practical knowledge of Python, GUI development, password hashing, encryption, secure local storage, file handling, and Git/GitHub version control.

## 📄 License

This project is created for educational and portfolio purposes.
