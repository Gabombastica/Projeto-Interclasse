from flask import flash
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError

from database import Time, db_session, Jogador


def select_todos_times():
    # Buscar todos os times no banco
    # 1- Montar o select
    times_sql = (
        select(Time, func.count(Jogador.id).label("jogadores"))
        .outerjoin(Jogador, Jogador.time_id == Time.id)
        .group_by(Time.id)
    )
    # 2- Executar o select
    times = db_session.execute(times_sql).all()
    return times

def select_quantidade_total():
    times_sql = select(func.count(Time.id))
    qntd_total = db_session.execute(times_sql).scalar()
    return qntd_total

print(select_quantidade_total())

def salvar(nome, turma, responsavel):
    # 3- Salvar no banco
    try:
        novo_time = Time(nome=nome, turma=turma, responsavel=responsavel)
        db_session.add(novo_time)
        db_session.commit()
        flash("Time criado com sucesso", "success")
    except SQLAlchemyError as e:
        db_session.rollback()
        flash("Ocorreu um erro, tente novamente", "error")
        print(f"{e}")
    except Exception as e:
        db_session.rollback()
        flash("Ocorreu um erro, tente novamente", "error")
        print(f"Erro: {e}")

