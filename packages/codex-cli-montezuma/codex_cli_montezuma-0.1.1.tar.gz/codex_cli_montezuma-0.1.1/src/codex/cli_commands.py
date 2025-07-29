"""
Module dedicated to parsing and executing Codex CLI commands.
Responsible for:
- Interpreting command-line arguments
- Executing special commands (doc, report, export, profile)
- Managing the main CLI interaction loop
- Deciding and executing tools
"""
from typing import Any, Dict, List, Optional, Callable
import sys
import pathlib
import json
import logging
from codex import database
from codex.suggestions import sugerir_pergunta_contextual, buscar_contexto_relevante
from codex.cli_core import PROMPT_MESTRA, FERRAMENTAS, gerar_documentacao_ferramentas
from codex.log_config import setup_logging
from locales.i18n import _

# Global logging configuration
setup_logging()

logger = logging.getLogger("codex.cli_commands")

def executar_comando_cli(args: List[str], client: Any, modelo_ia: str) -> None:
    """
    Interprets arguments and executes special commands or starts the CLI loop.
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
        print(database.gerar_relatorio_uso(session, n_mensagens=200))
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
    # Main CLI loop
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
        prompt_para_decidir: str = PROMPT_MESTRA + "\n\nPedido do Usuário: " + prompt_usuario
        response_decisao = client.generate_content(contents=prompt_para_decidir)
        resposta_ia: str = ""
        try:
            decodificado: Dict[str, Any] = json.loads(response_decisao.text)
            ferramenta: Optional[str] = decodificado.get("ferramenta")
            if ferramenta == "buscar_no_historico":
                termo: Optional[str] = decodificado.get('argumentos', {}).get('termo_chave')
                if termo is None:
                    resposta_ia = "[ERRO]: termo_chave não informado para busca no histórico."
                else:
                    logger.info(f"Tool 'buscar_no_historico' triggered for term: {termo}")
                    resultados = database.buscar_no_historico(session, termo_chave=termo)
                    contexto = "\n".join([f"- {res.role}: {res.content}" for res in resultados])
                    prompt_sintese = f"Contexto de conversas passadas:\n{contexto}\n\nBaseado nesse contexto, responda à pergunta original: '{prompt_usuario}'"
                    nova_response = client.generate_content(contents=prompt_sintese)
                    resposta_ia = nova_response.text
            elif ferramenta in FERRAMENTAS:
                logger.info(f"Tool '{ferramenta}' triggered with arguments: {decodificado.get('argumentos', {})}")
                resposta_ia = FERRAMENTAS[ferramenta](**decodificado.get('argumentos', {}))
            else:
                historico = database.carregar_historico(session)
                historico_formatado = "\n".join([f"- {msg.role}: {msg.content}" for msg in historico])
                prompt_conversa = f"Você é Codex, um mentor de IA. Histórico da conversa:\n{historico_formatado}\n\nResponda ao usuário: {prompt_usuario}"
                nova_response = client.generate_content(contents=prompt_conversa)
                resposta_ia = nova_response.text
        except (json.JSONDecodeError, TypeError):
            logger.warning("Failed to decode AI response as JSON. Returning raw text.")
            resposta_ia = response_decisao.text
        logger.info(f"AI response: {resposta_ia}")
        print(f"Codex: {resposta_ia}")
        session.add(database.Conversa(role="user", content=prompt_usuario))
        session.add(database.Conversa(role="model", content=resposta_ia))
        session.commit()
