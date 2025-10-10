import string
import secrets
import tkinter as tk
import tkinter.messagebox as mb

# Window creation
window = tk.Tk()
window.title("Splotchy's Password Generator")
window.geometry("640x640")
window.configure(background="lightgrey")

# Character pool
# characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation

#Title_lbl = tk.Label(window, text="Spltochy's Password Generator", font="Bender 30 bold", bg="lightgrey")
#Title_lbl.pack()

canvas = tk.Canvas(
    window,
    width=640,
    height=100,
    bg="lightgrey",
    highlightthickness=0)
canvas.pack()

text = "Splotchy's Password Generator"
font = ("Bender", 30, "bold")
x, y = 320, 50  # center position

# Drawing the text outline (credit to Tkinter documentation my goat)
outline_color = "black"
for dx in (-1,0,1):
    for dy in (-1,0,1):
        if dx != 0 or dy != 0:
            canvas.create_text(x+dx, y+dy, text=text, font=font, fill=outline_color)

# Draw the main text on top
canvas.create_text(x, y, text=text, font=font, fill="white")

# Label and input box for setting the password's length
Length_lbl = tk.Label(
    window,
    text="Set the password length",
    font="Bender 20 bold",
    bg="lightgrey")
Length_lbl.pack()

Length_entry = tk.Entry(
    window,
    font="Bender 20",
    justify="center")
Length_entry.pack(pady=10)

# Textbox where the generated password is displayed
Pw_entry = tk.Entry(
    window,
    font="Bender 20",
    justify="center",
    state="readonly",
    width=-1, show="*")

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
    if PwLength > 100:
        mb.showerror("Error", "Password length cannot exceed 100 characters.")
        return
    elif PwLength < 1:
        mb.showerror("Error","Password must contain at least 1 character")
        return

    Password_generation_options()

    if not characters:
        mb.showerror("Error", "No checkboxes were chosen.")
        return

    password = []
    for Pwl in range(PwLength):
        random_char = secrets.choice(characters)
        password.append(random_char)
    password = "".join(password)

    if not Pw_entry.winfo_ismapped():
        Pw_entry.pack()
    if not Showpw_check.winfo_ismapped():
        Showpw_check.pack(pady= 5)

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
        Copy_lbl.pack(pady= 10)
    window.after(3000, Copy_lbl.pack_forget)
    Copy_lbl.config(text="Password has been copied to clipboard.")

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
Pw_generate_btn = tk.Button(
    window,
    text="Generate Password",
    font="Bender 15",
    command=Generate_password)
Pw_generate_btn.pack()

Copy_btn = tk.Button(
    window,
    text="Copy To Clipboard",
    font="Bender 15",
    command=copy_password)
Copy_btn.pack(pady=5)

# Checkboxes for including or excluding letters, digits, and symbols
Add_Letters_check = tk.Checkbutton(
    window,
    text="Include Letters",
    font="Bender 15",
    variable=Include_letters_bool,
    command=Password_generation_options,
    bg="lightgrey")
Add_Letters_check.pack()

Add_Digits_check = tk.Checkbutton(
    window,
    text="Include Digits",
    font="Bender 15",
    variable=Include_digits_bool,
    command=Password_generation_options,
    bg="lightgrey")
Add_Digits_check.pack()

Add_Symbols_check = tk.Checkbutton(
    window,
    text="Include Symbols",
    font="Bender 15",
    variable=Include_symbols_bool,
    command=Password_generation_options,
    bg="lightgrey")
Add_Symbols_check.pack()

# Checkbox to toggle password visibility (asterisks on/off)
Showpw_check = tk.Checkbutton(window, text="Hide Password", font="Bender 15", variable=Show_password_bool, command=Toggle_Pw_Show, bg="lightgrey")

window.mainloop()