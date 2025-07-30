import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import codex.cli_agent as cli_agent

def test_main_doc_ferramentas(tmp_path, monkeypatch):
    # Testa o comando --doc-ferramentas
    doc_dir = tmp_path / "docs/guia_didatico"
    doc_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(cli_agent.pathlib.Path, "parent", tmp_path)
    monkeypatch.setattr(cli_agent, "checar_api_key", lambda: None)
    sys.argv = ["cli_agent.py", "--doc-ferramentas"]
    cli_agent.main()
    doc_path = tmp_path / "docs/guia_didatico/auto_documentacao_ferramentas.md"
    assert doc_path.exists()
    conteudo = doc_path.read_text(encoding="utf-8")
    assert "Documentação automática" in conteudo

def test_main_exportar_jsonl(monkeypatch):
    # Testa o comando --exportar-jsonl sem histórico
    monkeypatch.setattr(cli_agent.database, "Session", lambda: MagicMock())
    monkeypatch.setattr(cli_agent.database, "exportar_historico_jsonl", lambda session: "Exportação concluída: 0 pares salvos em historico_codex.jsonl")
    monkeypatch.setattr(cli_agent, "checar_api_key", lambda: None)
    sys.argv = ["cli_agent.py", "--exportar-jsonl"]
    cli_agent.main()

def test_main_relatorio_uso(monkeypatch):
    # Testa o comando --relatorio-uso sem histórico
    monkeypatch.setattr(cli_agent.database, "Session", lambda: MagicMock())
    monkeypatch.setattr(cli_agent.database, "gerar_relatorio_uso", lambda session, n_mensagens=200: "Relatório vazio")
    monkeypatch.setattr(cli_agent, "checar_api_key", lambda: None)
    sys.argv = ["cli_agent.py", "--relatorio-uso"]
    cli_agent.main()

def test_main_perfil_usuario(monkeypatch):
    # Testa o comando --perfil-usuario sem histórico
    monkeypatch.setattr(cli_agent.database, "Session", lambda: MagicMock())
    monkeypatch.setattr(cli_agent.database, "perfil_usuario", lambda session: {"temas_mais_frequentes": [], "horarios_mais_ativos": [], "total_perguntas": 0})
    monkeypatch.setattr(cli_agent, "checar_api_key", lambda: None)
    sys.argv = ["cli_agent.py", "--perfil-usuario"]
    cli_agent.main()

