from flask import flash
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from database import Jogador, db_session, Time


def select_todos_jogadores():
    # Buscar todos os times no banco
    # 1- Montar o select
    # join(Tabela que eu quero juntar, condição = Chave estrangeira == Chave primária)
    jogadores_sql = select(Jogador, Time).join(Time, Jogador.time_id == Time.id)
    # 2- Executar o select
    # Usar scalars quando tiver somente uma tabela
    # Usar all quando tem mais de uma tabela
    jogadores = db_session.execute(jogadores_sql).all()
    return jogadores


def select_quantidade_total():
    jogadores_sql = select(func.count(Jogador.id))
    qntd_total = db_session.execute(jogadores_sql).scalar()
    return qntd_total

print(select_quantidade_total())


def salvar(nome, numero_camisa, posicao, time_id):
    # 3- Salvar no banco
    try:
        novo_jogador = Jogador(nome=nome, numero_camisa=int(numero_camisa), posicao=posicao, time_id=int(time_id))
        db_session.add(novo_jogador)
        db_session.commit()
        flash("Jogador criado com sucesso", "success")
    except SQLAlchemyError as e:
        db_session.rollback()
        flash("Ocorreu um erro, tente novamente!", "error")
        print(f"{e}")
    except Exception as e:
        db_session.rollback()
        flash("Ocorreu um erro, tente novamente", "error")
        print(f"Erro: {e}")


def select_um(id_jogador):
    jogador_sql = select(Jogador).where(Jogador.id == id_jogador)
    jogador = db_session.execute(jogador_sql).scalar_one_or_none()
    return jogador

#print(select_um(5))

def select_jogadores_por_time(id_time):
    # Trazer jogadores de um time
    jogadores_sql = select(Jogador).where(Jogador.time_id == id_time)
    jogadores = db_session.execute(jogadores_sql).scalars().all()
    return jogadores

print(select_jogadores_por_time(1))

