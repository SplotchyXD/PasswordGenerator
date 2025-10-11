import string
import secrets
import tkinter as tk
import tkinter.messagebox as mb

# === Window Setup ===
window = tk.Tk()
window.title("Splotchy's Password Generator")
window.geometry("800x320")
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
        PwLength =1
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

    # Makes the password textbox, password hidden button and copy password button visible
    if not Pw_entry.winfo_ismapped():
        Pw_entry.place(x=15, y=150)
    if not Showpw_check.winfo_ismapped():
        Showpw_check.place(x=15, y=190)
    if not Copy_btn.winfo_ismapped():
        Copy_btn.place(x=15,y=230)

    # Displaying the generated password
    Pw_entry.config(state="normal")
    Pw_entry.delete(0, tk.END)
    Pw_entry.insert(0,password)
    Pw_entry.config(state="readonly")

# Logic for the copy to clipboard function
def copy_password():
    """Copy the generated password to the clipboard and briefly display a confirmation label."""
    window.clipboard_clear()
    window.clipboard_append(Pw_entry.get())
    window.update()
    # Make the label visible for 3 seconds and then hide it again
    if not Copy_lbl.winfo_ismapped():
        Copy_lbl.place(x=210, y=235)
    window.after(3000, Copy_lbl.place_forget)
    Copy_lbl.config(text="Password has been copied to clipboard.", font="Bender 15 bold")

# Logic for enabling/disabling the asterisks in the password textbox
def Toggle_Pw_Show():
    if Show_password_bool.get():
        Pw_entry.config(show="*")
    else:
        Pw_entry.config(show="")

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
    bg="lightgrey")

# Start event loop
window.mainloop()