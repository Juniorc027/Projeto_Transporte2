import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime
import re

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))
app.secret_key = 'sua_chave_secreta'

# Função para conectar ao banco de dados
def conectar_banco():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="projeto_transporte"
        )
        return conexao
    except mysql.connector.Error as err:
        print("Erro ao conectar:", err)
        return None

# Rota inicial
@app.route("/")
def index():
    return render_template("index (1).html")

# Rota para cadastrar responsável
@app.route("/cadastrar_responsavel", methods=["GET", "POST"])
def cadastrar_responsavel():
    if request.method == "POST":
        nome = request.form.get("nome")
        if len(nome) > 64:
            flash("Nome do responsável deve ter até 64 caracteres.", "danger")
            return redirect(url_for("cadastrar_responsavel"))
        contato = request.form.get("contato")
        endereco = request.form.get("endereco")
        
        # Validações aprimoradas:
        if not re.fullmatch(r"[A-Za-zÀ-ÿ ]+", nome):
            flash("Nome inválido. Insira apenas letras e espaços.", "danger")
            return redirect(url_for("cadastrar_responsavel"))
        if not re.fullmatch(r"\(\d{2}\)9\d{8}", contato):
            flash("Contato inválido. Use o formato (XX)9XXXXXXXX.", "danger")
            return redirect(url_for("cadastrar_responsavel"))
        if not re.fullmatch(r"[A-Za-zÀ-ÿ\d\s,.-]+", endereco):
            flash("Endereço inválido. Insira um endereço correto.", "danger")
            return redirect(url_for("cadastrar_responsavel"))
        
        conexao = conectar_banco()
        if conexao is None:
            flash("Erro na conexão com o banco de dados.", "danger")
            return redirect(url_for("cadastrar_responsavel"))
        cursor = conexao.cursor()
        try:
            query_check = "SELECT id FROM responsaveis WHERE nome = %s AND contato = %s AND endereco = %s"
            cursor.execute(query_check, (nome, contato, endereco))
            if cursor.fetchone():
                flash("Responsável já cadastrado com o mesmo nome, contato e endereço.", "danger")
                return redirect(url_for("cadastrar_responsavel"))
            
            query = "INSERT INTO responsaveis (nome, contato, endereco) VALUES (%s, %s, %s)"
            cursor.execute(query, (nome, contato, endereco))
            conexao.commit()
            flash("Responsável cadastrado com sucesso!", "success")
        except mysql.connector.Error as err:
            flash(f"Erro ao inserir responsável: {err}", "danger")
        finally:
            cursor.close()
            conexao.close()
        return redirect(url_for("listar_responsaveis"))
    return render_template("cadastrar_responsavel.html")

# Rota para listar responsáveis
@app.route("/listar_responsaveis")
def listar_responsaveis():
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro na conexão com o banco de dados.", "danger")
        return redirect(url_for("index"))
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT * FROM responsaveis")
        responsaveis = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Erro ao listar responsáveis: {err}", "danger")
        responsaveis = []
    finally:
        cursor.close()
        conexao.close()
    return render_template("listar_responsaveis.html", pendentes=responsaveis)

