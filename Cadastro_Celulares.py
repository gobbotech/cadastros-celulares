import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import sqlite3
import os
import configparser


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Cadastro de Celulares")

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.script_dir, "config.ini")

        self.create_database()

        self.layout = ttk.Frame(self)
        self.layout.pack(fill=tk.BOTH, expand=True)

        self.db_path_label = ttk.Label(self.layout, text=f"Caminho do Banco de Dados: {self.db_path}")
        self.db_path_label.pack(padx=10, pady=5, anchor=tk.W)

        self.choose_db_button = ttk.Button(self.layout, text="Configurações", command=self.open_settings_dialog)
        self.choose_db_button.pack(padx=10, pady=5, anchor=tk.W)

        self.new_celular_button = ttk.Button(self.layout, text="Novo Celular", command=self.show_new_celular_dialog)
        self.new_celular_button.pack(padx=10, pady=5, anchor=tk.W)

        self.email_button = ttk.Button(self.layout, text="Emails", command=self.show_emails_dialog)
        self.email_button.pack(padx=10, pady=5, anchor=tk.W)

        self.search_edit = ttk.Entry(self.layout)
        self.search_edit.pack(padx=10, pady=5, anchor=tk.W)
        self.search_edit.bind("<KeyRelease>", self.search_celular)

        self.table = ttk.Treeview(self.layout, columns=("Email", "Nome", "Departamento", "Telefone", "Modelo", "Número de Série", "IMEI 1", "IMEI 2"))
        self.table.heading("#0", text="ID")
        self.table.heading("Email", text="Email")
        self.table.heading("Nome", text="Nome")
        self.table.heading("Departamento", text="Departamento")
        self.table.heading("Telefone", text="Telefone")
        self.table.heading("Modelo", text="Modelo")
        self.table.heading("Número de Série", text="Número de Série")
        self.table.heading("IMEI 1", text="IMEI 1")
        self.table.heading("IMEI 2", text="IMEI 2")
        self.table.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.show_data()

    def create_database(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        if 'Database' not in self.config:
            self.config['Database'] = {'path': os.path.join(self.script_dir, 'dados.db')}
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)

        self.db_path = self.config.get('Database', 'path')

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS celulares ("
                            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                            "email TEXT,"
                            "nome TEXT,"
                            "departamento TEXT,"
                            "telefone TEXT,"
                            "modelo TEXT,"
                            "numero_serie TEXT,"
                            "imei1 TEXT,"
                            "imei2 TEXT,"
                            "vinculado INTEGER DEFAULT 0)")

        self.cursor.execute("CREATE TABLE IF NOT EXISTS emails ("
                            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                            "email TEXT,"
                            "senha TEXT,"
                            "vinculado INTEGER DEFAULT 0)")

    def open_settings_dialog(self):
        dialog = ConfiguracoesDialog(self)
        self.wait_window(dialog)

    def show_new_celular_dialog(self):
        dialog = CelularDialog(self)
        self.wait_window(dialog)

    def show_emails_dialog(self):
        dialog = EmailDialog(self)
        self.wait_window(dialog)

    def show_data(self):
        self.table.delete(*self.table.get_children())
        self.cursor.execute("SELECT * FROM celulares")
        for row in self.cursor.fetchall():
            self.table.insert("", "end", text=row[0], values=row[1:])

    def search_celular(self, event):
        text = self.search_edit.get().strip()

        self.table.delete(*self.table.get_children())

        if text:
            self.cursor.execute("SELECT * FROM celulares WHERE "
                                "email LIKE ? OR "
                                "nome LIKE ? OR "
                                "departamento LIKE ? OR "
                                "telefone LIKE ?",
                                ('%'+text+'%', '%'+text+'%', '%'+text+'%', '%'+text+'%'))
        else:
            self.cursor.execute("SELECT * FROM celulares")

        for row in self.cursor.fetchall():
            self.table.insert("", "end", text=row[0], values=row[1:])


class ConfiguracoesDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Configurações")

        self.layout = ttk.Frame(self)
        self.layout.pack(padx=10, pady=10)

        self.choose_db_button = ttk.Button(self.layout, text="Escolher Banco de Dados", command=self.choose_database)
        self.choose_db_button.grid(row=0, column=0, pady=5)

        self.theme_label = ttk.Label(self.layout, text="Tema:")
        self.theme_label.grid(row=1, column=0, pady=5)

        self.theme_combobox = ttk.Combobox(self.layout, values=["Claro", "Escuro"])
        self.theme_combobox.grid(row=1, column=1, pady=5)
        self.theme_combobox.bind("<<ComboboxSelected>>", self.change_theme)

        self.view_logs_button = ttk.Button(self.layout, text="Ver Logs", command=self.view_logs)
        self.view_logs_button.grid(row=2, column=0, pady=5)

    def choose_database(self):
        options = {'defaultextension': '.db', 'filetypes': [('Banco de Dados SQLite', '*.db')]}
        db_path = filedialog.askopenfilename(**options)

        if db_path:
            parent = self.master
            parent.config['Database']['path'] = db_path
            with open(parent.config_path, 'w') as configfile:
                parent.config.write(configfile)

            parent.db_path_label.config(text=f"Caminho do Banco de Dados: {db_path}")

    def change_theme(self, event):
        selected_theme = self.theme_combobox.get()
        if selected_theme == "Escuro":
            self.master.configure(background="black")
        else:
            self.master.configure(background="white")

    def view_logs(self):
        dialog = LogsDialog(self.master)
        self.wait_window(dialog)


class LogsDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Logs")

        self.layout = ttk.Frame(self)
        self.layout.pack(padx=10, pady=10)

        self.table = ttk.Treeview(self.layout, columns=("Data e Hora", "Ação", "Tabela"))
        self.table.heading("#0", text="ID")
        self.table.heading("Data e Hora", text="Data e Hora")
        self.table.heading("Ação", text="Ação")
        self.table.heading("Tabela", text="Tabela")
        self.table.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.show_logs()

    def show_logs(self):
        self.table.delete(*self.table.get_children())
        parent = self.master
        parent.cursor.execute("SELECT * FROM logs ORDER BY data_hora DESC")
        for row in parent.cursor.fetchall():
            self.table.insert("", "end", text=row[0], values=row[1:])


class CelularDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Novo Celular")

        self.layout = ttk.Frame(self)
        self.layout.pack(padx=10, pady=10)

        ttk.Label(self.layout, text="Nome:").grid(row=1, column=0, sticky=tk.W)
        self.nome_edit = ttk.Entry(self.layout)
        self.nome_edit.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(self.layout, text="Departamento:").grid(row=2, column=0, sticky=tk.W)
        self.departamento_edit = ttk.Entry(self.layout)
        self.departamento_edit.grid(row=2, column=1, sticky=tk.W)

        ttk.Label(self.layout, text="Telefone:").grid(row=3, column=0, sticky=tk.W)
        self.telefone_edit = ttk.Entry(self.layout)
        self.telefone_edit.grid(row=3, column=1, sticky=tk.W)

        ttk.Label(self.layout, text="Modelo:").grid(row=4, column=0, sticky=tk.W)
        self.modelo_edit = ttk.Entry(self.layout)
        self.modelo_edit.grid(row=4, column=1, sticky=tk.W)

        ttk.Label(self.layout, text="Número de Série:").grid(row=5, column=0, sticky=tk.W)
        self.numero_serie_edit = ttk.Entry(self.layout)
        self.numero_serie_edit.grid(row=5, column=1, sticky=tk.W)

        ttk.Label(self.layout, text="IMEI 1:").grid(row=6, column=0, sticky=tk.W)
        self.imei1_edit = ttk.Entry(self.layout)
        self.imei1_edit.grid(row=6, column=1, sticky=tk.W)

        ttk.Label(self.layout, text="IMEI 2:").grid(row=7, column=0, sticky=tk.W)
        self.imei2_edit = ttk.Entry(self.layout)
        self.imei2_edit.grid(row=7, column=1, sticky=tk.W)

        ttk.Button(self.layout, text="Selecionar Email", command=self.select_email).grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.selected_email_label = ttk.Label(self.layout, text="")
        self.selected_email_label.grid(row=0, column=2, padx=5, pady=5)

        ttk.Button(self.layout, text="Salvar", command=self.save_data).grid(row=8, column=0, columnspan=2)

    def select_email(self):
        dialog = EmailSelectionDialog(self.master)  
        self.wait_window(dialog)
        selected_email = dialog.selected_email
        if selected_email:
            self.selected_email_label.config(text=f"Email selecionado: {selected_email}")

    def save_data(self):
        nome = self.nome_edit.get()
        departamento = self.departamento_edit.get()
        telefone = self.telefone_edit.get()
        modelo = self.modelo_edit.get()
        numero_serie = self.numero_serie_edit.get()
        imei1 = self.imei1_edit.get()
        imei2 = self.imei2_edit.get()
        email = self.selected_email_label.cget("text").split(":")[-1].strip()

        parent = self.master
        try:
            parent.cursor.execute("INSERT INTO celulares (email, nome, departamento, telefone, modelo, numero_serie, imei1, imei2) "
                                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (email, nome, departamento, telefone, modelo, numero_serie, imei1, imei2))
            parent.conn.commit()

            messagebox.showinfo("Salvar", "Dados do novo celular salvos com sucesso.")

            parent.show_data()  
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar os dados: {e}")


class EmailDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Escolher Email")

        self.layout = ttk.Frame(self)
        self.layout.pack(padx=10, pady=10)

        self.table = ttk.Treeview(self.layout, columns=("Email", "Senha", "Vinculado"))
        self.table.heading("#0", text="ID")
        self.table.heading("Email", text="Email")
        self.table.heading("Senha", text="Senha")
        self.table.heading("Vinculado", text="Vinculado")
        self.table.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.search_email_edit = ttk.Entry(self.layout)
        self.search_email_edit.pack(padx=10, pady=5)
        self.search_email_edit.bind("<KeyRelease>", self.search_email)

        ttk.Button(self.layout, text="Novo email", command=self.choose_email).pack(padx=10, pady=5)

        self.show_emails()

    def show_emails(self):
        self.table.delete(*self.table.get_children())
        parent = self.master
        parent.cursor.execute("SELECT * FROM emails")
        for row in parent.cursor.fetchall():
            vinculado = "SIM" if row[3] == 1 else "NÃO"
            self.table.insert("", "end", text=row[0], values=(row[1], row[2], vinculado))

    def choose_email(self):
        selected_item = self.table.focus()
        if selected_item:
            selected_email = self.table.item(selected_item)['values'][0]
            messagebox.showinfo("Escolher Email", f"Email escolhido: {selected_email}")

    def search_email(self, event):
        text = self.search_email_edit.get().strip()

        self.table.delete(*self.table.get_children())

        if text:
            parent = self.master
            parent.cursor.execute("SELECT * FROM emails WHERE email LIKE ? AND (vinculado = 0 OR vinculado IS NULL)", ('%'+text+'%',))
        else:
            parent.cursor.execute("SELECT * FROM emails")

        for row in parent.cursor.fetchall():
            vinculado = "SIM" if row[3] == 1 else "NÃO"
            self.table.insert("", "end", text=row[0], values=(row[1], row[2], vinculado))


class EmailInputDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Novo Email")

        self.layout = ttk.Frame(self)
        self.layout.pack(padx=10, pady=10)

        self.email_edit = ttk.Entry(self.layout)
        self.email_edit.grid(row=0, column=1, padx=5, pady=5)

        self.senha_edit = ttk.Entry(self.layout)
        self.senha_edit.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.layout, text="Email:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(self.layout, text="Senha:").grid(row=1, column=0, sticky=tk.W)

        ttk.Button(self.layout, text="Salvar", command=self.save_data).grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def save_data(self):
        email = self.email_edit.get()
        senha = self.senha_edit.get()

        parent = self.master
        try:
            parent.cursor.execute("INSERT INTO emails (email, senha) VALUES (?, ?)", (email, senha))
            parent.conn.commit()
            messagebox.showinfo("Salvar", "Novo email salvo com sucesso.")
            parent.show_emails()  
        except sqlite3.Error as e:
            messagebox.showerror("Erro", f"Erro ao salvar o email: {e}")


class EmailSelectionDialog(tk.Toplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("Escolher Email")

        self.layout = ttk.Frame(self)
        self.layout.pack(padx=10, pady=10)

        self.table = ttk.Treeview(self.layout, columns=("Email",))
        self.table.heading("#0", text="ID")
        self.table.heading("Email", text="Email")
        self.table.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.select_button = ttk.Button(self.layout, text="Selecionar", command=self.select_email)
        self.select_button.pack(padx=10, pady=5)

        self.selected_email = None

        self.show_emails()

    def show_emails(self):
        self.table.delete(*self.table.get_children())
        parent = self.master
        parent.cursor.execute("SELECT * FROM emails WHERE vinculado = 0 OR vinculado IS NULL")
        for row in parent.cursor.fetchall():
            self.table.insert("", "end", text=row[0], values=(row[1],))

    def select_email(self):
        selected_item = self.table.focus()
        if selected_item:
            self.selected_email = self.table.item(selected_item)['values'][0]
            self.destroy()


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()