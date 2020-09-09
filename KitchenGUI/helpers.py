import tkinter as tk
import tkinter.messagebox as tkmb
from tkinter import N,E,S,W

def resizeSetup(target, rows=1, cols=1):
    for row in range(rows):
        tk.Grid.rowconfigure(target, row, weight=1)
    for col in range(cols):
        tk.Grid.columnconfigure(target, col, weight=1)
