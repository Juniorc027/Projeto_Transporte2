import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import re  # adicionado para validação de expressões regulares
import plotly.express as px  # adicionado para gráficos interativos
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # modificado

# ===== CONEXÃO E FUNÇÕES DO BANCO MySQL (Cadastros) =====

def conectar_banco():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",                # Altere conforme seu usuário MySQL
            password="",                # Altere conforme sua senha MySQL
            database="projeto_transporte"
        )
        return conexao
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {err}")
        return None

def inserir_responsavel(conexao, nome, contato, endereco):
    if conexao is None:
        return
    cursor = conexao.cursor()
    try:
        query = "INSERT INTO responsaveis (nome, contato, endereco) VALUES (%s, %s, %s)"
        dados = (nome, contato, endereco)
        cursor.execute(query, dados)
        conexao.commit()
        print(f"Responsável {nome} inserido com sucesso!")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao inserir responsável: {err}")
    finally:
        cursor.close()

def listar_responsaveis(conexao):
    if conexao is None:
        return []
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT * FROM responsaveis")
        responsaveis = cursor.fetchall()
        return responsaveis
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao listar responsáveis: {err}")
        return []
    finally:
        cursor.close()

def excluir_responsavel(conexao, id_responsavel):
    if conexao is None:
        return
    cursor = conexao.cursor()
    try:
        # Removendo todos os alunos vinculados ao responsável
        cursor.execute("DELETE FROM alunos WHERE responsavel_id = %s", (id_responsavel,))
        cursor.execute("DELETE FROM responsaveis WHERE id = %s", (id_responsavel,))
        conexao.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao excluir responsável: {err}")
    finally:
        cursor.close()

def inserir_aluno_mysql(conexao, nome, idade, serie, responsavel_id, escola_id):
    if conexao is None:
        return
    cursor = conexao.cursor()
    try:
        query = "INSERT INTO alunos (nome, idade, serie, responsavel_id, escola_id) VALUES (%s, %s, %s, %s, %s)"
        dados = (nome, idade, serie, responsavel_id, escola_id)
        cursor.execute(query, dados)
        conexao.commit()
        print(f"Aluno {nome} cadastrado com sucesso!")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao inserir aluno: {err}")
    finally:
        cursor.close()

def listar_alunos_mysql(conexao):
    if conexao is None:
        return []
    cursor = conexao.cursor()
    try:
        query = """
        SELECT alunos.id, alunos.nome, alunos.idade, alunos.serie, responsaveis.nome AS responsavel, escolas.nome AS escola 
        FROM alunos
        LEFT JOIN responsaveis ON alunos.responsavel_id = responsaveis.id
        LEFT JOIN escolas ON alunos.escola_id = escolas.id
        """
        cursor.execute(query)
        alunos = cursor.fetchall()
        return alunos
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao listar alunos: {err}")
        return []
    finally:
        cursor.close()

def inserir_escola(conexao, nome, endereco, horario_entrada, horario_saida):
    if conexao is None:
        return
    cursor = conexao.cursor()
    try:
        query = "INSERT INTO escolas (nome, endereco, horario_entrada, horario_saida) VALUES (%s, %s, %s, %s)"
        dados = (nome, endereco, horario_entrada, horario_saida)
        cursor.execute(query, dados)
        conexao.commit()
        print(f"Escola {nome} cadastrada com sucesso!")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao inserir escola: {err}")
    finally:
        cursor.close()

def listar_escolas(conexao):
    if conexao is None:
        return []
    cursor = conexao.cursor()
    try:
        query = "SELECT id, nome, endereco, horario_entrada, horario_saida FROM escolas"
        cursor.execute(query)
        escolas = cursor.fetchall()
        return escolas
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao listar escolas: {err}")
        return []
    finally:
        cursor.close()

# ===== FUNÇÕES DO BANCO MySQL (Finanças) =====

