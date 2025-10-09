import string
import secrets
import tkinter as tk
import tkinter.messagebox as mb

# Window creation
window = tk.Tk()
window.title("Password Generator")
window.geometry("640x480")

# Character pool
characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation

Length_lbl = tk.Label(window, text="Set the password length")
Length_lbl.pack()

Length_entry = tk.Entry(window)
Length_entry.pack()
Pw_entry = tk.Entry(window, state="readonly", width=50)
Pw_entry.pack(pady=10)
Copy_lbl = tk.Label(window, text="", fg="blue")
Copy_lbl.pack()

def Generate_password():
    try:
        PwLength = int(Length_entry.get())
    except ValueError:
        mb.showerror("Error", "Enter a valid number please.")
        return
    
    password = []
    for Pwl in range(PwLength):
        random_char = secrets.choice(characters)
        password.append(random_char)
    password = "".join(password)

    #mb.showinfo("Password Generated", password)
    Pw_entry.config(state="normal")
    Pw_entry.delete(0, tk.END)
    Pw_entry.insert(0,password)
    Pw_entry.config(state="readonly")

def copy_password():
    window.clipboard_clear()
    window.clipboard_append(Pw_entry.get())
    window.update()
    Copy_lbl.config(text="Password has been copied to clipboard.")

Pw_generate_btn = tk.Button(window, text="Generate Password", command=Generate_password)
Pw_generate_btn.pack()

Copy_btn = tk.Button(window, text="Copy To Clipboard", command=lambda: copy_password())
Copy_btn.pack(pady=5)

window.mainloop()