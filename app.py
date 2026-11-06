from flask import Flask, render_template, request, redirect, url_for, flash, g
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from banco import tabela_time, tabela_jogador, tabela_partida, tabela_movimentacao
from database import *
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

app = Flask(__name__)
# secret_key aqui apenas em momento de criação, em produção deve ser protegida!
app.secret_key = "chave-secreta-interclasse-2026"

# Configuração do Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Faça login para acessar"

# Prevenir gargalo "too many connections"
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Carregar informações do usuário logado
@login_manager.user_loader
def load_user(user_id):
    return db_session.get(Usuario, int(user_id))

# Interface de autenticação
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")


        usuario_sql = select(Usuario).where(Usuario.email == email)
        usuario_resultado = db_session.execute(usuario_sql).scalar() # usuario_resultado representa a class Usuario

        if not usuario_resultado:
            flash("Falha na autenticação: E-mail não encontrado", "error")
            return redirect(url_for("login"))
        if usuario_resultado and usuario_resultado.check_password(senha):
            login_user(usuario_resultado)
            return redirect(url_for("dashboard"))
        else:
            flash("Falha na autenticação: Senha incorreta", "error")

@app.route("/")
def dashboard():
    # Buscar todos os times no banco (Select)
    times = tabela_time.select_quantidade_total()

    # Buscar todos os jogadores no banco (Select)
    jogadores = tabela_jogador.select_quantidade_total()

    # Buscar todos as partidas no banco (Select)
    partidas = tabela_partida.select_quantidade_total()

    # Buscar todos as movimentações no banco (Select)
    movimentacoes = tabela_movimentacao.select_quantidade_total()

    return render_template(
        "dashboard.html",
        total_jogadores=jogadores,
        total_times=times,
        total_partidas=partidas,
        total_movimentacoes=movimentacoes
    )


@app.route("/jogadores")
def listar_jogadores():
    # Buscar todos os jogadores no banco (Select)
    jogadores = tabela_jogador.select_todos_jogadores()
    return render_template("jogadores.html", jogadores=jogadores, times=[])


@app.route("/jogadores/novo", methods=["GET", "POST"])
def novo_jogador():

    if request.method == "POST":
        # 1- Pegar os valores digitados no form
        nome = request.form.get("nome").strip()
        numero_camisa = request.form.get("numero_camisa") or None
        posicao = request.form.get("posicao").strip()
        time_id = request.form.get("time_id") or None

        # 2- Verificar se foi digitado
        if not nome:
            flash("Preencha o nome do jogador", "error")
            return redirect(url_for("novo_jogador"))
        if not numero_camisa:
            flash("Preencha o número da camisa do jogador", "error")
            return redirect(url_for("novo_jogador"))
        if not posicao:
            flash("Preencha a posição do jogador", "error")
            return redirect(url_for("novo_jogador"))
        if not time_id:
            flash("Preencha o time do jogador", "error")
            return redirect(url_for("novo_jogador"))

        # 3- Salvar no banco
        tabela_jogador.salvar(nome, numero_camisa, posicao, time_id)

    # Buscar todos os times no banco (Select)
    times = tabela_time.select_todos_times()

    # Buscar todos os jogadores no banco (Select)
    jogadores = tabela_jogador.select_todos_jogadores()

    # Carregar o Formulário
    return render_template("jogadores.html", jogadores=jogadores, times=times)

@app.route("/jogadores/<id_jogador>", methods=["GET", "POST"])
def editar_jogador(id_jogador):
    # Buscar o jogador no Banco
    jogador = tabela_jogador.select_um(id_jogador)

    # Salvar as alterações
    if request.method == "POST":
        # 1- Pegar os valores digitados no form
        nome = request.form.get("nome").strip()
        numero_camisa = request.form.get("numero_camisa") or None
        posicao = request.form.get("posicao").strip()
        time_id = request.form.get("time_id") or None

        # 2- Verificar se foi digitado
        if not nome:
            flash("Preencha o nome do jogador", "error")
        elif not numero_camisa:
            flash("Preencha o número da camisa do jogador", "error")
        elif not posicao:
            flash("Preencha a posição do jogador", "error")
        elif not time_id:
            flash("Preencha o time do jogador", "error")
        else:
            jogador.nome = nome
            jogador.numero_camisa = numero_camisa
            jogador.posicao = posicao
            jogador.time_id = int(time_id)
            db_session.commit()

            flash("Jogador alterado com sucesso", "success")

        return redirect(url_for("listar_jogadores"))

    # Carregar as informações
    jogadores = tabela_jogador.select_todos_jogadores()
    times = tabela_time.select_todos_times()
    return render_template("jogadores.html", jogadores=jogadores, editar=jogador, times=times)

@app.route("/times")
def listar_times():
    # Buscar todos os times no banco (Select)
    times = tabela_time.select_todos_times()
    return render_template("times.html", times=times)

