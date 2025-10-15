import string
import secrets
import tkinter as tk
import tkinter.messagebox as mb
from tkinter import PhotoImage
import webbrowser
import sqlite3 as sql
from datetime import datetime
import hashlib
import os
from base64 import b64encode, b64decode
import time
from cryptography.fernet import Fernet

Encryption_key = None

def Create_master_password_window():
    """Window for creating the master password on the first startup"""
    window.withdraw() # Hiding the main window from the user

    Setup_window = tk.Toplevel()
    Setup_window.title("Create Master Password")
    Setup_window.geometry("640x320")
    Setup_window.config(bg="lightgrey")

    Setup_window.protocol("WM_DELETE_WINDOW", lambda: None) # Remove the window's x button function

    # === Interface Widgets ===
    Title_lbl = tk.Label(
        Setup_window,
        text="Create Master Password",
        font="Bender 30 bold",
        bg="lightgrey",
        justify="center"
    )
    Title_lbl.place(x=20, y= 20)

    password_lbl = tk.Label(
        Setup_window,
        text="Password",
        font="Bender 20 bold",
        bg="lightgrey"
    )
    password_lbl.place(x=20, y=70)
    
    password_entry = tk.Entry(
        Setup_window,
        font="Bender 20 bold",
        show="*",
        width=25
    )
    password_entry.place(x=20, y=110)

    Confirm_lbl = tk.Label(
        Setup_window,
        text="Confirm Password:",
        font="Bender 20 bold",
        bg="lightgrey"
    )
    Confirm_lbl.place(x=20, y=150)
    Confirm_entry = tk.Entry(
        Setup_window,
        font="Bender 20 bold",
        show="*",
        width=25
    )
    Confirm_entry.place(x=20, y=190)

    Submit_btn = tk.Button(
        Setup_window,
        text="Save Password",
        font="Bender 15 bold",
        command=lambda: Submit_master_password(password_entry, Confirm_entry, Setup_window)
    )
    Submit_btn.place(x=460, y=190)

def Master_password_exists():
    """Check if user has setup their master password"""
    con = sql.connect("Passwords.db")
    cursor = con.cursor()
    cursor.execute("SELECT COUNT(*) FROM MasterPassword")
    count = cursor.fetchone()[0]
    con.close()
    return count > 0

def Save_master_password(password):
    """Hash the password and save it to the database, Using PBKDF2 with 480000 iterations makes brute force attacks not practical"""
    # Generate salt 
    # Used to ensure the identical passwords return different encryptions
    Salt = os.urandom(32)

    # Hashing password using PBKDF2_HMAC_SHA256 with the massive(480,000) iteration count
    Password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        Salt,
        480000
    )
    Salt_text = b64encode(Salt).decode()
    Hash_text = b64encode(Password_hash).decode()

    con = sql.connect("Passwords.db")
    cursor = con.cursor()
    cursor.execute(
        "INSERT INTO MasterPassword (id, salt, password_hash) VALUES (1, ?, ?)",
        (Salt_text, Hash_text)
    )
    con.commit()
    con.close()

def Master_password_verification(password):
    """Check if user inputed password matchess the stored hash"""
    con = sql.connect("Passwords.db")
    cursor = con.cursor()
    cursor.execute("SELECT salt, password_hash FROM MasterPassword WHERE id = 1")
    result = cursor.fetchone()
    con.close()

    if not result:
        return False
    
    Stored_salt = b64decode(result[0])
    Stored_hash =b64decode(result[1])

    Input_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        Stored_salt,
        480000
    )

    return Input_hash == Stored_hash

def Encryption_key_derive(password):
    """
    Derive an encryption key from the master password.
    uses the same salt as password verification to ensure the user always
    generates the same key for the same password
    """
    con = sql.connect("Passwords.db")
    cursor = con.cursor()
    cursor.execute("SELECT salt FROM MasterPassword WHERE id = 1")
    result = cursor.fetchone()
    con.close()

    Stored_salt = b64decode(result[0])

    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        Stored_salt,
        480000
    )
    return b64encode(key)