# Rota para cadastrar aluno
@app.route("/cadastrar_aluno", methods=["GET", "POST"])
def cadastrar_aluno():
    # Carrega dados para os selects
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro na conexão com o banco de dados.", "danger")
        return redirect(url_for("index"))
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id, nome FROM responsaveis")
        responsaveis = cursor.fetchall()
        cursor.execute("SELECT id, nome FROM escolas")
        escolas = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Erro ao carregar dados: {err}", "danger")
        responsaveis = []
        escolas = []
    finally:
        cursor.close()
        conexao.close()
    
    if request.method == "POST":
        nome = request.form.get("nome")
        if len(nome) > 64:
            flash("Nome do aluno deve ter até 64 caracteres.", "danger")
            return redirect(url_for("cadastrar_aluno"))
        idade = request.form.get("idade")
        serie = request.form.get("serie")
        responsavel_id = request.form.get("responsavel_id")
        escola_id = request.form.get("escola_id")
        
        if not re.fullmatch(r"[A-Za-zÀ-ÿ ]+", nome):
            flash("Nome inválido. Insira apenas letras e espaços.", "danger")
            return redirect(url_for("cadastrar_aluno"))
        if not idade.isdigit() or not (3 <= int(idade) <= 18):
            flash("Idade inválida. Deve estar entre 3 e 18 anos.", "danger")
            return redirect(url_for("cadastrar_aluno"))
        if not re.fullmatch(r"[A-Za-zÀ-ÿ\d\s.-]+", serie):
            flash("Série inválida.", "danger")
            return redirect(url_for("cadastrar_aluno"))
        
        conexao = conectar_banco()
        if conexao is None:
            flash("Erro na conexão com o banco de dados.", "danger")
            return redirect(url_for("cadastrar_aluno"))
        cursor = conexao.cursor()
        try:
            query = "INSERT INTO alunos (nome, idade, serie, responsavel_id, escola_id) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (nome, idade, serie, responsavel_id, escola_id))
            conexao.commit()
            flash("Aluno cadastrado com sucesso!", "success")
        except mysql.connector.Error as err:
            flash(f"Erro ao inserir aluno: {err}", "danger")
        finally:
            cursor.close()
            conexao.close()
        return redirect(url_for("listar_alunos"))
    return render_template("cadastrar_aluno.html", responsaveis=responsaveis, escolas=escolas)

# Rota para listar alunos
@app.route("/listar_alunos")
def listar_alunos():
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro na conexão com o banco de dados.", "danger")
        return redirect(url_for("index"))
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
    except mysql.connector.Error as err:
        flash(f"Erro ao listar alunos: {err}", "danger")
        alunos = []
    finally:
        cursor.close()
        conexao.close()
    return render_template("listar_alunos.html", alunos=alunos)

# Rota para deletar aluno
@app.route("/deletar_aluno/<nome>", methods=["POST"])
def deletar_aluno(nome):
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro na conexão com o banco de dados.", "danger")
        return redirect(url_for("listar_alunos"))
    cursor = conexao.cursor()
    try:
        query = "DELETE FROM alunos WHERE nome = %s"
        cursor.execute(query, (nome,))
        conexao.commit()
        flash("Aluno excluído com sucesso!", "success")
    except mysql.connector.Error as err:
        flash(f"Erro ao excluir aluno: {err}", "danger")
    finally:
        cursor.close()
        conexao.close()
    return redirect(url_for("listar_alunos"))

# Rota para cadastrar escola
@app.route("/cadastrar_escola", methods=["GET", "POST"])
def cadastrar_escola():
    if request.method == "POST":
        nome = request.form.get("nome")
        endereco = request.form.get("endereco")
        horario_entrada = request.form.get("horario_entrada")
        horario_saida = request.form.get("horario_saida")
        
        if not re.fullmatch(r"[A-Za-zÀ-ÿ\d\s,.-]+", nome):
            flash("Nome da escola inválido.", "danger")
            return redirect(url_for("cadastrar_escola"))
        if not re.fullmatch(r"[A-Za-zÀ-ÿ\d\s,.-]+", endereco):
            flash("Endereço inválido.", "danger")
            return redirect(url_for("cadastrar_escola"))
        if horario_entrada == horario_saida:
            flash("Horário de entrada e saída não podem ser iguais.", "danger")
            return redirect(url_for("cadastrar_escola"))
            
        conexao = conectar_banco()
        if conexao is None:
            flash("Erro na conexão com o banco de dados.", "danger")
            return redirect(url_for("cadastrar_escola"))
        cursor = conexao.cursor()
        try:
            query = "INSERT INTO escolas (nome, endereco, horario_entrada, horario_saida) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (nome, endereco, horario_entrada, horario_saida))
            conexao.commit()
            flash("Escola cadastrada com sucesso!", "success")
        except mysql.connector.Error as err:
            flash(f"Erro ao cadastrar escola: {err}", "danger")
        finally:
            cursor.close()
            conexao.close()
        return redirect(url_for("listar_escolas"))
    return render_template("cadastrar_escola.html")

# Rota para listar escolas
@app.route("/listar_escolas")
def listar_escolas():
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro na conexão com o banco de dados.", "danger")
        return redirect(url_for("index"))
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT * FROM escolas")
        escolas = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Erro ao listar escolas: {err}", "danger")
        escolas = []
    finally:
        cursor.close()
        conexao.close()
    return render_template("listar_escolas.html", escolas=escolas)