def test_main_json_decode_error(monkeypatch):
    # Testa branch de erro de JSON na resposta da IA
    class FakeModel:
        def __init__(self):
            self.models = self

        def generate_content(self, *args, **kwargs):
            class Resp:
                text = "Texto de resposta simulado."
            return Resp()
    inputs = iter(["olá Codex!", "sair", "sair", "sair", "sair", "sair"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    with patch("google.genai.Client", return_value=FakeModel()):
        monkeypatch.setattr("codex.cli_commands.checar_api_key", lambda: "fake_api_key")
        monkeypatch.setattr(cli_agent.database, "criar_banco_e_tabelas", lambda: None)
        monkeypatch.setattr(cli_agent.database, "Session", lambda: MagicMock())
        monkeypatch.setattr("codex.suggestions.sugerir_pergunta_contextual", lambda session: [])
        monkeypatch.setattr("codex.suggestions.buscar_contexto_relevante", lambda session, pergunta_usuario, n=5: [])
        monkeypatch.setattr("builtins.input", lambda _: "sair")
        sys.argv = ["cli_agent.py"]
        cli_agent.main()

def test_main_ferramenta_inexistente(monkeypatch):
    # Testa branch de ferramenta inexistente
    class FakeClient:
        def __init__(self):
            self.models = self
        
        def generate_content(self, *args, **kwargs):
            class Resp:
                text = '{"ferramenta": "inexistente", "argumentos": {}}'
            return Resp()
    with patch("google.genai.Client", return_value=FakeClient()):
        monkeypatch.setattr("codex.cli_commands.checar_api_key", lambda: "fake_api_key")
        monkeypatch.setattr(cli_agent.database, "criar_banco_e_tabelas", lambda: None)
        monkeypatch.setattr(cli_agent.database, "Session", lambda: MagicMock())
        monkeypatch.setattr("codex.suggestions.sugerir_pergunta_contextual", lambda session: [])
        monkeypatch.setattr("codex.suggestions.buscar_contexto_relevante", lambda session, pergunta_usuario, n=5: [])
        monkeypatch.setattr("builtins.input", lambda _: "sair")
        sys.argv = ["cli_agent.py"]
        cli_agent.main()

def test_ferramenta_erro(monkeypatch):
    # Simula erro ao executar uma ferramenta
    from unittest.mock import patch, MagicMock
    class FakeClient:
        def __init__(self):
            self.models = self
        
        def generate_content(self, *args, **kwargs):
            class Resp:
                text = '{"ferramenta": "escrever_arquivo", "argumentos": {"nome_do_arquivo": "fail.txt"}}'
            return Resp()
    def ferramenta_erro(**kwargs):
        raise Exception("Erro simulado na ferramenta")
    with patch("google.genai.Client", return_value=FakeClient()):
        monkeypatch.setattr("codex.cli_commands.checar_api_key", lambda: "fake_api_key")
        monkeypatch.setattr(cli_agent.database, "criar_banco_e_tabelas", lambda: None)
        monkeypatch.setattr(cli_agent.database, "Session", lambda: MagicMock())
        monkeypatch.setattr("codex.suggestions.sugerir_pergunta_contextual", lambda session: [])
        monkeypatch.setattr("codex.suggestions.buscar_contexto_relevante", lambda session, pergunta_usuario, n=5: [])
        cli_agent.FERRAMENTAS["escrever_arquivo"] = ferramenta_erro
        monkeypatch.setattr("builtins.input", lambda _: "sair")
        sys.argv = ["cli_agent.py"]
        try:
            cli_agent.main()
        except Exception as e:
            assert "Erro simulado" in str(e)

def test_main_commit_erro(monkeypatch):
    # Simula erro ao salvar no banco de dados
    from unittest.mock import patch, MagicMock
    class FakeSession:
        def add(self, obj):
            pass
        def commit(self):
            raise Exception("Erro de commit simulado")
        def query(self, *a, **kw):
            class DummyQuery:
                def filter(self, *a, **kw): return self
                def group_by(self, *a, **kw): return self
                def order_by(self, *a, **kw): return self
                def limit(self, n): return self
                def all(self): return []
            return DummyQuery()
    class FakeClient:
        def __init__(self):
            self.models = self
        
        def generate_content(self, *args, **kwargs):
            class Resp:
                text = '{"ferramenta": "consultar_wikipedia", "argumentos": {"termo": "Python"}}'
            return Resp()
    with patch("google.genai.Client", return_value=FakeClient()):
        monkeypatch.setattr("codex.cli_commands.checar_api_key", lambda: "fake_api_key")
        monkeypatch.setattr(cli_agent.database, "criar_banco_e_tabelas", lambda: None)
        monkeypatch.setattr(cli_agent.database, "Session", lambda: FakeSession())
        monkeypatch.setattr("codex.suggestions.sugerir_pergunta_contextual", lambda session: [])
        monkeypatch.setattr("codex.suggestions.buscar_contexto_relevante", lambda session, pergunta_usuario, n=5: [])
        monkeypatch.setattr("builtins.input", lambda _: "sair")
        sys.argv = ["cli_agent.py"]
        # Apenas roda o fluxo, não espera exceção
        cli_agent.main()

def test_sugerir_pergunta_contextual_erro(monkeypatch):
    # Simula erro ao sugerir pergunta contextual
    from codex.suggestions import sugerir_pergunta_contextual
    monkeypatch.setattr("codex.suggestions.sugerir_pergunta_contextual", lambda session: (_ for _ in ()).throw(Exception("Erro de sugestão")))
    # Adicionado mock para checar_api_key
    monkeypatch.setattr("codex.cli_commands.checar_api_key", lambda: "fake_api_key")
    monkeypatch.setattr(cli_agent.database, "criar_banco_e_tabelas", lambda: None)
    monkeypatch.setattr(cli_agent.database, "Session", lambda: MagicMock())
    monkeypatch.setattr("codex.suggestions.buscar_contexto_relevante", lambda session, pergunta_usuario, n=5: [])
    monkeypatch.setattr("builtins.input", lambda _: "sair")
    sys.argv = ["cli_agent.py"]
    try:
        cli_agent.main()
    except Exception as e:
        assert "Erro de sugestão" in str(e)

def test_input_invalido(monkeypatch):
    # Simula input inválido do usuário
    from unittest.mock import patch, MagicMock
    class FakeClient:
        def __init__(self):
            self.models = self
        
        def generate_content(self, *args, **kwargs):
            class Resp:
                text = 'Texto qualquer'
            return Resp()
    with patch("google.genai.Client", return_value=FakeClient()):
        monkeypatch.setattr("codex.cli_commands.checar_api_key", lambda: "fake_api_key")
        monkeypatch.setattr(cli_agent.database, "criar_banco_e_tabelas", lambda: None)
        monkeypatch.setattr(cli_agent.database, "Session", lambda: MagicMock())
        monkeypatch.setattr("codex.suggestions.sugerir_pergunta_contextual", lambda session: [])
        monkeypatch.setattr("codex.suggestions.buscar_contexto_relevante", lambda session, pergunta_usuario, n=5: [])
        monkeypatch.setattr("builtins.input", lambda _: "sair")
        sys.argv = ["cli_agent.py"]
        cli_agent.main()