def Encrypt_password(password):
    """Encrypt the users password using the encryption key"""
    if Encryption_key is None:
        raise Exception("Not logged in - no encryption key available to use")
    
    fernet = Fernet(Encryption_key)
    encrypted = fernet.encrypt(password.encode())
    return encrypted.decode()

def Decrypt_password(encrypted_password):
    """Decrypt the users password using the encryption key"""
    if Encryption_key is None:
        raise Exception("Not logged in - no encryption key available to use")
    
    fernet = Fernet(Encryption_key)
    decrypted = fernet.decrypt(encrypted_password.encode())
    return decrypted.decode()

def Submit_login(password_entry, login_window):
    """Handels users login input"""
    password = password_entry.get()
    if not password:
        mb.showerror("Error","Please enter your password. ")
        return
    
    if Master_password_verification(password):

        global Encryption_key
        Encryption_key = Encryption_key_derive(password)

        login_window.destroy() # Closes the log in window after getting the correct master password
        window.deiconify() # Will put the main window on top
    else:
        mb.showerror("Error", "Password was incorrect.")
        password_entry.delete(0, tk.END)

def Submit_master_password(password_entry, Confirm_entry, setup_window):
    """Validate and save the master password"""
    password = password_entry.get()
    confirm = Confirm_entry.get()

    if not password or not confirm:
        mb.showerror("Error", "Both fields must be filled.")
        return
    
    if password !=confirm:
        mb.showerror("Error", "Passwords do not match.")
        return
    
    Save_master_password(password)

    global Encryption_key
    Encryption_key = Encryption_key_derive(password)

    setup_window.destroy() # Closes the master password window after saving the master password
    window.deiconify() # Will put the main window on top

    mb.showinfo("Success", "Master password has been created succesfully. ")


# === Database Startup ===
def Startup_db():
    """Create or connect to the SQLite database and check if the table exists."""
    con = sql.connect("Passwords.db")
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Passwords(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            date_created TEXT NOT NULL)
    """)
    con.commit()
    con.close()

def Create_Master_password_table():
    """Create a table that stores the users master password hash and salt"""
    con = sql.connect("Passwords.db")
    cursor = con.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MasterPassword(
            id INTEGER PRIMARY KEY,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL)
    """)
    con.commit()
    con.close()

Startup_db()
Create_Master_password_table()

def Login_window_popup():
    window.withdraw() # Hiding the main window from the user

    Login_window = tk.Toplevel()
    Login_window.title("Create Master Password")
    Login_window.geometry("640x320")
    Login_window.config(bg="lightgrey")
    Login_window.protocol("WM_DELETE_WINDOW", lambda: None)

            
    Title_lbl = tk.Label(
        Login_window,
        text="Welcome Back",
        font="Bender 30 bold",
        bg="lightgrey",
        justify="center"
    )
    Title_lbl.place(x=20, y= 20)

    Title_lbl2 = tk.Label(
        Login_window,
        text="Sign In",
        font="Bender 30 bold",
        bg="lightgrey",
        justify="center"
    )
    Title_lbl2.place(x=20, y= 70)

    password_lbl = tk.Label(
        Login_window,
        text="Password",
        font="Bender 20 bold",
        bg="lightgrey"
    )
    password_lbl.place(x=20, y=130)
    password_entry = tk.Entry(
        Login_window,
        font="Bender 20 bold",
        show="*",
        width=25
    )
    password_entry.place(x=20, y=170)

    Login_btn = tk.Button(
        Login_window,
        text="Login",
        font="Bender 15 bold",
        command=lambda: Submit_login(password_entry, Login_window)
    )
    Login_btn.place(x=20, y=210)