def criar_banco_financas(conexao):
    if conexao is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não estabelecida.")
        return
    cursor = conexao.cursor()
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsaveis (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            contato VARCHAR(255) NOT NULL,
            endereco VARCHAR(255) NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS escolas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            endereco VARCHAR(255) NOT NULL,
            horario_entrada TIME NOT NULL,
            horario_saida TIME NOT NULL
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            idade INT NOT NULL,
            serie VARCHAR(255) NOT NULL,
            responsavel_id INT NOT NULL,
            escola_id INT NOT NULL,
            FOREIGN KEY (responsavel_id) REFERENCES responsaveis(id),
            FOREIGN KEY (escola_id) REFERENCES escolas(id)
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            aluno_id INT NOT NULL,
            valor DECIMAL(10, 2) NOT NULL,
            data DATE NOT NULL,
            status ENUM('pendente', 'pago') NOT NULL,
            FOREIGN KEY (aluno_id) REFERENCES alunos(id)
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INT AUTO_INCREMENT PRIMARY KEY,
            pagamento_id INT NOT NULL,
            data_pagamento DATETIME NOT NULL,
            FOREIGN KEY (pagamento_id) REFERENCES pagamentos(id)
        )
        """)
        conexao.commit()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao criar tabelas: {err}")
    finally:
        cursor.close()

def registrar_pagamento_mysql(conexao, aluno_id, valor, data_vencimento):
    if conexao is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não estabelecida.")
        return
    cursor = conexao.cursor()
    try:
        valor = float(valor)
        datetime.strptime(data_vencimento, "%Y-%m-%d")
        cursor.execute("SELECT id FROM alunos WHERE id=%s", (aluno_id,))
        if not cursor.fetchone():
            messagebox.showerror("Erro", "Aluno não encontrado")
            return
        cursor.execute(
            "INSERT INTO pagamentos (aluno_id, valor, data, status) VALUES (%s, %s, %s, 'pendente')",
            (aluno_id, valor, data_vencimento)
        )
        conexao.commit()
        messagebox.showinfo("Sucesso", "Pagamento registrado com sucesso")
    except ValueError:
        messagebox.showerror("Erro", "Valor deve ser numérico e data no formato AAAA-MM-DD")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao registrar pagamento: {err}")
    finally:
        cursor.close()

def atualizar_status_pagamento_mysql(conexao, pagamento_id):
    if conexao is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não estabelecida.")
        return
    cursor = conexao.cursor()
    try:
        cursor.execute("UPDATE pagamentos SET status = 'pago' WHERE id = %s", (pagamento_id,))
        data_pagamento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO historico (pagamento_id, data_pagamento) VALUES (%s, %s)",
                       (pagamento_id, data_pagamento))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Pagamento confirmado")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao atualizar pagamento: {err}")
    finally:
        cursor.close()

def obter_pagamento_pendentes_mysql(conexao):
    cursor = conexao.cursor()
    try:
        cursor.execute("""
        SELECT p.id, a.nome, p.valor, p.data 
        FROM pagamentos p
        INNER JOIN alunos a ON p.aluno_id = a.id
        WHERE p.status = 'pendente'
        """)
        resultados = cursor.fetchall()
        return resultados
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao obter pagamentos pendentes: {err}")
        return []
    finally:
        cursor.close()

def obter_historico_completo_mysql(conexao):
    if conexao is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não estabelecida.")
        return []
    cursor = conexao.cursor()
    try:
        cursor.execute("""
        SELECT a.nome, p.valor, p.data, h.data_pagamento FROM historico h
        INNER JOIN pagamentos p ON h.pagamento_id = p.id
        INNER JOIN alunos a ON p.aluno_id = a.id
        """)
        resultados = cursor.fetchall()
        return resultados
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao obter histórico completo: {err}")
        return []
    finally:
        cursor.close()

def gerar_relatorio_pagamentos_mysql(conexao):
    if conexao is None:
        messagebox.showerror("Erro", "Conexão com o banco de dados não estabelecida.")
        return [0, 0]
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT status, COUNT(*) FROM pagamentos GROUP BY status")
        dados = cursor.fetchall()
        pendentes = 0
        pagos = 0
        for status, count in dados:
            if status == 'pendente':
                pendentes = count
            elif status == 'pago':
                pagos = count
        return [pendentes, pagos]
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao gerar relatório de pagamentos: {err}")
        return [0, 0]
    finally:
        cursor.close()

# ===== INTERFACE UNIFICADA =====

def add_focus_binding(widget):
    widget.bind("<Button-1>", lambda event: (widget.focus_force(), "break"))

class UnifiedApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        # Customização visual aprimorada
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f8ff")  # fundo azul-claro
        style.configure("TLabel", background="#f0f8ff", foreground="#154360", font=("Arial", 12))
        style.configure("TButton", background="#5dade2", foreground="white", font=("Arial", 12, "bold"), borderwidth=2, relief="raised")
        style.configure("TEntry", foreground="#154360", font=("Helvetica", 12))
        style.map("TButton", background=[("active", "#3498db")], relief=[("pressed", "sunken")])
        self.configure(background="#f0f8ff")
        self.title("Sistema de Transporte Escolar - Unificado")
        self.geometry("900x700")
        
        # Frame principal para centralizar as opções
        self.frame_principal = ttk.Frame(self)
        self.frame_principal.pack(expand=True, fill="both")
        
        # Botões principais
        self.btn_cadastros = ttk.Button(self.frame_principal, text="Cadastros", command=self.mostrar_aba_cadastros)
        self.btn_financas = ttk.Button(self.frame_principal, text="Finanças", command=self.mostrar_aba_financas)
        self.btn_cadastros.pack(pady=20)
        self.btn_financas.pack(pady=20)
        
        # Frame para submenus de cadastros
        self.frame_cadastros = ttk.Frame(self)
        self.notebook_cadastros = ttk.Notebook(self.frame_cadastros)
        self.frame_responsaveis = ttk.Frame(self.notebook_cadastros)
        self.frame_alunos = ttk.Frame(self.notebook_cadastros)
        self.frame_escolas = ttk.Frame(self.notebook_cadastros)
        self.notebook_cadastros.add(self.frame_responsaveis, text="Responsáveis")
        self.notebook_cadastros.add(self.frame_alunos, text="Alunos")
        self.notebook_cadastros.add(self.frame_escolas, text="Escolas")
        self.notebook_cadastros.pack(expand=True, fill="both")
        # Botão para voltar ao início no menu Cadastros
        ttk.Button(self.frame_cadastros, text="Voltar ao início", command=self.voltar_inicio).pack(pady=10)
        
        # Frame para submenus de finanças
        self.frame_financas = ttk.Frame(self)
        self.notebook_financas = ttk.Notebook(self.frame_financas)
        self.frame_pagamentos = ttk.Frame(self.notebook_financas)
        self.frame_relatorios = ttk.Frame(self.notebook_financas)
        self.notebook_financas.add(self.frame_pagamentos, text="Pagamentos")
        self.notebook_financas.add(self.frame_relatorios, text="Relatórios")
        self.notebook_financas.pack(expand=True, fill="both")
        # Botão para voltar ao início no menu Finanças
        ttk.Button(self.frame_financas, text="Voltar ao início", command=self.voltar_inicio).pack(pady=10)
        
        # Conexão MySQL para Cadastros e Finanças
        self.conexao_mysql = conectar_banco()
        if self.conexao_mysql is not None:
            # Cria o banco MySQL para Finanças (se ainda não existir)
            criar_banco_financas(self.conexao_mysql)
        
        self.criar_aba_cadastros()
        self.criar_aba_financas()
    
    def voltar_inicio(self):
        self.frame_cadastros.pack_forget()
        self.frame_financas.pack_forget()
        self.frame_principal.pack(expand=True, fill="both")
    
    def mostrar_aba_cadastros(self):
        self.frame_principal.pack_forget()
        self.frame_financas.pack_forget()
        self.frame_cadastros.pack(expand=True, fill="both")
    
    def mostrar_aba_financas(self):
        self.frame_principal.pack_forget()
        self.frame_cadastros.pack_forget()
        self.frame_financas.pack(expand=True, fill="both")
    
    # ----- Aba Cadastros (MySQL) ----------
    def criar_aba_cadastros(self):
        # Responsáveis
        try:
            self.frame_responsaveis.grid_columnconfigure(0, weight=1)
            self.frame_responsaveis.grid_columnconfigure(1, weight=1)
            tk.Label(self.frame_responsaveis, text="Nome:", font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky="e")
            self.entry_nome_resp = tk.Entry(self.frame_responsaveis, font=("Arial", 12))
            self.entry_nome_resp.grid(row=0, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_nome_resp)
            tk.Label(self.frame_responsaveis, text="Contato:", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky="e")
            self.entry_contato_resp = tk.Entry(self.frame_responsaveis, font=("Arial", 12))
            self.entry_contato_resp.grid(row=1, column=1, pady=5, sticky="w")
            self.entry_contato_resp.insert(0, "()")  # campo preenchido com "()"
            add_focus_binding(self.entry_contato_resp)
            tk.Label(self.frame_responsaveis, text="Endereço:", font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky="e")
            self.entry_endereco_resp = tk.Entry(self.frame_responsaveis, font=("Arial", 12))
            self.entry_endereco_resp.grid(row=2, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_endereco_resp)
            ttk.Button(self.frame_responsaveis, text="Cadastrar Responsável", command=self.cadastrar_responsavel).grid(row=3, column=0, columnspan=2, pady=10)
            self.tree_responsaveis = ttk.Treeview(self.frame_responsaveis, columns=("ID", "Nome", "Contato", "Endereço"), show="headings")
            for col in ("ID", "Nome", "Contato", "Endereço"):
                self.tree_responsaveis.heading(col, text=col)
                self.tree_responsaveis.column(col, width=100, anchor="center")
            self.tree_responsaveis.grid(row=4, column=0, columnspan=2, pady=10)
            tk.Label(self.frame_responsaveis, text="ID do Responsável:", font=("Arial", 12)).grid(row=5, column=0, pady=5, sticky="e")
            self.entry_id_resp = tk.Entry(self.frame_responsaveis, font=("Arial", 12))
            self.entry_id_resp.grid(row=5, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_id_resp)
            ttk.Button(self.frame_responsaveis, text="Excluir Responsável", command=self.excluir_responsavel_gui).grid(row=6, column=0, columnspan=2, pady=10)
            self.atualizar_lista_responsaveis()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao configurar menu de Responsáveis: {e}")
    
        # Alunos
        try:
            self.frame_alunos.grid_columnconfigure(0, weight=1)
            self.frame_alunos.grid_columnconfigure(1, weight=1)
            tk.Label(self.frame_alunos, text="Nome:", font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky="e")
            self.entry_nome_aluno = tk.Entry(self.frame_alunos, font=("Arial", 12))
            self.entry_nome_aluno.grid(row=0, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_nome_aluno)
            tk.Label(self.frame_alunos, text="Idade:", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky="e")
            self.entry_idade_aluno = tk.Entry(self.frame_alunos, font=("Arial", 12))
            self.entry_idade_aluno.grid(row=1, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_idade_aluno)
            tk.Label(self.frame_alunos, text="Série:", font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky="e")
            self.entry_serie_aluno = tk.Entry(self.frame_alunos, font=("Arial", 12))
            self.entry_serie_aluno.grid(row=2, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_serie_aluno)
            tk.Label(self.frame_alunos, text="ID do Responsável:", font=("Arial", 12)).grid(row=3, column=0, pady=5, sticky="e")
            self.entry_responsavel_id_aluno = tk.Entry(self.frame_alunos, font=("Arial", 12))
            self.entry_responsavel_id_aluno.grid(row=3, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_responsavel_id_aluno)
            tk.Label(self.frame_alunos, text="ID da Escola:", font=("Arial", 12)).grid(row=4, column=0, pady=5, sticky="e")
            self.entry_escola_id_aluno = tk.Entry(self.frame_alunos, font=("Arial", 12))
            self.entry_escola_id_aluno.grid(row=4, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_escola_id_aluno)
            ttk.Button(self.frame_alunos, text="Cadastrar Aluno", command=self.cadastrar_aluno).grid(row=5, column=0, columnspan=2, pady=10)
            self.tree_alunos = ttk.Treeview(self.frame_alunos, columns=("ID", "Nome", "Idade", "Série", "Responsável", "Escola"), show="headings")
            for col in ("ID", "Nome", "Idade", "Série", "Responsável", "Escola"):
                self.tree_alunos.heading(col, text=col)
                self.tree_alunos.column(col, width=100, anchor="center")
            self.tree_alunos.grid(row=6, column=0, columnspan=2, pady=10)
            self.atualizar_lista_alunos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao configurar menu de Alunos: {e}")
    
        # Escolas
        try:
            self.frame_escolas.grid_columnconfigure(0, weight=1)
            self.frame_escolas.grid_columnconfigure(1, weight=1)
            tk.Label(self.frame_escolas, text="Nome:", font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky="e")
            self.entry_nome_escola = tk.Entry(self.frame_escolas, font=("Arial", 12))
            self.entry_nome_escola.grid(row=0, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_nome_escola)
            tk.Label(self.frame_escolas, text="Endereço:", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky="e")
            self.entry_endereco_escola = tk.Entry(self.frame_escolas, font=("Arial", 12))
            self.entry_endereco_escola.grid(row=1, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_endereco_escola)
            tk.Label(self.frame_escolas, text="Horário de Entrada:", font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky="e")
            self.entry_horario_entrada_escola = tk.Entry(self.frame_escolas, font=("Arial", 12))
            self.entry_horario_entrada_escola.grid(row=2, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_horario_entrada_escola)
            tk.Label(self.frame_escolas, text="Horário de Saída:", font=("Arial", 12)).grid(row=3, column=0, pady=5, sticky="e")
            self.entry_horario_saida_escola = tk.Entry(self.frame_escolas, font=("Arial", 12))
            self.entry_horario_saida_escola.grid(row=3, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_horario_saida_escola)
            ttk.Button(self.frame_escolas, text="Cadastrar Escola", command=self.cadastrar_escola).grid(row=4, column=0, columnspan=2, pady=10)
            self.tree_escolas = ttk.Treeview(self.frame_escolas, columns=("ID", "Nome", "Endereço", "Horário de Entrada", "Horário de Saída"), show="headings")
            for col in ("ID", "Nome", "Endereço", "Horário de Entrada", "Horário de Saída"):
                self.tree_escolas.heading(col, text=col)
                self.tree_escolas.column(col, width=100, anchor="center")
            self.tree_escolas.grid(row=5, column=0, columnspan=2, pady=10)
            self.atualizar_lista_escolas()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao configurar menu de Escolas: {e}")
    
    # ----- Aba Finanças (MySQL) ----------
    def criar_aba_financas(self):
        try:
            # Configuração do submenu Pagamentos
            self.frame_pagamentos.grid_columnconfigure(0, weight=1)
            self.frame_pagamentos.grid_columnconfigure(1, weight=1)
            tk.Label(self.frame_pagamentos, text="ID do Aluno:", font=("Arial", 12)).grid(row=0, column=0, pady=5, sticky="e")
            self.entry_id_aluno_pag = tk.Entry(self.frame_pagamentos, font=("Arial", 12))
            self.entry_id_aluno_pag.grid(row=0, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_id_aluno_pag)
            tk.Label(self.frame_pagamentos, text="Valor:", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky="e")
            self.entry_valor_pag = tk.Entry(self.frame_pagamentos, font=("Arial", 12))
            self.entry_valor_pag.grid(row=1, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_valor_pag)
            tk.Label(self.frame_pagamentos, text="Data de Vencimento (AAAA-MM-DD):", font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky="e")
            self.entry_data_pag = tk.Entry(self.frame_pagamentos, font=("Arial", 12))
            self.entry_data_pag.grid(row=2, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_data_pag)
            ttk.Button(self.frame_pagamentos, text="Registrar Pagamento", command=self.registrar_pagamento).grid(row=3, column=0, columnspan=2, pady=10)
            tk.Label(self.frame_pagamentos, text="ID do Pagamento:", font=("Arial", 12)).grid(row=4, column=0, pady=5, sticky="e")
            self.entry_id_pagamento = tk.Entry(self.frame_pagamentos, font=("Arial", 12))
            self.entry_id_pagamento.grid(row=4, column=1, pady=5, sticky="w")
            add_focus_binding(self.entry_id_pagamento)
            ttk.Button(self.frame_pagamentos, text="Marcar como Pago", command=self.marcar_como_pago).grid(row=5, column=0, columnspan=2, pady=10)
            self.tree_pendentes = ttk.Treeview(self.frame_pagamentos, columns=("ID", "Aluno", "Valor", "Vencimento"), show="headings")
            for col in ("ID", "Aluno", "Valor", "Vencimento"):
                self.tree_pendentes.heading(col, text=col)
                self.tree_pendentes.column(col, width=100, anchor="center")
            self.tree_pendentes.grid(row=6, column=0, columnspan=2, pady=10)
            self.atualizar_lista_pendentes()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao configurar menu de Pagamentos: {e}")
        
        try:
            # Configuração do submenu Relatórios
            ttk.Button(self.frame_relatorios, text="Gerar Gráfico de Pagamentos", command=self.gerar_relatorio_gui).pack(pady=10)
            self.tree_historico = ttk.Treeview(self.frame_relatorios, columns=("Aluno", "Valor", "Vencimento", "Data de Pagamento"), show="headings")
            for col in ("Aluno", "Valor", "Vencimento", "Data de Pagamento"):
                self.tree_historico.heading(col, text=col)
                self.tree_historico.column(col, width=120, anchor="center")
            self.tree_historico.pack(expand=True, fill="both", padx=10, pady=10)
            self.atualizar_historico()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao configurar menu de Relatórios: {e}")
    
    # ----- Funções de Cadastros (MySQL) -----
    def cadastrar_responsavel(self):
        nome = self.entry_nome_resp.get().strip()
        contato = self.entry_contato_resp.get().strip()
        endereco = self.entry_endereco_resp.get().strip()
        # Validação: campo 'nome' deve conter letras e não ser numérico
        if nome.isdigit():
            messagebox.showerror("Erro", "O campo 'Nome' deve conter apenas texto!")
            return
        if not (nome and contato and endereco):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        if not re.fullmatch(r"\(\d{2}\)9\d{8}", contato):
            messagebox.showerror("Erro", "Número de celular inválido. Insira no formato (XX)9XXXXXXXX.")
            return
        inserir_responsavel(self.conexao_mysql, nome, contato, endereco)
        self.atualizar_lista_responsaveis()
        
    def cadastrar_aluno(self):
        nome = self.entry_nome_aluno.get().strip()
        idade_str = self.entry_idade_aluno.get().strip()
        serie = self.entry_serie_aluno.get().strip()
        responsavel_id_str = self.entry_responsavel_id_aluno.get().strip()
        escola_id_str = self.entry_escola_id_aluno.get().strip()
        
        if not nome:
            messagebox.showerror("Erro", "O campo 'Nome' é obrigatório!")
            return
        if not re.fullmatch(r"[A-Za-zÀ-ÿ ]+", nome):
            messagebox.showerror("Erro", "Nome do aluno inválido. Utilize apenas letras e espaços.")
            return
        if nome.isdigit():
            messagebox.showerror("Erro", "O campo 'Nome' deve conter apenas texto!")
            return
        if not idade_str:
            messagebox.showerror("Erro", "O campo 'Idade' é obrigatório!")
            return
        if not idade_str.isdigit():
            messagebox.showerror("Erro", "O campo 'Idade' deve ser um número inteiro!")
            return
        if not serie:
            messagebox.showerror("Erro", "O campo 'Série' é obrigatório!")
            return
        if not responsavel_id_str:
            messagebox.showerror("Erro", "O campo 'ID do Responsável' é obrigatório!")
            return
        if not responsavel_id_str.isdigit():
            messagebox.showerror("Erro", "O campo 'ID do Responsável' deve ser um número inteiro!")
            return
        if not escola_id_str:
            messagebox.showerror("Erro", "O campo 'ID da Escola' é obrigatório!")
            return
        if not escola_id_str.isdigit():
            messagebox.showerror("Erro", "O campo 'ID da Escola' deve ser um número inteiro!")
            return
        try:
            idade = int(idade_str)
            responsavel_id = int(responsavel_id_str)
            escola_id = int(escola_id_str)
        except Exception:
            messagebox.showerror("Erro", "Erro na conversão dos campos numéricos!")
            return
        inserir_aluno_mysql(self.conexao_mysql, nome, idade, serie, responsavel_id, escola_id)
        self.atualizar_lista_alunos()
        
    def cadastrar_escola(self):
        nome = self.entry_nome_escola.get().strip()
        endereco = self.entry_endereco_escola.get().strip()
        horario_entrada = self.entry_horario_entrada_escola.get().strip()
        horario_saida = self.entry_horario_saida_escola.get().strip()
        if not nome:
            messagebox.showerror("Erro", "O campo 'Nome' é obrigatório!")
            return
        if nome.isdigit() or not any(c.isalpha() for c in nome):
            messagebox.showerror("Erro", "O campo 'Nome' deve conter texto!")
            return
        if not endereco:
            messagebox.showerror("Erro", "O campo 'Endereço' é obrigatório!")
            return
        if not horario_entrada:
            messagebox.showerror("Erro", "O campo 'Horário de Entrada' é obrigatório!")
            return
        if not horario_saida:
            messagebox.showerror("Erro", "O campo 'Horário de Saída' é obrigatório!")
            return
        inserir_escola(self.conexao_mysql, nome, endereco, horario_entrada, horario_saida)
        self.atualizar_lista_escolas()
    
    def listar_responsaveis_gui(self):
        self.atualizar_lista_responsaveis()
    
    def atualizar_lista_responsaveis(self):
        for item in self.tree_responsaveis.get_children():
            self.tree_responsaveis.delete(item)
        responsaveis = listar_responsaveis(self.conexao_mysql)
        for r in responsaveis:
            self.tree_responsaveis.insert("", "end", values=r)
    
    def excluir_responsavel_gui(self):
        try:
            id_resp = self.entry_id_resp.get()
            if not id_resp.isdigit():
                messagebox.showerror("Erro", "Digite um ID válido!")
                return
            excluir_responsavel(self.conexao_mysql, int(id_resp))
            self.atualizar_lista_responsaveis()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir responsável: {e}")
    
    def listar_alunos_gui(self):
        self.atualizar_lista_alunos()
    
    def atualizar_lista_alunos(self):
        for item in self.tree_alunos.get_children():
            self.tree_alunos.delete(item)
        alunos = listar_alunos_mysql(self.conexao_mysql)
        for a in alunos:
            self.tree_alunos.insert("", "end", values=a)
    
    def listar_escolas_gui(self):
        self.atualizar_lista_escolas()
    
    def atualizar_lista_escolas(self):
        for item in self.tree_escolas.get_children():
            self.tree_escolas.delete(item)
        escolas = listar_escolas(self.conexao_mysql)
        for e in escolas:
            self.tree_escolas.insert("", "end", values=e)
    
    # ----- Funções de Finanças (MySQL) --------
    def registrar_pagamento(self):
        id_aluno = self.entry_id_aluno_pag.get()
        valor = self.entry_valor_pag.get()
        data_vencimento = self.entry_data_pag.get()
        if not (id_aluno and valor and data_vencimento):
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        try:
            id_aluno = int(id_aluno)
            valor = float(valor)
        except ValueError:
            messagebox.showerror("Erro", "ID e Valor devem ser numéricos!")
            return
        registrar_pagamento_mysql(self.conexao_mysql, id_aluno, valor, data_vencimento)
        self.atualizar_lista_pendentes()
    
    def marcar_como_pago(self):
        id_pagamento = self.entry_id_pagamento.get()
        if not id_pagamento.isdigit():
            messagebox.showerror("Erro", "Digite um ID válido!")
            return
        atualizar_status_pagamento_mysql(self.conexao_mysql, int(id_pagamento))
        self.atualizar_lista_pendentes()
        self.atualizar_historico()
    
    def atualizar_lista_pendentes(self):
        if self.conexao_mysql is None:
            messagebox.showerror("Erro", "Conexão com o banco de dados não estabelecida.")
            return
        for item in self.tree_pendentes.get_children():
            self.tree_pendentes.delete(item)
        pendentes = obter_pagamento_pendentes_mysql(self.conexao_mysql)
        for p in pendentes:
            self.tree_pendentes.insert("", "end", values=p)
    
    def atualizar_historico(self):
        if self.conexao_mysql is None:
            messagebox.showerror("Erro", "Conexão com o banco de dados não estabelecida.")
            return
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        historico = obter_historico_completo_mysql(self.conexao_mysql)
        for h in historico:
            self.tree_historico.insert("", "end", values=h)
    
    def gerar_relatorio_gui(self):
        if self.conexao_mysql is None:
            messagebox.showerror("Erro", "Conexão com o banco de dados não estabelecida.")
            return
        dados = gerar_relatorio_pagamentos_mysql(self.conexao_mysql)
        if sum(dados) == 0:
            messagebox.showinfo("Info", "Não há dados suficientes para gerar o gráfico.")
            return
        labels = ["Pendentes", "Pagos"]
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        ax.clear()
        ax.pie(dados, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        if hasattr(self, "graph_frame"):
            self.graph_frame.destroy()
        self.graph_frame = ttk.Frame(self.frame_relatorios)
        self.graph_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        if hasattr(self, "toolbar"):
            self.toolbar.destroy()
        self.toolbar = NavigationToolbar2Tk(self.graph_canvas, self.graph_frame)
        self.toolbar.update()

if __name__ == "__main__":
    app = UnifiedApplication()
    app.mainloop()