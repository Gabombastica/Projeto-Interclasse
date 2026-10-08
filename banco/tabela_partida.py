from flask import flash
from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased
from sqlalchemy.sql.elements import or_

from database import db_session, Partida, Time

def select_todas_partidas():
    # Buscar todos os times no banco
    # 1- Montar o select

    TimeCasa = aliased(Time)
    TimeVisitante = aliased(Time)

    partidas_sql = (
        select(Partida, TimeCasa, TimeVisitante)
        .join(TimeCasa, Partida.time_casa_id == TimeCasa.id)
        .join(TimeVisitante, Partida.time_visitante_id == TimeVisitante.id)
    )
    # 2- Executar o select
    partidas_casa = db_session.execute(partidas_sql).all()
    return partidas_casa

def select_quantidade_total():
    partidas_sql = select(func.count(Partida.id))
    qntd_total = db_session.execute(partidas_sql).scalar()
    return qntd_total

print(select_quantidade_total())

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
