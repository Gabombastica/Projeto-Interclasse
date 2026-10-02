from flask import flash
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database import Partida, db_session

def select_todas_partidas():
    # Buscar todos os times no banco
    # 1- Montar o select
    partidas_sql = select(Partida)
    # 2- Executar o select
    partidas = db_session.execute(partidas_sql).scalars().all()
    return partidas

def salvar(time_casa_id, time_visitante_id, gols_casa, gols_visitante, data_partida):
    # 3- Salvar no banco
    try:
        nova_partida = Partida(time_casa_id=int(time_casa_id), time_visitante_id=int(time_visitante_id), gols_casa=int(gols_casa), gols_visitante=int(gols_visitante), data_partida=data_partida)
        db_session.add(nova_partida)
        db_session.commit()
        flash("Partida criada com sucesso", "success")
    except SQLAlchemyError as e:
        db_session.rollback()
        flash("Ocorreu um erro, tente novamente", "error")
        print(f"{e}")
    except Exception as e:
        db_session.rollback()
        flash("Ocorreu um erro, tente novamente", "error")
        print(f"Erro: {e}")
