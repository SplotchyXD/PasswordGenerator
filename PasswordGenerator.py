import string
import secrets
import tkinter as tk
import tkinter.messagebox as mb

# Window creation
window = tk.Tk()
window.title("Password Generator")
window.geometry("640x480")
window.configure(background="lightgrey")

# Character pool
characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation

#Title_lbl = tk.Label(window, text="Spltochy's Password Generator", font="Bender 30 bold", bg="lightgrey")
#Title_lbl.pack()

canvas = tk.Canvas(window, width=640, height=100, bg="lightgrey", highlightthickness=0)
canvas.pack()

text = "Splotchy's Password Generator"
font = ("Bender", 30, "bold")
x, y = 320, 50  # center position

# Drawwing the border(yeah im not gonna lie I literally just googled for this)
outline_color = "black"
for dx in (-1,0,1):
    for dy in (-1,0,1):
        if dx != 0 or dy != 0:
            canvas.create_text(x+dx, y+dy, text=text, font=font, fill=outline_color)

# Draw the main text on top
canvas.create_text(x, y, text=text, font=font, fill="white")

# Label asking for the passwords length
Length_lbl = tk.Label(window, text="Set the password length", font="Bender 20 bold", bg="lightgrey")
Length_lbl.pack()

# Textbox for the users input, used for the passwords length
Length_entry = tk.Entry(window, font="Bender 20", justify="center")
Length_entry.pack(pady=10)

# Textbox that the generated password gets printed to
Pw_entry = tk.Entry(window, font="Bender 15", justify="center", state="readonly", width=-1)
#Pw_entry.pack(pady=10)

# label that will notify when a password gets copied to clipboard
Copy_lbl = tk.Label(window, text="", font="Bender", fg="blue")

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
        mb.showerror("Error","Password must contain atleast 1 character")

    password = []
    for Pwl in range(PwLength):
        random_char = secrets.choice(characters)
        password.append(random_char)
    password = "".join(password)

    if not Pw_entry.winfo_ismapped():
        Pw_entry.pack()

    # Displaying the generated password
    Pw_entry.config(state="normal")
    Pw_entry.delete(0, tk.END)
    Pw_entry.insert(0,password)
    Pw_entry.config(state="readonly")

# Logic for the copy to clipboard function
def copy_password():
    """Copy the password to clipboard and update the label"""
    window.clipboard_clear()
    window.clipboard_append(Pw_entry.get())
    window.update()
    """Make the label visible for 3 seconds and then hide it again"""
    if not Copy_lbl.winfo_ismapped():
        Copy_lbl.pack(pady= 10)
    window.after(3000, Copy_lbl.pack_forget)
    Copy_lbl.config(text="Password has been copied to clipboard.")


# Button for generating the password
Pw_generate_btn = tk.Button(window, text="Generate Password", font="Bender 15", command=Generate_password)
Pw_generate_btn.pack()

# Button to copy the password straight to clipboard
Copy_btn = tk.Button(window, text="Copy To Clipboard", font="Bender 15", command=lambda: copy_password())
Copy_btn.pack(pady=5)

window.mainloop()