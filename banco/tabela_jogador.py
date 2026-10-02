from flask import flash
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database import Jogador, db_session

def select_todos_jogadores():
    # Buscar todos os times no banco
    # 1- Montar o select
    jogadores_sql = select(Jogador)
    # 2- Executar o select
    jogadores = db_session.execute(jogadores_sql).scalars().all()
    return jogadores

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