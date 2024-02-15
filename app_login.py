import sys
import os
import datetime
import configparser
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QLineEdit, QDialog, QFileDialog, QHBoxLayout, QMessageBox, QStackedWidget
)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from ldap3 import Server, Connection, SIMPLE, SYNC
from PyQt5.QtCore import pyqtSignal


class NextWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.init_ui(username)

    def init_ui(self, username):
        self.setWindowTitle('Next Window')
        self.setGeometry(400, 400, 300, 150)

        layout = QVBoxLayout()
        welcome_label = QLabel(f'Welcome, {username}!')
        layout.addWidget(welcome_label)
        self.setLayout(layout)


class AutenticacaoAD(QWidget):
    # Define a signal for successful login
    login_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Login')
        self.setGeometry(300, 300, 300, 150)

        layout = QVBoxLayout()

        self.label_username = QLabel('Username:')
        self.label_password = QLabel('Password:')
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('Login', self)

        layout.addWidget(self.label_username)
        layout.addWidget(self.username_input)
        layout.addWidget(self.label_password)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        # Connect the login button to the authentication method
        self.login_button.clicked.connect(self.authenticate)
        self.username_input.returnPressed.connect(self.authenticate)
        self.password_input.returnPressed.connect(self.authenticate)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username:
            self.show_message('Campo do usuario em branco, favor inserir usuario.')
            return

        if not password:
            self.show_message('Campo de senha em branco, favor inserir sua senha.')
            return

        server = Server('ldap://192.168.200.25:389', get_info=SYNC)

        try:
            conn = Connection(server, user=f"{username}@aarsl.local", password=password, authentication=SIMPLE)
            conn.bind()

            if conn.bind():
                conn.unbind()
                self.login_successful.emit(username)
            else:
                conn.unbind()
                self.show_message('Usuario ou senha invalida.')
        except Exception as e:
            print(f"Authentication failed: {e}")
            self.show_message('Usuario ou senha invalida.')

    def show_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def open_main_window(self, username):
        main_window = MainWindow(username)
        main_window.show()
        self.hide()


class CelularDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Celular")

        layout = QVBoxLayout()

        self.email_button = QPushButton("Escolher Email")
        self.email_button.clicked.connect(self.show_emails_dialog)
        layout.addWidget(self.email_button)

        self.nome_edit = QLineEdit()
        self.departamento_edit = QLineEdit()
        self.telefone_edit = QLineEdit()
        self.modelo_edit = QLineEdit()
        self.numero_serie_edit = QLineEdit()
        self.imei1_edit = QLineEdit()
        self.imei2_edit = QLineEdit()

        # Connect QLineEdit textEdited event to uppercase conversion function
        self.nome_edit.textEdited.connect(self.to_uppercase)
        self.departamento_edit.textEdited.connect(self.to_uppercase)
        self.telefone_edit.textEdited.connect(self.to_uppercase)
        self.modelo_edit.textEdited.connect(self.to_uppercase)
        self.numero_serie_edit.textEdited.connect(self.to_uppercase)
        self.imei1_edit.textEdited.connect(self.to_uppercase)
        self.imei2_edit.textEdited.connect(self.to_uppercase)

        layout.addWidget(QLabel("Nome:"))
        layout.addWidget(self.nome_edit)
        layout.addWidget(QLabel("Departamento:"))
        layout.addWidget(self.departamento_edit)
        layout.addWidget(QLabel("Telefone:"))
        layout.addWidget(self.telefone_edit)
        layout.addWidget(QLabel("Modelo do Celular:"))
        layout.addWidget(self.modelo_edit)
        layout.addWidget(QLabel("Número de Série:"))
        layout.addWidget(self.numero_serie_edit)
        layout.addWidget(QLabel("IMEI 1:"))
        layout.addWidget(self.imei1_edit)
        layout.addWidget(QLabel("IMEI 2:"))
        layout.addWidget(self.imei2_edit)

        save_button = QPushButton("Salvar")
        save_button.clicked.connect(self.save_data)

        layout.addWidget(save_button)

        self.setLayout(layout)

        self.selected_email = None

    def show_emails_dialog(self):
        dialog = EmailDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            selected_email = dialog.selected_email
            self.selected_email = selected_email
            self.email_button.setText(f"Email Escolhido: {selected_email}")

    def save_data(self):
        if self.selected_email:
            confirmation_dialog = ConfirmationDialog(self, self.selected_email)
            result = confirmation_dialog.exec_()
            if result == QDialog.Accepted:
                db = QSqlDatabase.database()
                query = QSqlQuery(db)

                query.prepare("INSERT INTO celulares (email, nome, departamento, telefone, modelo, numero_serie, imei1, imei2) "
                              "VALUES (:email, :nome, :departamento, :telefone, :modelo, :numero_serie, :imei1, :imei2)")

                query.bindValue(":email", self.selected_email)
                query.bindValue(":nome", self.nome_edit.text())
                query.bindValue(":departamento", self.departamento_edit.text())
                query.bindValue(":telefone", self.telefone_edit.text())
                query.bindValue(":modelo", self.modelo_edit.text())
                query.bindValue(":numero_serie", self.numero_serie_edit.text())
                query.bindValue(":imei1", self.imei1_edit.text())
                query.bindValue(":imei2", self.imei2_edit.text())

                if query.exec_():
                    self.show_success_message("Salvo com sucesso!")
                    self.accept()
                    self.parent().show_data()  # Call function to update the table
                else:
                    print("Erro ao inserir dados:", query.lastError().text())
        else:
            self.show_error_message("Escolha um email antes de salvar.")

    def show_success_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Sucesso")
        msg.exec_()

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Erro")
        msg.exec_()

    def to_uppercase(self, text):
        return text.upper()


