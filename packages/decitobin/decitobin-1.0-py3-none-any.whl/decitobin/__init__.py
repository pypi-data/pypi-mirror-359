import tkinter as tk
from tkinter import font

def dec2bin(decimal):
    if decimal < 0:
        raise ValueError("Decimal number must be non-negative")
    return bin(decimal)[2:]

def convert(*args):
    try:
        decimal = int(entry.get())
        result = dec2bin(decimal)
        result_var.set(result)
    except Exception as e:
        result_var.set(f"Error: {e}")

root = tk.Tk()
root.title("Decimal to Binary Converter")
root.geometry("350x150")
root.resizable(False, False)

f = font.Font(family="Arial", size=12)

tk.Label(root, text="Enter Decimal:", font=f).pack(pady=(15, 5))
entry = tk.Entry(root, font=f, justify="center")
entry.pack(pady=2)
entry.focus()

tk.Button(root, text="Convert", font=f, command=convert).pack(pady=5)

result_var = tk.StringVar()
result_entry = tk.Entry(root, font=f, textvariable=result_var, justify="center", state="readonly", fg="#007acc")
result_entry.pack(pady=(5, 10))

root.bind('<Return>', convert)
root.mainloop()