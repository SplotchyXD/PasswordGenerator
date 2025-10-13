import string
import secrets
import tkinter as tk
import tkinter.messagebox as mb
from tkinter import PhotoImage
import webbrowser
import sqlite3 as sql
from datetime import datetime

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
Startup_db()


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

    Username_lbl = tk.Label(Save_window, text="Username: ", font="Bender 15 bold", bg="lightgrey")
    Username_lbl.place(x=30, y=30)

    # Username input field
    Username_entry = tk.Entry(Save_window, font="Bender 15", width=25)
    Username_entry.place(x=150, y=32)

    # Making the password variables global
    global Password_lbl
    global Password_entry
    Password_lbl = tk.Label(Save_window, text="Password: ", font="Bender 15 bold", bg="lightgrey")
    Password_lbl.place(x=30, y=80)
    
    # Password input field
    Password_entry = tk.Entry(Save_window, font="Bender 15", width=25, show="*")
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
        cursor.execute(
            "INSERT INTO Passwords (username, password, date_created) VALUES (?, ?, ?)",
            (Username, Password, datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
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

# Start event loop
window.mainloop()