class ConfirmationDialog(QDialog):
    def __init__(self, parent=None, email=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmação")

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"Tem certeza que deseja usar o email '{email}'?"))

        confirm_button = QPushButton("Confirmar")
        confirm_button.clicked.connect(self.accept)

        cancel_button = QPushButton("Cancelar")
        cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)


class EmailDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Escolher Email")

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Email", "Senha"])

        layout.addWidget(self.table)

        self.search_email_edit = QLineEdit()
        self.search_email_edit.setPlaceholderText("Buscar por e-mail...")
        self.search_email_edit.textChanged.connect(self.search_email)
        layout.addWidget(self.search_email_edit)

        self.new_email_button = QPushButton("Novo Email")
        self.new_email_button.clicked.connect(self.show_new_email_dialog)
        layout.addWidget(self.new_email_button)

        self.choose_email_button = QPushButton("Escolher Email")
        self.choose_email_button.clicked.connect(self.choose_email)
        layout.addWidget(self.choose_email_button)

        self.setLayout(layout)

        self.selected_email = None

        self.show_emails()

    def show_emails(self):
        query = QSqlQuery("SELECT email, senha FROM emails")
        self.table.setRowCount(0)

        while query.next():
            row_position = self.table.rowCount()
            email = query.value(0)
            senha = query.value(1)

            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(email))
            self.table.setItem(row_position, 1, QTableWidgetItem(senha))

        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.clicked.connect(self.handle_table_click)

    def handle_table_click(self):
        pass

    def show_new_email_dialog(self):
        dialog = EmailInputDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.show_emails()

    def choose_email(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            self.selected_email = self.table.item(selected_row, 0).text()
            self.accept()

    def search_email(self):
        text = self.search_email_edit.text().strip()

        if text:
            query = QSqlQuery(f"SELECT email, senha FROM emails WHERE email LIKE '%{text}%'")
        else:
            query = QSqlQuery("SELECT email, senha FROM emails")

        self.table.setRowCount(0)

        while query.next():
            row_position = self.table.rowCount()
            email = query.value(0)
            senha = query.value(1)

            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(email))
            self.table.setItem(row_position, 1, QTableWidgetItem(senha))

    def show_new_email_dialog(self):
        dialog = EmailInputDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.show_emails()


