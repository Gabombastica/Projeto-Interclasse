from flask import flash
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database import Time, db_session

def select_todos_times():
    # Buscar todos os times no banco
    # 1- Montar o select
    times_sql = select(Time)
    # 2- Executar o select
    times = db_session.execute(times_sql).scalars().all()
    return times

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

