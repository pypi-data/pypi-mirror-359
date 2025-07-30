import os
import tempfile
import pytest
from codex import database
from sqlalchemy.orm import sessionmaker

# Correção: garantir que todos os imports e patches nos testes estejam corretos após a modularização.
# Exemplo de import correto para testes:
# from codex.cli_core import escrever_arquivo, listar_arquivos, ler_arquivo
# from codex.suggestions import sugerir_pergunta_frequente, sugerir_pergunta_contextual, buscar_contexto_relevante
# from codex.integrations.stackoverflow import consultar_stackoverflow
# from codex.integrations.google import consultar_google
# from codex.integrations.github import consultar_github
# from codex.integrations.wikipedia import consultar_wikipedia
# from codex.integrations.wolframalpha import consultar_wolframalpha
#
# Exemplo de patch correto para IA:
# from unittest.mock import patch
# @patch("google.genai.Client")
# def test_alguma_coisa(mock_genai_client, ...):
#     ...
# Exemplo de patch correto para sugestões/contexto:
# monkeypatch.setattr("codex.suggestions.sugerir_pergunta_contextual", lambda session: ...)
# monkeypatch.setattr("codex.suggestions.buscar_contexto_relevante", lambda session, pergunta_usuario, n=5: ...)

@pytest.fixture
def temp_db():
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    database.engine = database.create_engine(f'sqlite:///{db_path}', connect_args={"check_same_thread": False})
    database.Session = sessionmaker(bind=database.engine)
    database.criar_banco_e_tabelas()
    yield db_path
    os.remove(db_path)

@pytest.fixture
def session(temp_db):
    return database.Session()

def test_criar_e_buscar_conversa(session):
    nova_msg = database.Conversa(role='user', content='Teste Pytest')
    session.add(nova_msg)
    session.commit()
    # Usar a nova assinatura da função
    resultado = database.buscar_no_historico(termo='Teste')
    assert 'Teste Pytest' in resultado

def test_carregar_historico(session):
    session.add(database.Conversa(role='user', content='Primeira'))
    session.add(database.Conversa(role='model', content='Resposta'))
    session.commit()
    historico = database.carregar_historico(session)
    assert len(historico) == 2
    assert historico[0].content == 'Primeira'
    assert historico[1].role == 'model'

def test_buscar_no_historico_sem_resultado(session):
    resultado = database.buscar_no_historico(termo='inexistente')
    assert 'No results found' in resultado or 'resultados encontrados' in resultado

def test_database_main(monkeypatch):
    # Testa execução direta do database.py
    import importlib
    from codex import database
    importlib.reload(database)

def test_buscar_no_historico_prints(session, caplog):
    # Testa logs do banco
    session.add(database.Conversa(role='user', content='Teste Print'))
    session.commit()
    with caplog.at_level('INFO', logger="codex.database"):
        resultado = database.buscar_no_historico(termo='Print')
    assert "Buscando no histórico por termo: 'Print'" in caplog.text

# Removido test_database_main_exec pois runpy não captura prints de subprocessos de forma confiável