def Create_saved_passwords_window():
    """Open the saved passwords window and display the decrypted versions of the saved passwords"""
    Saved_passwords_window = tk.Toplevel()
    Saved_passwords_window.title("Saved Passwords")
    Saved_passwords_window.geometry("800x320")
    Saved_passwords_window.resizable(width=False, height=False)
    Saved_passwords_window.configure(background="lightgrey")
    Saved_passwords_window.attributes("-topmost", True)

    listbox = tk.Listbox(
    Saved_passwords_window,
    width= 200,
    justify="left",
    font="Bender 10 bold"
    )
    listbox.pack()

    def Get_passwords():
        con = sql.connect("Passwords.db")
        cursor = con.cursor()
        for row in cursor.execute("SELECT username, password, date_created FROM Passwords"):
            try:
                decrypted_password = Decrypt_password(row[1])
            except:
                decrypted_password = ("Decryption Failed.")

            data_text = f"Username: {row[0]} | Password: {decrypted_password} | Created: {row[2]}"
            listbox.insert(tk.END, data_text)
            listbox.update_idletasks()
            time.sleep(0.1) # Visual effect: makes it look like the passwords are getting loaded in

    Get_passwords()

    def Copy_username():
        """Copy the username from the row"""
        select = listbox.curselection()
        if not select:
            mb.showwarning("Warning", "Please select a username entry first.")
            return
        
        select_text = listbox.get(select[0])
        username = select_text.split(" | ")[0].replace("Username: ", "")

        Saved_passwords_window.clipboard_clear()
        Saved_passwords_window.clipboard_append(username)
    
    def Copy_password():
        """Copy the password from the row"""
        select = listbox.curselection()
        if not select:
            mb.showwarning("Warning", "Please select a password entry first.")
            return
        
        select_text = listbox.get(select[0])
        password = select_text.split(" | ")[1].replace("Password: ", "")

        Saved_passwords_window.clipboard_clear()
        Saved_passwords_window.clipboard_append(password)


    Copy_username_btn = tk.Button(
        Saved_passwords_window,
        text="Copy Username",
        font="Bender 15 bold",
        command=Copy_username
    )
    Copy_username_btn.place(x=10, y=170)

    Copy_password_btn = tk.Button(
        Saved_passwords_window,
        text="Copy Password",
        font="Bender 15 bold",
        command= Copy_password
    )
    Copy_password_btn.place(x=180, y=170)
# === Window Setup ===
window = tk.Tk()
window.title("Splotchy's Password Generator")
window.geometry("800x320")
window.resizable(width=False, height=False)
window.configure(background="lightgrey")

# === Title Canvas ===
# Using canvas for Drawing an outline on the title
canvas = tk.Canvas(
    window,
    width=800,
    height=100,
    bg="lightgrey",
    highlightthickness=0)
canvas.pack()

text = "Splotchy's Password Generator"
font = ("Bender", 30, "bold")
x, y = 320, 50

# Drawing the text outline (credit to Tkinter documentation my goat)
outline_color = "black"
for dx in (-1,0,1):
    for dy in (-1,0,1):
        if dx != 0 or dy != 0:
            canvas.create_text(x+dx, y+dy, text=text, font=font, fill=outline_color)

# Draw the main text on top
canvas.create_text(x, y, text=text, font=font, fill="white")

# === Password Length Input ===
# Label and entry box for setting the desired password length.
Length_lbl = tk.Label(
    window,
    text="Set The Password Length:",
    font="Bender 20 bold",
    bg="lightgrey")
Length_lbl.place(x=25, y=100)

# Variable that stores the user's input
Length_Var = tk.StringVar()

# Function that prevents the user from typing below 1 or above 50.
# (The limit is 50 for now, deal with it)
def Clamp_Length(*args):
    Value = Length_Var.get()
    if Value == "":
        return
    if not Value.isdigit():
        Length_Var.set("1")
        return
    IntValue = int(Value)
    if IntValue < 1:
        Length_Var.set("1")
    elif IntValue > 50:
        Length_Var.set("50")

# Attach the clamp function to trigger whenever the user types in the box
# This function is called automatically every time the text changes using trace_add()
Length_Var.trace_add("write", Clamp_Length)

# Textbox for the users input, used for the passwords length
Length_entry = tk.Entry(
    window,
    font="Bender 20",
    justify="center",
    width=3,
    textvariable=Length_Var
)
Length_entry.place(x=360, y=102)

# Textbox where the generated password is displayed
# State set to read-only to stop users from editing the passwords
Pw_entry = tk.Entry(
    window,
    font="Bender 20",
    state="readonly",
    width=-1,
    show="*")

