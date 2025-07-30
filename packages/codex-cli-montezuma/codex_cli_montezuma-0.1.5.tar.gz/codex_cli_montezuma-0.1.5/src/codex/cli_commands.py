"""
Module dedicated to parsing and executing Codex CLI commands.
Responsible for:
- Interpreting command-line arguments
- Executing special commands (doc, report, export, profile)
- Managing the main CLI interaction loop
- Using official Gemini Function Calling
"""
from typing import Any, Dict, List, Optional, Callable
import sys
import pathlib
import json
import logging
from google import genai
from google.genai import types
from . import database
from .suggestions import sugerir_pergunta_contextual, buscar_contexto_relevante
from .cli_core import FERRAMENTAS, gerar_documentacao_ferramentas
from .log_config import setup_logging
from .locales.i18n import _
from .cli_core import checar_api_key

# Global logging configuration
setup_logging()

logger = logging.getLogger("codex.cli_commands")


def executar_comando_cli(args: List[str]) -> None:
    """
    Interpreta argumentos e executa comandos especiais ou inicia o loop da CLI.
    A inicialização do cliente da IA e a verificação da chave são feitas aqui
    para garantir que ocorram apenas quando necessário.
    """
    modo_limpo = '--clean' in args
    modo_verbose = '--verbose' in args
    modo_quiet = '--quiet' in args
    if modo_quiet:
        setup_logging(level="ERROR")
    elif modo_verbose:
        setup_logging(level="INFO")
    else:
        setup_logging(level="WARNING")
    logger.info(_("Starting CLI execution with args: {args}").format(args=args))
    primeira_interacao = True
    if len(args) > 1 and args[1] == "--doc-ferramentas":
        doc: str = gerar_documentacao_ferramentas()
        doc_path = pathlib.Path(__file__).parent / "docs/guia_didatico/auto_documentacao_ferramentas.md"
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc)
        logger.info(_("Tools documentation updated at {doc_path}").format(doc_path=doc_path))
        return
    if len(args) > 1 and args[1] == "--relatorio-uso":
        session = database.Session()
        logger.info(_("Generating usage report..."))
        relatorio = database.gerar_relatorio_uso(session, n_mensagens=200)
        print(relatorio)
        return
    if len(args) > 1 and args[1] == "--exportar-jsonl":
        session = database.Session()
        logger.info(_("Exporting history to JSONL..."))
        print(database.exportar_historico_jsonl(session))
        return
    if len(args) > 1 and args[1] == "--perfil-usuario":
        session = database.Session()
        perfil = database.perfil_usuario(session)
        logger.info(_("User profile summary: {perfil}").format(perfil=perfil))
        print(_("User profile summary:"))
        for k, v in perfil.items():
            print(f"- {k}: {v}")
        return

    # A partir deste ponto, os comandos exigem a API do Google.
    API_KEY = checar_api_key()
    client = genai.Client(api_key=API_KEY)
    modelo_ia = "gemini-1.5-flash"

    database.criar_banco_e_tabelas()
    session = database.Session()
    logger.info(_("Welcome to Codex CLI! Main loop started."))
    print(_("Welcome to Codex CLI! Type 'sair' to exit."))
    print(_("Type '/sugestoes' to see suggestions, '/historico' to see context, or 'ajuda' for commands."))
    while True:
        prompt_usuario: str = ''
        if not modo_limpo and primeira_interacao:
            sugestoes: List[str] = sugerir_pergunta_contextual(session)
            if sugestoes:
                logger.debug(f"Suggestions presented to the user: {sugestoes}")
                print("[Codex Suggestions]")
                for s in sugestoes:
                    print(f"- {s}")
            primeira_interacao = False
        prompt_usuario = input("Você: ")
        if prompt_usuario.strip().lower() in ['/sugestoes', '?']:
            sugestoes: List[str] = sugerir_pergunta_contextual(session)
            if sugestoes:
                print("[Codex Suggestions]")
                for s in sugestoes:
                    print(f"- {s}")
            continue
        if prompt_usuario.strip().lower() in ['/historico', '!h']:
            contexto_relevante: List[str] = buscar_contexto_relevante(session, '', n=5)
            if contexto_relevante:
                print("[Relevant context from history]")
                for linha in contexto_relevante:
                    print(linha)
            continue
        if prompt_usuario.strip().lower() in ['ajuda', '--help', '-h']:
            print(_("Available commands:\n  /sugestoes or ?  - See suggestions\n  /historico or !h - View history context\n  sair            - End session\n  ajuda           - Show this help\n  --clean         - Clean mode (no automatic suggestions)\n  --verbose       - Show detailed logs\n  --quiet         - Hide all logs except critical errors"))
            continue
        if prompt_usuario.strip() == '' and not modo_limpo:
            continue
        if prompt_usuario.strip().lower() == 'sair':
            logger.info("User ended the session.")
            print(_("See you soon!"))
            break
        # Simplified approach: use direct Python functions as tools
        # This uses automatic function calling which is more reliable
        from .cli_core import escrever_arquivo, listar_arquivos, ler_arquivo
        from .integrations.wikipedia import consultar_wikipedia
        from .integrations.stackoverflow import consultar_stackoverflow  
        from .integrations.google import consultar_google
        from .integrations.github import consultar_github
        from .integrations.wolframalpha import consultar_wolframalpha
        
        # Use Python functions directly - SDK will handle schema generation
        tools = [
            escrever_arquivo,
            listar_arquivos, 
            ler_arquivo,
            consultar_wikipedia,
            consultar_stackoverflow,
            consultar_google,
            consultar_github,
            consultar_wolframalpha
        ]
        
        config = types.GenerateContentConfig(
            tools=tools,
            # Enable automatic function calling
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
        )
        
        # Simple user prompt
        contents = [types.Content(role="user", parts=[types.Part(text=prompt_usuario)])]
        
        try:
            response = client.models.generate_content(
                model=modelo_ia,
                contents=contents,
                config=config
            )
            
            resposta_ia = getattr(response, 'text', str(response))
                
        except Exception as e:
            logger.error(f"Error during model generation: {e}")
            resposta_ia = f"[ERRO]: Erro ao processar solicitação: {e}"
        logger.info(f"AI response: {resposta_ia}")
        print(f"Codex: {resposta_ia}")
        session.add(database.Conversa(role="user", content=prompt_usuario))
        session.add(database.Conversa(role="model", content=resposta_ia))
        session.commit()