# Rota para registrar pagamento
@app.route("/registrar_pagamento", methods=["GET", "POST"])
def registrar_pagamento():
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro na conexão com o banco de dados.", "danger")
        return redirect(url_for("index"))
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id, nome FROM alunos")
        alunos = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Erro ao obter alunos: {err}", "danger")
        alunos = []
    finally:
        cursor.close()
        conexao.close()
    if request.method == "POST":
        aluno_id = request.form.get("aluno_id")
        valor = request.form.get("valor")
        data_vencimento = request.form.get("data_vencimento")
        try:
            valor_float = float(valor)
            if valor_float <= 0:
                flash("O valor do pagamento deve ser maior que zero.", "danger")
                return redirect(url_for("registrar_pagamento"))
        except ValueError:
            flash("Valor inválido.", "danger")
            return redirect(url_for("registrar_pagamento"))
        conexao = conectar_banco()
        if conexao is None:
            flash("Erro na conexão com o banco de dados.", "danger")
            return redirect(url_for("registrar_pagamento"))
        cursor = conexao.cursor()
        try:
            query = "INSERT INTO pagamentos (aluno_id, valor, data, status) VALUES (%s, %s, %s, 'pendente')"
            cursor.execute(query, (aluno_id, valor_float, data_vencimento))
            conexao.commit()
            flash("Pagamento registrado com sucesso!", "success")
        except mysql.connector.Error as err:
            flash(f"Erro ao registrar pagamento: {err}", "danger")
        finally:
            cursor.close()
            conexao.close()
        return redirect(url_for("registrar_pagamento"))
    return render_template("registrar_pagamento.html", alunos=alunos)

# Rota para marcar pagamento como pago
@app.route("/marcar_pago", methods=["GET", "POST"])
def marcar_pago():
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro na conexão com o banco de dados.", "danger")
        return redirect(url_for("index"))
    cursor = conexao.cursor()
    try:
        query = "SELECT pagamentos.id, alunos.nome, pagamentos.valor, pagamentos.data FROM pagamentos LEFT JOIN alunos ON pagamentos.aluno_id = alunos.id WHERE pagamentos.status = 'pendente'"
        cursor.execute(query)
        pendentes = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Erro ao obter pagamentos pendentes: {err}", "danger")
        pendentes = []
    finally:
        cursor.close()
        conexao.close()
    if request.method == "POST":
        pagamento_id = request.form.get("pagamento_id")
        conexao = conectar_banco()
        if conexao is None:
            flash("Erro na conexão com o banco de dados.", "danger")
            return redirect(url_for("marcar_pago"))
        cursor = conexao.cursor()
        try:
            cursor.execute("UPDATE pagamentos SET status = 'pago' WHERE id = %s", (pagamento_id,))
            conexao.commit()
            flash("Pagamento marcado como pago!", "success")
        except mysql.connector.Error as err:
            flash(f"Erro ao marcar pagamento como pago: {err}", "danger")
        finally:
            cursor.close()
            conexao.close()
        return redirect(url_for("marcar_pago"))
    return render_template("marcar_pago.html", pendentes=pendentes)

# Rota para relatório de pagamentos
@app.route("/relatorio")
def relatorio():
    conexao = conectar_banco()
    if conexao is None:
        flash("Erro na conexão com o banco de dados.", "danger")
        return redirect(url_for("index"))
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT pagamentos.id, alunos.nome, pagamentos.valor, pagamentos.data FROM pagamentos LEFT JOIN alunos ON pagamentos.aluno_id = alunos.id WHERE pagamentos.status = 'pago'")
        pagos = cursor.fetchall()
        cursor.execute("SELECT pagamentos.id, alunos.nome, pagamentos.valor, pagamentos.data FROM pagamentos LEFT JOIN alunos ON pagamentos.aluno_id = alunos.id WHERE pagamentos.status = 'pendente'")
        pendentes = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Erro ao obter dados do relatório: {err}", "danger")
        pagos = []
        pendentes = []
    finally:
        cursor.close()
        conexao.close()
    return render_template("relatorio.html", pagos=pagos, pendentes=pendentes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)