import os
import sys
import tempfile
import pytest
from codex import database
from sqlalchemy.orm import sessionmaker

def setup_temp_db():
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    database.engine = database.create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
    database.Session = sessionmaker(bind=database.engine)
    database.criar_banco_e_tabelas()
    return db_path

def teardown_temp_db(db_path):
    os.remove(db_path)

def test_gerar_relatorio_uso():
    db_path = setup_temp_db()
    session = database.Session()
    session.add(database.Conversa(role='user', content='Primeira pergunta'))
    session.add(database.Conversa(role='model', content='Primeira resposta'))
    session.add(database.Conversa(role='user', content='Segunda pergunta'))
    session.commit()
    relatorio = database.gerar_relatorio_uso(session, n_mensagens=10)
    assert 'Perguntas mais frequentes' in relatorio
    assert 'Total de interações' in relatorio
    teardown_temp_db(db_path)

def test_exportar_historico_jsonl():
    db_path = setup_temp_db()
    session = database.Session()
    session.add(database.Conversa(role='user', content='Exportar teste'))
    session.add(database.Conversa(role='model', content='Resposta exportada'))
    session.commit()
    resultado = database.exportar_historico_jsonl(session)
    assert 'Exportação concluída' in resultado
    assert os.path.exists('historico_codex.jsonl')
    with open('historico_codex.jsonl', 'r', encoding='utf-8') as f:
        linhas = f.readlines()
        print('DEBUG linhas exportadas:', linhas)
        assert any('Exportar teste' in linha or 'exportar teste' in linha.lower() for linha in linhas)
    os.remove('historico_codex.jsonl')
    teardown_temp_db(db_path)

def test_perfil_usuario():
    db_path = setup_temp_db()
    session = database.Session()
    session.add(database.Conversa(role='user', content='Python pytest'))
    session.add(database.Conversa(role='user', content='Python cobertura'))
    session.commit()
    perfil = database.perfil_usuario(session)
    assert 'temas_mais_frequentes' in perfil
    assert 'horarios_mais_ativos' in perfil
    assert perfil['total_perguntas'] == 2
    teardown_temp_db(db_path)
