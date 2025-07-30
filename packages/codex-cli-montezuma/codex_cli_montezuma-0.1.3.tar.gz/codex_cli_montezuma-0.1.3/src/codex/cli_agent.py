import os
import sys
import pathlib
import json
import requests
from google import genai
from google.genai import types
from . import database
from .integrations.wikipedia import consultar_wikipedia
from .integrations.stackoverflow import consultar_stackoverflow
from .integrations.google import consultar_google
from .integrations.github import consultar_github
from .integrations.wolframalpha import consultar_wolframalpha
from .cli_commands import executar_comando_cli
from .suggestions import buscar_contexto_relevante
from .cli_core import FERRAMENTAS, gerar_documentacao_ferramentas, checar_api_key
from .locales.i18n import _

def main():
    """Entry point for Codex global CLI."""
    # A inicialização do cliente e a verificação da chave foram movidas
    # para cli_commands.py para serem executadas apenas quando necessário.
    executar_comando_cli(sys.argv)

if __name__ == "__main__":
    main()
