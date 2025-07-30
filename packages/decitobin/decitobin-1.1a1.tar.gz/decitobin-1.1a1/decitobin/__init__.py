import tkinter as tk
from tkinter import font
# -*- coding: utf-8 -*-

def dec2bin(decimal):
    if decimal < 0:
        raise ValueError("Decimal number must be non-negative")
    return bin(decimal)[2:]

def ascii2bin(text):
    return ' '.join(format(ord(c), '08b') for c in text)

def convert(*args):
    try:
        user_input = entry.get()
        if user_input.isdigit():
            result = dec2bin(int(user_input))
        else:
            result = ascii2bin(user_input)
        result_var.set(result)
    except Exception as e:
        result_var.set(f"Error: {e}")

root = tk.Tk()
root.title("Decimal & Text to Binary")
root.geometry("400x180")
root.resizable(False, False)

f = font.Font(family="Arial", size=12)

tk.Label(root, text="Enter Decimal or Text:", font=f).pack(pady=(15, 5))
entry = tk.Entry(root, font=f, justify="center")
entry.pack(pady=2)
entry.focus()

tk.Button(root, text="Convert", font=f, command=convert).pack(pady=5)

result_var = tk.StringVar()
result_entry = tk.Entry(root, font=f, textvariable=result_var, justify="center", state="readonly", fg="#007acc", width=50)
result_entry.pack(pady=(5, 10))

root.bind('<Return>', convert)
root.mainloop()