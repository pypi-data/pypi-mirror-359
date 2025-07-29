import sys

def ask_user():
    number = input("enter your number: ")
    if number != "777":
        print("❌ Access denied")
        sys.exit()
    else:
        print("✅ Access granted")

ask_user()