# Label that notifies the user when a password is copied to the clipboard
Copy_lbl = tk.Label(
    window,
    text="",
    font="Bender",
    fg="blue")

# ===== Password Configuration Options =====
Include_symbols_bool = tk.BooleanVar(value=True)
Include_digits_bool = tk.BooleanVar(value=True)
Include_letters_bool = tk.BooleanVar(value=True)

# Controls whether password masking (asterisks) is enabled
Show_password_bool = tk.BooleanVar(value=True)

# Function: Generates a password with user inputed length control
def Generate_password():
    """Generate a password with the user defined length and display it"""
    try:
        PwLength = int(Length_entry.get())
    except ValueError:
        mb.showerror("Error", "Enter a valid number please.")
        return
    if PwLength < 1:
        PwLength = 1
    elif PwLength > 50:
        PwLength = 50

    # Clear user's input
    Length_entry.delete(0, tk.END)
    Length_entry.insert(0, str(PwLength))

    # Update the character pool based on selected checkboxes
    Password_generation_options()

    # Show an error if no character types are selected
    if not characters:
        mb.showerror("Error", "No checkboxes were chosen.")
        return
    
    # Building the password by selecting random characters from the pool
    password = []
    for Pwl in range(PwLength):
        random_char = secrets.choice(characters)
        password.append(random_char)
    password = "".join(password)

    # Makes the additional widgets vissible
    if not Pw_entry.winfo_ismapped():
        Pw_entry.place(x=15, y=150)
    if not Showpw_check.winfo_ismapped():
        Showpw_check.place(x=15, y=190)
    if not Copy_btn.winfo_ismapped():
        Copy_btn.place(x=190,y=230)
    if not Save_password_btn.winfo_ismapped():
        Save_password_btn.place(x=15,y=230)

    # Displaying the generated password
    Pw_entry.config(state="normal")
    Pw_entry.delete(0, tk.END)
    Pw_entry.insert(0,password)
    Pw_entry.config(state="readonly")

