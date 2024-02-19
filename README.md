Cadastro de Celulares
---------------------
Este é um programa desenvolvido em Python utilizando a biblioteca Tkinter para criar uma interface gráfica. O programa permite o cadastro de informações de celulares, tais como nome, departamento, telefone, modelo, número de série e IMEI, além de associar esses dados a um endereço de e-mail.

Funcionalidades Principais:
Cadastro de Celulares:

Permite adicionar novos celulares com informações como nome, departamento, telefone, modelo, número de série e IMEI.
Gerenciamento de E-mails:

Possibilita escolher e associar um endereço de e-mail ao cadastro de um celular.
Configurações:

Permite selecionar o banco de dados SQLite a ser utilizado.
Opção para escolher entre temas claro e escuro.
Estrutura do Código:
MainWindow:

Classe principal que representa a janela principal da aplicação.
Mostra a lista de celulares cadastrados e fornece botões para acesso às funcionalidades de cadastro de novos celulares, gerenciamento de e-mails e configurações.
ConfiguracoesDialog:

Janela para configurar o banco de dados e o tema da aplicação.
LogsDialog:

Janela para visualizar registros de logs.
CelularDialog:

Janela para cadastrar novos celulares, permitindo a seleção de um e-mail existente.
EmailDialog:

Janela para escolher e associar um endereço de e-mail aos celulares cadastrados.
EmailInputDialog:

Janela para inserir um novo endereço de e-mail.
EmailSelectionDialog:

Janela para selecionar um e-mail existente.
Como Executar:
Para executar o programa, basta executar o código Python fornecido. Certifique-se de ter as bibliotecas necessárias instaladas, como tkinter, sqlite3 e configparser. O programa abrirá uma janela com as opções de cadastro de celulares, gerenciamento de e-mails e configurações.