class EmailInputDialog(QDialog):
    def __init__(self, parent=None, email=None, senha=None):
        super().__init__(parent)
        self.setWindowTitle("Novo Email")

        layout = QVBoxLayout()

        self.email_edit = QLineEdit()
        self.email_edit.setText(email if email else "")
        self.senha_edit = QLineEdit()
        self.senha_edit.setText(senha if senha else "")

        self.email_edit.textEdited.connect(self.to_uppercase)

        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_edit)
        layout.addWidget(QLabel("Senha:"))
        layout.addWidget(self.senha_edit)

        save_button = QPushButton("Salvar")
        save_button.clicked.connect(self.save_data)

        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_data(self):
        email = self.email_edit.text()
        senha = self.senha_edit.text()

        if email and senha:
            db = QSqlDatabase.database()
            query = QSqlQuery(db)

            query.prepare("INSERT INTO emails (email, senha) VALUES (:email, :senha)")
            query.bindValue(":email", email)
            query.bindValue(":senha", senha)

            if query.exec_():
                self.accept()
            else:
                print("Erro ao inserir email:", query.lastError().text())
        else:
            self.show_error_message("Preencha todos os campos.")

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Erro")
        msg.exec_()

    def to_uppercase(self, text):
        return text.upper()


class MainWindow(QWidget):
    def __init__(self, username):
        super().__init__()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.ini")
        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        if 'Database' not in self.config:
            self.config['Database'] = {'path': os.path.join(script_dir, 'dados.db')}

        self.create_database()

        self.layout = QVBoxLayout()

        self.db_path_label = QLabel(f"Caminho do Banco de Dados: {self.db.databaseName()}")
        self.layout.addWidget(self.db_path_label)

        self.choose_db_button = QPushButton("Configurações")
        self.choose_db_button.clicked.connect(self.open_settings_dialog)
        self.layout.addWidget(self.choose_db_button)

        self.new_celular_button = QPushButton("Novo Celular")
        self.new_celular_button.clicked.connect(self.show_new_celular_dialog)
        self.layout.addWidget(self.new_celular_button)

        self.email_button = QPushButton("Emails")
        self.email_button.clicked.connect(self.show_emails_dialog)
        self.layout.addWidget(self.email_button)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Buscar por celular...")
        self.search_edit.textChanged.connect(self.search_celular)
        self.layout.addWidget(self.search_edit)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["Email", "Nome", "Departamento", "Telefone", "Modelo", "Número de Série", "IMEI 1", "IMEI 2"])
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        self.show_data()

        self.setWindowTitle("Cadastro de Celulares")

    def create_database(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        db_path = self.config.get('Database', 'path')
        self.db.setDatabaseName(db_path)

        if not self.db.open():
            print("Erro ao abrir o banco de dados.")
            return

        query = QSqlQuery()
        query.exec_(
            "CREATE TABLE IF NOT EXISTS celulares ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "email TEXT,"
            "nome TEXT,"
            "departamento TEXT,"
            "telefone TEXT,"
            "modelo TEXT,"
            "numero_serie TEXT,"
            "imei1 TEXT,"
            "imei2 TEXT)")

        query.exec_(
            "CREATE TABLE IF NOT EXISTS emails ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "email TEXT,"
            "senha TEXT)")

    def show_data(self):
        query = QSqlQuery("SELECT email, nome, departamento, telefone, modelo, numero_serie, imei1, imei2 FROM celulares")
        self.table.setRowCount(0)

        while query.next():
            row_position = self.table.rowCount()
            email = query.value(0)
            nome = query.value(1)
            departamento = query.value(2)
            telefone = query.value(3)
            modelo = query.value(4)
            numero_serie = query.value(5)
            imei1 = query.value(6)
            imei2 = query.value(7)

            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(email))
            self.table.setItem(row_position, 1, QTableWidgetItem(nome))
            self.table.setItem(row_position, 2, QTableWidgetItem(departamento))
            self.table.setItem(row_position, 3, QTableWidgetItem(telefone))
            self.table.setItem(row_position, 4, QTableWidgetItem(modelo))
            self.table.setItem(row_position, 5, QTableWidgetItem(numero_serie))
            self.table.setItem(row_position, 6, QTableWidgetItem(imei1))
            self.table.setItem(row_position, 7, QTableWidgetItem(imei2))

    def search_celular(self):
        text = self.search_edit.text().strip()

        if text:
            query = QSqlQuery(
                f"SELECT email, nome, departamento, telefone, modelo, numero_serie, imei1, imei2 FROM celulares "
                f"WHERE nome LIKE '%{text}%' "
                f"OR departamento LIKE '%{text}%' "
                f"OR telefone LIKE '%{text}%' "
                f"OR modelo LIKE '%{text}%' "
                f"OR numero_serie LIKE '%{text}%' "
                f"OR imei1 LIKE '%{text}%' "
                f"OR imei2 LIKE '%{text}%'")
        else:
            query = QSqlQuery("SELECT email, nome, departamento, telefone, modelo, numero_serie, imei1, imei2 FROM celulares")

        self.table.setRowCount(0)

        while query.next():
            row_position = self.table.rowCount()
            email = query.value(0)
            nome = query.value(1)
            departamento = query.value(2)
            telefone = query.value(3)
            modelo = query.value(4)
            numero_serie = query.value(5)
            imei1 = query.value(6)
            imei2 = query.value(7)

            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(email))
            self.table.setItem(row_position, 1, QTableWidgetItem(nome))
            self.table.setItem(row_position, 2, QTableWidgetItem(departamento))
            self.table.setItem(row_position, 3, QTableWidgetItem(telefone))
            self.table.setItem(row_position, 4, QTableWidgetItem(modelo))
            self.table.setItem(row_position, 5, QTableWidgetItem(numero_serie))
            self.table.setItem(row_position, 6, QTableWidgetItem(imei1))
            self.table.setItem(row_position, 7, QTableWidgetItem(imei2))

    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec_()

    def show_new_celular_dialog(self):
        dialog = CelularDialog(self)
        dialog.exec_()
        self.show_data()

    def show_emails_dialog(self):
        dialog = EmailDialog(self)
        dialog.exec_()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")

        layout = QVBoxLayout()

        self.db_path_label = QLabel(f"Caminho do Banco de Dados: {parent.db.databaseName()}")
        layout.addWidget(self.db_path_label)

        self.choose_db_button = QPushButton("Escolher Banco de Dados")
        self.choose_db_button.clicked.connect(self.choose_db_file)
        layout.addWidget(self.choose_db_button)

        save_button = QPushButton("Salvar")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def choose_db_file(self):
        file_dialog = QFileDialog()
        db_file_path, _ = file_dialog.getSaveFileName(self, "Escolha o Banco de Dados", "", "SQLite (*.db)")
        if db_file_path:
            self.db_path_label.setText(f"Caminho do Banco de Dados: {db_file_path}")

    def save_settings(self):
        new_db_path = self.db_path_label.text().split(": ")[1]
        config = configparser.ConfigParser()
        config.read("config.ini")
        if 'Database' not in config:
            config['Database'] = {}
        config['Database']['path'] = new_db_path

        with open("config.ini", "w") as config_file:
            config.write(config_file)


class MainWindowStackedWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.stacked_widget = QStackedWidget()

        self.login_widget = AutenticacaoAD()
        self.login_widget.login_successful.connect(self.show_main_window)
        self.stacked_widget.addWidget(self.login_widget)

        self.main_window_widget = MainWindow("")
        self.stacked_widget.addWidget(self.main_window_widget)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stacked_widget)

    def show_main_window(self, username):
        self.main_window_widget = MainWindow(username)
        self.stacked_widget.addWidget(self.main_window_widget)
        self.stacked_widget.setCurrentWidget(self.main_window_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindowStackedWidget()
    window.setWindowTitle("Cadastro de Celulares")
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())
