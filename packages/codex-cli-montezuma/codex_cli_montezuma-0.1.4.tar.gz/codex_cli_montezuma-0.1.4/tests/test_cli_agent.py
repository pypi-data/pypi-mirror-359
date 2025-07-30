import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from codex.cli_agent import main as cli_main, checar_api_key
from codex.cli_core import escrever_arquivo, listar_arquivos, ler_arquivo
from codex.suggestions import sugerir_pergunta_frequente

@patch("google.genai.Client")
def test_cli_agent_runs(mock_genai_client, monkeypatch):
    # Configura o mock do cliente genai
    mock_instance = mock_genai_client.return_value
    mock_response = MagicMock()
    mock_response.text = "Texto de resposta simulado."
    mock_instance.models.generate_content.return_value = mock_response

    # Simula uma sequência de entradas do usuário e captura as saídas
    inputs = iter(["olá Codex!", "sair", "sair", "sair", "sair", "sair"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    # Não testamos a integração com a IA real aqui, só o fluxo CLI
    try:
        cli_main()
    except SystemExit:
        pass  # Permite sair normalmente

def test_cli_agent_input_vazio(monkeypatch):
    inputs = iter(["", "sair"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    try:
        cli_main()
    except SystemExit:
        pass

@patch("google.genai.Client")
def test_cli_agent_comando_invalido(mock_genai_client, monkeypatch):
    # Configura o mock do modelo de IA
    mock_instance = mock_genai_client.return_value
    mock_response = MagicMock()
    mock_response.text = "Texto de resposta simulado."
    mock_instance.models.generate_content.return_value = mock_response
    inputs = iter(["olá Codex!", "sair", "sair", "sair", "sair", "sair", "sair"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    # Não testamos a integração com a IA real aqui, só o fluxo CLI
    try:
        cli_main()
    except SystemExit:
        pass

@patch("google.genai.Client")
def test_checar_api_key_ausente(monkeypatch):
    # Remove a variável de ambiente para simular erro
    old_key = os.environ.pop("GOOGLE_API_KEY", None)
    try:
        with pytest.raises(SystemExit):
            checar_api_key()
    finally:
        if old_key:
            os.environ["GOOGLE_API_KEY"] = old_key

def test_escrever_arquivo_erro_json():
    # Simula erro de JSON na resposta da IA
    resposta = escrever_arquivo(nome_do_arquivo=None, conteudo=None)
    assert "ERRO" in resposta

@patch("google.genai.Client")
def test_cli_agent_branch_buscar_no_historico(mock_genai_client, monkeypatch):
    mock_instance = mock_genai_client.return_value
    mock_response = MagicMock()
    # mock_response.text = '{"ferramenta": "buscar_no_historico", "argumentos": {"termo_chave": "Quantum"}}'
    class FakeResponse:
        def __init__(self, text):
            self.text = text
    mock_instance.models.generate_content.return_value = FakeResponse('{"ferramenta": "buscar_no_historico", "argumentos": {"termo_chave": "Quantum"}}')

    # Garantir que o valor de .text seja uma string real
    mock_instance.models.generate_content.return_value.text = str(mock_response.text)

    inputs = iter(["o que nós conversamos sobre o projeto Quantum?", "sair", "sair", "sair", "sair"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    try:
        cli_main()
    except SystemExit:
        pass

@patch("google.genai.Client")
def test_cli_agent_branch_escrever_arquivo(mock_genai_client, monkeypatch):
    # Simula resposta da IA para escrever_arquivo
    mock_response = MagicMock()
    mock_response.text = '{"ferramenta": "escrever_arquivo", "argumentos": {"nome_do_arquivo": "mock.txt", "conteudo": "mock"}}'
    instance = mock_genai_client.return_value
    instance.models.generate_content.return_value = mock_response  # Retorna objeto com .text
    inputs = iter(["crie um arquivo chamado 'mock.txt' com o conteúdo 'mock'", "sair", "sair", "sair"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    try:
        cli_main()
    except SystemExit:
        pass

@patch("google.genai.Client")
def test_cli_agent_branch_resposta_padrao(mock_genai_client, monkeypatch):
    # Simula resposta da IA para branch padrão
    mock_response = MagicMock()
    mock_response.text = 'Olá, esta é uma resposta padrão.'
    instance = mock_genai_client.return_value
    instance.models.generate_content.return_value = mock_response  # Retorna objeto com .text
    inputs = iter(["me conte uma piada", "sair", "sair", "sair"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    try:
        cli_main()
    except SystemExit:
        pass

def test_cli_agent_print_saida(monkeypatch, capsys):
    # Simula resposta inválida para forçar JSONDecodeError
    from unittest.mock import patch, MagicMock
    # Adicionado mock para checar_api_key
    monkeypatch.setattr("codex.cli_commands.checar_api_key", lambda: "fake_api_key")
    with patch("google.genai.Client") as mock_genai_client:
        mock_response = MagicMock()
        mock_response.text = "resposta inválida"
        instance = mock_genai_client.return_value
        instance.models.generate_content.return_value = mock_response

        inputs = iter(["forçar erro json", "sair", "sair", "sair"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        try:
            cli_main()
        except SystemExit:
            pass

        captured = capsys.readouterr()
        assert "Codex: resposta inválida" in captured.out

@patch("google.genai.Client")
def test_cli_agent_branch_else(mock_genai_client, monkeypatch):
    # Simula resposta da IA para branch else
    mock_response = MagicMock()
    # mock_response.text = '{"ferramenta": "outra_ferramenta", "argumentos": {}}'
    class FakeResponse:
        def __init__(self, text):
            self.text = text
    instance = mock_genai_client.return_value
    instance.models.generate_content.return_value = FakeResponse('{"ferramenta": "outra_ferramenta", "argumentos": {}}')

    # Garantir que o valor de .text seja uma string real
    instance.models.generate_content.return_value.text = str(mock_response.text)

    inputs = iter(["comando desconhecido", "sair", "sair", "sair", "sair"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    try:
        cli_main()
    except SystemExit:
        pass

def test_sugerir_pergunta_frequente(monkeypatch):
    # Simula a sugestão de uma pergunta frequente
    from unittest.mock import patch, MagicMock
    monkeypatch.setattr("codex.cli_commands.checar_api_key", lambda: "fake_api_key")
    with patch("google.genai.Client") as mock_genai_client:
        mock_response = MagicMock()
        mock_response.text = '{"ferramenta": "pergunta_frequente", "argumentos": {"pergunta": "Qual o sentido da vida?"}}'
        instance = mock_genai_client.return_value
        instance.models.generate_content.return_value = mock_response  # Retorna objeto com .text
        inputs = iter(["qual o sentido da vida?", "sair", "sair", "sair"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        try:
            cli_main()
        except SystemExit:
            pass

@patch("codex.cli_core.listar_arquivos")
def test_listar_arquivos(mock_listar_arquivos, tmp_path):
    # Cria estrutura de diretório temporária
    pasta = tmp_path / "docs"
    pasta.mkdir()
    (pasta / "arquivo1.txt").write_text("abc")
    (pasta / "arquivo2.txt").write_text("def")
    mock_listar_arquivos.side_effect = lambda caminho, base_path: [f"{caminho}/arquivo1.txt", f"{caminho}/arquivo2.txt"]
    resultado = listar_arquivos(caminho="docs", base_path=tmp_path)
    assert "arquivo1.txt" in resultado and "arquivo2.txt" in resultado
    # Testa diretório vazio
    pasta_vazia = tmp_path / "vazio"
    pasta_vazia.mkdir()
    mock_listar_arquivos.side_effect = lambda caminho, base_path: []
    resultado_vazio = listar_arquivos(caminho="vazio", base_path=tmp_path)
    assert "está vazio" in resultado_vazio
    # Testa diretório inexistente
    mock_listar_arquivos.side_effect = FileNotFoundError
    resultado_erro = listar_arquivos(caminho="nao_existe", base_path=tmp_path)
    assert "não encontrado" in resultado_erro

def test_ler_arquivo(tmp_path):
    from codex.cli_core import ler_arquivo
    # Cria arquivo de teste
    arquivo = tmp_path / "exemplo.txt"
    arquivo.write_text("conteudo de teste")
    # Testa leitura normal
    resultado = ler_arquivo(nome_do_arquivo="exemplo.txt", base_path=tmp_path)
    assert "conteudo de teste" in resultado
    # Testa arquivo vazio
    arquivo_vazio = tmp_path / "vazio.txt"
    arquivo_vazio.write_text("")
    resultado_vazio = ler_arquivo(nome_do_arquivo="vazio.txt", base_path=tmp_path)
    assert "está vazio" in resultado_vazio
    # Testa arquivo inexistente
    resultado_erro = ler_arquivo(nome_do_arquivo="nao_existe.txt", base_path=tmp_path)
    assert "não encontrado" in resultado_erro
    # Testa sem nome
    resultado_sem_nome = ler_arquivo(nome_do_arquivo="", base_path=tmp_path)
    assert "não informado" in resultado_sem_nome
    # Testa arquivo grande
    arquivo_grande = tmp_path / "grande.txt"
    arquivo_grande.write_text("a" * 3000)
    resultado_grande = ler_arquivo(nome_do_arquivo="grande.txt", base_path=tmp_path)
    assert "primeiras 2000 letras" in resultado_grande

@patch("codex.cli_agent.requests.get")
def test_consultar_stackoverflow_sucesso(mock_get):
    from codex.integrations.stackoverflow import consultar_stackoverflow
    # Mock da busca de perguntas
    mock_resp_perg = MagicMock()
    mock_resp_perg.json.return_value = {
        "items": [{
            "title": "Como usar pytest?",
            "link": "https://stackoverflow.com/q/123",
            "question_id": 123
        }]
    }
    mock_resp_perg.status_code = 200
    # Mock da busca de respostas
    mock_resp_resp = MagicMock()
    mock_resp_resp.json.return_value = {
        "items": [{"body": "<p>Use o comando <code>pytest</code> no terminal.</p>"}]
    }
    mock_resp_resp.status_code = 200
    mock_get.side_effect = [mock_resp_perg, mock_resp_resp]
    resultado = consultar_stackoverflow(termo="pytest")
    assert "Como usar pytest?" in resultado
    assert "https://stackoverflow.com/q/123" in resultado
    assert "pytest" in resultado

@patch("codex.integrations.stackoverflow.requests.get")
def test_consultar_stackoverflow_sem_resultado(mock_get):
    from codex.integrations.stackoverflow import consultar_stackoverflow
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"items": []}
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp
    resultado = consultar_stackoverflow(termo="termo_inexistente_abcxyz")
    assert "Nenhuma pergunta encontrada" in resultado

@patch("codex.integrations.stackoverflow.requests.get")
def test_consultar_stackoverflow_sem_termo(mock_get):
    from codex.integrations.stackoverflow import consultar_stackoverflow
    resultado = consultar_stackoverflow(termo="")
    assert "Nenhum termo informado" in resultado

@patch("codex.integrations.stackoverflow.requests.get")
def test_consultar_stackoverflow_erro_api(mock_get):
    from codex.integrations.stackoverflow import consultar_stackoverflow
    mock_get.side_effect = Exception("Erro de conexão")
    resultado = consultar_stackoverflow(termo="pytest")
    assert "ERRO DA FERRAMENTA" in resultado

from unittest.mock import patch, MagicMock

@patch("codex.cli_agent.requests.get")
def test_consultar_google_sucesso(mock_get, monkeypatch):
    from codex.integrations.google import consultar_google
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "items": [
            {"title": "Python Docs", "link": "https://python.org", "snippet": "Documentação oficial do Python."},
            {"title": "PyPI", "link": "https://pypi.org", "snippet": "Repositório de pacotes Python."},
            {"title": "Stack Overflow", "link": "https://stackoverflow.com", "snippet": "Perguntas e respostas sobre Python."}
        ]
    }
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp
    monkeypatch.setenv("GOOGLE_SEARCH_API_KEY", "fake-key")
    monkeypatch.setenv("GOOGLE_SEARCH_CX", "fake-cx")
    resultado = consultar_google(termo="python")
    assert "Python Docs" in resultado
    assert "PyPI" in resultado
    assert "Stack Overflow" in resultado

@patch("codex.integrations.google.requests.get")
def test_consultar_google_sem_resultado(mock_get, monkeypatch):
    from codex.integrations.google import consultar_google
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"items": []}
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp
    monkeypatch.setenv("GOOGLE_SEARCH_API_KEY", "fake-key")
    monkeypatch.setenv("GOOGLE_SEARCH_CX", "fake-cx")
    resultado = consultar_google(termo="termo_inexistente_abcxyz")
    assert "Nenhum resultado encontrado" in resultado

@patch("codex.integrations.google.requests.get")
def test_consultar_google_sem_termo(mock_get, monkeypatch):
    from codex.integrations.google import consultar_google
    monkeypatch.setenv("GOOGLE_SEARCH_API_KEY", "fake-key")
    monkeypatch.setenv("GOOGLE_SEARCH_CX", "fake-cx")
    resultado = consultar_google(termo="")
    assert "Nenhum termo informado" in resultado

@patch("codex.integrations.google.requests.get")
def test_consultar_google_sem_api_key_ou_cx(mock_get, monkeypatch):
    from codex.integrations.google import consultar_google
    monkeypatch.delenv("GOOGLE_SEARCH_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_SEARCH_CX", raising=False)
    resultado = consultar_google(termo="python")
    assert "Para usar a busca no Google, configure as variáveis" in resultado

@patch("codex.integrations.google.requests.get")
def test_consultar_google_erro_api(mock_get, monkeypatch):
    from codex.integrations.google import consultar_google
    monkeypatch.setenv("GOOGLE_SEARCH_API_KEY", "fake-key")
    monkeypatch.setenv("GOOGLE_SEARCH_CX", "fake-cx")
    mock_get.side_effect = Exception("Erro de conexão")
    resultado = consultar_google(termo="python")
    assert "ERRO DA FERRAMENTA" in resultado

@patch("codex.integrations.github.requests.get")
def test_consultar_github_sucesso(mock_get):
    from codex.integrations.github import consultar_github
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "items": [
            {"full_name": "psf/requests", "html_url": "https://github.com/psf/requests", "description": "HTTP for Humans."},
            {"full_name": "pallets/flask", "html_url": "https://github.com/pallets/flask", "description": "Web framework."},
            {"full_name": "pytest-dev/pytest", "html_url": "https://github.com/pytest-dev/pytest", "description": "Testing framework."}
        ]
    }
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp
    resultado = consultar_github(termo="python")
    assert "psf/requests" in resultado
    assert "pallets/flask" in resultado
    assert "pytest-dev/pytest" in resultado

@patch("codex.integrations.github.requests.get")
def test_consultar_github_sem_resultado(mock_get):
    from codex.integrations.github import consultar_github
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"items": []}
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp
    resultado = consultar_github(termo="termo_inexistente_abcxyz")
    assert "Nenhum repositório encontrado" in resultado

@patch("codex.integrations.github.requests.get")
def test_consultar_github_sem_termo(mock_get):
    from codex.integrations.github import consultar_github
    resultado = consultar_github(termo="")
    assert "Nenhum termo informado" in resultado

@patch("codex.integrations.github.requests.get")
def test_consultar_github_erro_api(mock_get):
    from codex.integrations.github import consultar_github
    mock_get.side_effect = Exception("Erro de conexão")
    resultado = consultar_github(termo="python")
    assert "ERRO DA FERRAMENTA" in resultado

@patch("codex.integrations.wolframalpha.requests.get")
def test_consultar_wolframalpha_sucesso(mock_get, monkeypatch):
    from codex.integrations.wolframalpha import consultar_wolframalpha
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "42"
    mock_get.return_value = mock_resp
    monkeypatch.setenv("WOLFRAMALPHA_APPID", "fake-appid")
    resultado = consultar_wolframalpha(termo="meaning of life")
    assert "42" in resultado

@patch("codex.integrations.wolframalpha.requests.get")
def test_consultar_wolframalpha_sem_termo(mock_get, monkeypatch):
    from codex.integrations.wolframalpha import consultar_wolframalpha
    monkeypatch.setenv("WOLFRAMALPHA_APPID", "fake-appid")
    resultado = consultar_wolframalpha(termo="")
    assert "Nenhum termo informado" in resultado

@patch("codex.integrations.wolframalpha.requests.get")
def test_consultar_wolframalpha_sem_appid(mock_get, monkeypatch):
    from codex.integrations.wolframalpha import consultar_wolframalpha
    monkeypatch.delenv("WOLFRAMALPHA_APPID", raising=False)
    resultado = consultar_wolframalpha(termo="2+2")
    assert "Para usar WolframAlpha, configure a variável" in resultado

@patch("codex.integrations.wolframalpha.requests.get")
def test_consultar_wolframalpha_erro_api(mock_get, monkeypatch):
    from codex.integrations.wolframalpha import consultar_wolframalpha
    monkeypatch.setenv("WOLFRAMALPHA_APPID", "fake-appid")
    mock_get.side_effect = Exception("Erro de conexão")
    resultado = consultar_wolframalpha(termo="2+2")
    assert "ERRO DA FERRAMENTA" in resultado

@patch("codex.integrations.wolframalpha.requests.get")
def test_consultar_wolframalpha_nao_sabe(mock_get, monkeypatch):
    from codex.integrations.wolframalpha import consultar_wolframalpha
    mock_resp = MagicMock()
    mock_resp.status_code = 501
    mock_resp.text = "WolframAlpha does not understand your input"
    mock_get.return_value = mock_resp
    monkeypatch.setenv("WOLFRAMALPHA_APPID", "fake-appid")
    resultado = consultar_wolframalpha(termo="pergunta impossível")
    assert "não sabe responder" in resultado

# Correção: garantir que todos os imports e patches nos testes estejam corretos após a modularização.
# Exemplo de import correto para testes:
# from src.cli_core import escrever_arquivo, listar_arquivos, ler_arquivo
# from src.suggestions import sugerir_pergunta_frequente, sugerir_pergunta_contextual, buscar_contexto_relevante
# from src.integrations.stackoverflow import consultar_stackoverflow
# from src.integrations.google import consultar_google
# from src.integrations.github import consultar_github
# from src.integrations.wikipedia import consultar_wikipedia
# from src.integrations.wolframalpha import consultar_wolframalpha
#
# Exemplo de patch correto para IA:
# from unittest.mock import patch
# @patch("google.genai.Client")
# def test_alguma_coisa(mock_genai_client, ...):
#     ...
# Exemplo de patch correto para sugestões/contexto:
# monkeypatch.setattr("src.suggestions.sugerir_pergunta_contextual", lambda session: ...)
# monkeypatch.setattr("src.suggestions.buscar_contexto_relevante", lambda session, pergunta_usuario, n=5: ...)