def Save_password_window_popup():
    """Open a new window to save the current generated password."""

    # Creating the the popup window as a global variable
    global Save_window
    Save_window = tk.Toplevel(window)
    Save_window.title("Save Generated Password")
    Save_window.geometry("480x240")
    Save_window.configure(bg="lightgrey")

    # ===== Interface Widgets =====
    Username_lbl = tk.Label(
        Save_window,
        text="Username: ",
        font="Bender 15 bold",
        bg="lightgrey"
    )
    Username_lbl.place(x=30, y=30)

    # Username input field
    Username_entry = tk.Entry(
        Save_window,
        font="Bender 15 bold",
        width=25
    )
    Username_entry.place(x=150, y=32)

    # Making the password variables global
    global Password_lbl
    global Password_entry
    Password_lbl = tk.Label(
        Save_window,
        text="Password: ",
        font="Bender 15 bold",
        bg="lightgrey"
    )
    Password_lbl.place(x=30, y=80)
    
    # Password input field
    Password_entry = tk.Entry(
        Save_window,
        font="Bender 15",
        width=25,
        show="*"
    )
    Password_entry.place(x=150, y=82)
    Password_entry.insert(0, Pw_entry.get())

    # Logic for saving a given username and the generated password
    def Save_password_data():
        Username = Username_entry.get()
        Password = Password_entry.get()
        
        if not Username or not Password:
            mb.showerror("Error", "Both fields must be filled.")
            return
        
        # Opening a connection to the db and sending the data to it
        con = sql.connect("Passwords.db")
        cursor = con.cursor()
        encrypted_password = Encrypt_password(Password)
        cursor.execute(
            "INSERT INTO Passwords (username, password, date_created) VALUES (?, ?, ?)",
            (Username, encrypted_password, datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        )
        con.commit()
        con.close()

        # Showing the user that the password has been saved to the db
        mb.showinfo("Saved", f"Password for '{Username}' has been saved succesfully.")
        Save_window.destroy()

    Save_btn = tk.Button(
        Save_window,
        text="Save Password",
        font="Bender 15 bold",
        command=Save_password_data
    )
    Save_btn.place(x=150, y=180)

    Hide_btn = tk.Checkbutton(
        Save_window,
        text="Hide Password",
        font="Bender 15 bold",
        variable=Show_password_bool,
        command=Toggle_Pw_Show
    )
    Hide_btn.place(x=150, y=120)

# Logic for the copy to clipboard function
def copy_password():
    """Copy the generated password to the clipboard and briefly display a confirmation label."""
    window.clipboard_clear()
    window.clipboard_append(Pw_entry.get())
    window.update()

    # Make the label visible for 3 seconds and then hide it again
    if not Copy_lbl.winfo_ismapped():
        Copy_lbl.place(x=190, y=193)
    window.after(3000, Copy_lbl.place_forget)
    Copy_lbl.config(text="Password has been copied to clipboard.", font="Bender 15 bold")

# Logic for enabling/disabling the asterisks in the password textbox
def Toggle_Pw_Show():
    Show_char = "*" if Show_password_bool.get() else ""
    Pw_entry.config(show=Show_char)
    try:
        if Save_window.winfo_exists() and Save_window.winfo_viewable():
            Password_entry.config(show=Show_char)
    except NameError:
        pass
  
# Logic for the option checkboxes
def Password_generation_options():
    global characters
    characters = ""
    if Include_letters_bool.get():
        characters += string.ascii_letters
    if Include_digits_bool.get():
        characters += string.digits
    if Include_symbols_bool.get():
        characters += string.punctuation

# Opens the project Github repository
def Open_Project_Repo():
    url = "https://github.com/SplotchyXD/PasswordGenerator"
    webbrowser.open(url)

# ===== Interface Buttons =====
# Button that generates the password by using the Generate_password command
Pw_generate_btn = tk.Button(
    window,
    text="Generate Password",
    font="Bender 15 bold",
    command=Generate_password)
Pw_generate_btn.place(x=420,y=100)

# Button that copies the generated password to clipboard
Copy_btn = tk.Button(
    window,
    text="Copy To Clipboard",
    font="Bender 15 bold",
    command=copy_password)

# === Password Option Checkboxes ===
# Each checkbox allows the enabling/disabling of letters, digits and symbols
Add_Letters_check = tk.Checkbutton(
    window,
    text="Include Letters",
    font="Bender 15 bold",
    variable=Include_letters_bool,
    command=Password_generation_options,
    bg="lightgrey")
Add_Letters_check.place(x=355, y=280)

Add_Digits_check = tk.Checkbutton(
    window,
    text="Include Digits",
    font="Bender 15 bold",
    variable=Include_digits_bool,
    command=Password_generation_options,
    bg="lightgrey")
Add_Digits_check.place(x=195, y=280)

Add_Symbols_check = tk.Checkbutton(
    window,
    text="Include Symbols",
    font="Bender 15 bold",
    variable=Include_symbols_bool,
    command=Password_generation_options,
    bg="lightgrey")
Add_Symbols_check.place(x=15, y=280)

# Checkbox to toggle password visibility (asterisks on/off)
Showpw_check = tk.Checkbutton(
    window,text="Hide Password",
    font="Bender 15 bold",
    variable=Show_password_bool,
    command=Toggle_Pw_Show,
    bg="lightgrey"
)

Github_Logo = PhotoImage(file="Github logo.png")

Github_btn = tk.Button(
    window,
    image=Github_Logo,
    bg="lightgray",
    activebackground="lightgray",
    command=Open_Project_Repo
)
Github_btn.place(x=725, y=245)

Save_password_btn = tk.Button(
    window,
    text="Save Password",
    font="Bender 15 bold",
    command=Save_password_window_popup
)

Passwords_btn = tk.Button(
    window,
    text="Saved Passwords",
    font="Bender 15 bold",
    command=Create_saved_passwords_window
)
Passwords_btn.place(x=540, y=275)

# Check if master password exists
# if yes: display login window
# if not: display the master password window(first time setup)
if Master_password_exists():
    Login_window_popup()
else:
    Create_master_password_window()

# Start event loop
window.mainloop()