@app.route("/times/novo", methods=["GET", "POST"])
def novo_time():

    if request.method == "POST":
        # 1- Pegar os valores digitados no form
        nome = request.form.get("nome")
        turma = request.form.get("turma")
        responsavel = request.form.get("responsavel")
        jogadores_ids = request.form.getlist("jogadores")

        # 2- Verificar se foi digitado
        if not nome:
            flash("Preencha o nome do time", "error")
            return redirect(url_for("novo_time"))
        if not turma:
            flash("Preencha a turma do time", "error")
            return redirect(url_for("novo_time"))
        if not responsavel:
            flash("Preencha o nome do responsável do time ", "error")
            return redirect(url_for("novo_time"))

        # 3- Salvar no banco
        time = tabela_time.salvar(nome=nome, turma=turma, responsavel=responsavel)

        if jogadores_ids:
            for jogador_id in jogadores_ids:
                jogador = tabela_jogador.select_um(jogador_id)
                jogador.time_id = time.id
                db_session.add(jogador)
                db_session.commit()


    # Buscar todos os times no banco (Select)
    times = tabela_time.select_todos_times()
    jogadores = tabela_jogador.select_todos_jogadores()
    return render_template("times.html", times=times, jogadores=jogadores)

@app.route("/time/<id_time>")
def detalhes_time(id_time):
    time = tabela_time.select_um(int(id_time))
    jogadores = tabela_jogador.select_jogadores_por_time(int(id_time)) # Fazer uma função que traga todos os jogadores do time
    partidas = tabela_partida.select_partidas_por_time(int(id_time))
    return render_template("time_detalhes.html", time=time, jogadores=jogadores, qntd_jogadores=len(jogadores), partidas=partidas, qntd_partidas=len(partidas))

@app.route("/partidas")
def listar_partidas():
    # Buscar todos as partidas no banco (Select)
    partidas = tabela_partida.select_todas_partidas()
    return render_template("partidas.html", partidas=partidas)

@app.route("/partidas/nova", methods=["GET", "POST"])
def nova_partida():

    if request.method == "POST":
        # 1- Pegar os campos do formulário
        time_casa_id = request.form.get("time_casa_id")
        time_visitante_id = request.form.get("time_visitante_id")
        gols_casa = request.form.get("gols_casa") or 0
        gols_visitante = request.form.get("gols_visitante") or 0
        data_partida = request.form.get("data_partida", "").strip()
        print(data_partida)
        #date_partida = datetime.strptime(data_partida, "%Y-%m-%d").date()

        # 2- Verificar se foi digitado
        if not time_casa_id:
            flash("Preencha o time da casa de partida", "error")
            return redirect(url_for("nova_partida"))
        if not time_visitante_id:
            flash("Preencha o campo", "error")
            return redirect(url_for("nova_partida"))
        if not gols_casa:
            flash("Preencha a quantidade de gols do time da casa", "error")
            return redirect(url_for("nova_partida"))
        if not gols_visitante:
            flash("Preencha a quantidade de gols do time visitante", "error")
            return redirect(url_for("nova_partida"))
        if not data_partida:
            flash("Preencha a data da partida", "error")
            return redirect(url_for("nova_partida"))

        # 3- Verificar se os times são iguais
        if time_visitante_id == time_casa_id:
            flash("Selecione times diferentes", "error")
            return render_template("partidas.html")

        # 4- Salvar no banco
        tabela_partida.salvar(time_casa_id, time_visitante_id, gols_casa, gols_visitante, data_partida)

    # Buscar todos os times no banco (Select)
    times = tabela_time.select_todos_times()

    # Buscar todos as partidas no banco (Select)
    partidas = tabela_partida.select_todas_partidas()
    return render_template("partidas.html", partidas=partidas, times=times)

@app.route("/movimentacao/nova/id<int:id_jogador>")
@app.route("/movimentacao/nova", methods=["GET", "POST"])
def nova_movimentacao(id_jogador=None):
    if request.method == "POST":
        # 1- Pegar informações do Formulário (POST)
        jogador_id = request.form.get("jogador_id")
        time_destino_id = request.form.get("time_destino_id")

        # 2- Verificar informações selecionadas
        if not jogador_id:
            flash("Selecione o jogador", "error")
            return redirect(url_for("nova_movimentacao"))
        if not time_destino_id:
            flash("Selecione o time de destino", "error")
            return redirect(url_for("nova_movimentacao"))

        # 3- Salvar no banco
        tabela_movimentacao.salvar(jogador_id, time_destino_id)
        return redirect(url_for("nova_movimentacao"))
    # Carregar dados para movimentação
    movimentacoes = tabela_movimentacao.select_todos()
    jogadores = tabela_jogador.select_todos_jogadores()
    times = tabela_time.select_todos_times()

    return render_template(
        "movimentacoes.html",
        movimentacoes=movimentacoes,
        jogadores=jogadores,
        times=times,
        jogador_selecionado_id=id_jogador
    )

if __name__ == "__main__":
    app.run(debug=True)