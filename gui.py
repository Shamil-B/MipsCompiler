import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Compiler")
        self.pack(expand=True, fill='both')
        self.create_widgets()

    def create_widgets(self):
        # Text Editor with line numbers
        editor_frame = tk.Frame(self)
        editor_frame.pack(side='left', expand=True, fill='both')

        self.editor = tk.Text(editor_frame, width=80, height=25, bg='black', fg='white',
                              insertbackground='white', selectbackground='gray', selectforeground='white',
                              font=("Consolas", 12))
        self.editor.pack(side='left', expand=True, fill='both')
        self.editor.tag_configure("line", background="black", foreground='gray')
        self.editor.bind("<Key>", self.update_line_numbers)
        self.scrollbar = tk.Scrollbar(editor_frame, command=self.editor.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.editor.config(yscrollcommand=self.scrollbar.set)
        self.linenumbers = tk.Text(editor_frame, width=4, height=25, bg="black", fg="gray", font=("Consolas", 12))
        self.linenumbers.pack(side='left', fill='y')
        self.linenumbers.insert('end', '1\n', 'line')
        self.linenumbers.config(state='disabled')

        # Buttons
        button_frame = tk.Frame(self, bg='black')
        button_frame.pack(side='top', anchor='ne')

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_editor, bg='red', fg='white')
        self.clear_button.pack(side='right', padx=5, pady=5)

        self.run_button = tk.Button(button_frame, text="Run", command=self.run_compiler, bg='blue', fg='white')
        self.run_button.pack(side='right', padx=5, pady=5)

        # Output area
        self.output = tk.Text(self, width=80, height=10, bg='black', fg='white', insertbackground='white',
                              font=("Consolas", 12))
        self.output.pack(side='bottom', fill='x')

        # Set the remaining space to be black
        self.config(bg='black')

    def update_line_numbers(self, event):
        self.linenumbers.config(state='normal')
        self.linenumbers.delete(1.0, tk.END)
        text = self.editor.get(1.0, tk.END)
        lines = text.count("\n")
        for i in range(1, lines+1):
            self.linenumbers.insert(tk.END, f"{i}\n", "line")
        self.linenumbers.config(state='disabled')

    def run_compiler(self):
        with open("input.txt", "w") as f:
            f.write(self.editor.get("1.0", "end"))
            
        # TODO: Implement your compiler logic here
        self.output.delete(1.0, tk.END)
        
        with open('output.txt', 'r') as result:
            for line in result:
                self.output.insert(tk.END, line)

        

    def clear_editor(self):
        self.editor.delete(1.0, tk.END)
        self.linenumbers.config(state='normal')
        self.linenumbers.delete(1.0, tk.END)
        self.linenumbers.insert('end', '1\n', 'line')
        self.linenumbers.config(state='disabled')


root = tk.Tk()
root.configure(bg='black')
app = Application(master=root)
app.mainloop()
