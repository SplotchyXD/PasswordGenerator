import string
import secrets

# string.ascii_lowercase, all letters in lowercase
# string.ascii_uppercase, all letters in uppercase
# string.digits,          all digits
# string.punctuation,     all symbols

characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
char = secrets.choice(characters)
password = []

PwLength = int(input("Enter password length: "))
print("Password length is set to: ", PwLength)

for Pwl in range(PwLength):
    random_char = secrets.choice(characters)
    password.append(random_char)
password = "".join(password)
print(password)