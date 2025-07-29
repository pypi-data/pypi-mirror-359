"""
Core module for Codex CLI: constants, tool registry, and utilities.
"""
from codex.integrations.wikipedia import consultar_wikipedia
from codex.integrations.stackoverflow import consultar_stackoverflow
from codex.integrations.google import consultar_google
from codex.integrations.github import consultar_github
from codex.integrations.wolframalpha import consultar_wolframalpha
from typing import Any, Optional, Union
import pathlib
import os
import logging
from codex.log_config import setup_logging
from locales.i18n import _

# Global logging configuration
setup_logging()

logger = logging.getLogger("codex.cli_core")

def escrever_arquivo(**kwargs: Any) -> str:
    nome_do_arquivo: Optional[str] = kwargs.get("nome_do_arquivo")
    conteudo: Optional[str] = kwargs.get("conteudo")
    base_path: pathlib.Path = pathlib.Path(__file__).parent
    if not nome_do_arquivo or not conteudo:
        logger.warning(_("File name or content not provided."))
        return _("[ERROR]: File name or content not provided.")
    try:
        caminho_final: pathlib.Path = base_path / nome_do_arquivo
        with open(caminho_final, "w", encoding='utf-8') as f:
            f.write(conteudo)
        logger.info(_("Arquivo '{file}' criado em {path}." ).format(file=nome_do_arquivo, path=caminho_final))
        return _("[AÇÃO]: Arquivo '{file}' criado na pasta do projeto.").format(file=nome_do_arquivo)
    except Exception as e:
        logger.error(_("Error creating file '{file}': {err}").format(file=nome_do_arquivo, err=e))
        return _("[TOOL ERROR]: {err}").format(err=e)

def listar_arquivos(**kwargs: Any) -> str:
    caminho: str = kwargs.get("caminho", ".")
    base_path: Union[str, pathlib.Path] = kwargs.get("base_path", pathlib.Path(__file__).parent)
    dir_path: pathlib.Path = (pathlib.Path(base_path) / caminho).resolve()
    if not dir_path.exists() or not dir_path.is_dir():
        logger.warning("Diretório '{dir}' não encontrado.".format(dir=caminho))
        return "[ERRO]: Diretório '{dir}' não encontrado.".format(dir=caminho)
    itens = sorted(os.listdir(dir_path))
    if not itens:
        logger.info("Diretório '{dir}' está vazio.".format(dir=caminho))
        return "[INFO]: Diretório '{dir}' está vazio.".format(dir=caminho)
    logger.debug(_("Contents of '{dir}': {items}").format(dir=caminho, items=itens))
    return _("Contents of '{dir}':\n").format(dir=caminho) + "\n".join(itens)

def ler_arquivo(**kwargs: Any) -> str:
    nome_do_arquivo: Optional[str] = kwargs.get("nome_do_arquivo")
    base_path: Union[str, pathlib.Path] = kwargs.get("base_path", pathlib.Path(__file__).parent)
    if not nome_do_arquivo:
        logger.warning(_("[ERRO]: Nome do arquivo não informado."))
        return _("[ERRO]: Nome do arquivo não informado.")
    caminho_final: pathlib.Path = (pathlib.Path(base_path) / nome_do_arquivo).resolve()
    try:
        if not caminho_final.exists() or not caminho_final.is_file():
            logger.warning("Arquivo '{file}' não encontrado.".format(file=nome_do_arquivo))
            return "[ERRO]: Arquivo '{file}' não encontrado.".format(file=nome_do_arquivo)
        with open(caminho_final, "r", encoding='utf-8') as f:
            conteudo: str = f.read()
        if not conteudo.strip():
            logger.info("Arquivo '{file}' está vazio.".format(file=nome_do_arquivo))
            return "[INFO]: Arquivo '{file}' está vazio.".format(file=nome_do_arquivo)
        if len(conteudo) > 2000:
            logger.info(_("Arquivo '{file}' é grande, mostrando apenas parte do conteúdo.").format(file=nome_do_arquivo))
            return _("[INFO]: Arquivo muito grande, mostrando as primeiras 2000 letras:\n{content}...").format(content=conteudo[:2000])
        logger.debug(_("Content read from '{file}'.").format(file=nome_do_arquivo))
        return _("Content of '{file}':\n{content}").format(file=nome_do_arquivo, content=conteudo)
    except Exception as e:
        logger.error(_("Error reading file '{file}': {err}").format(file=nome_do_arquivo, err=e))
        return _("[TOOL ERROR]: {err}").format(err=e)

PROMPT_MESTRA = _(
    """
You are Codex, an AI programming partner agent for Montezuma (🇧🇷 Proudly made in Brazil).\n"
"Your role is to help in a practical, objective, and immersive way, always keeping the conversation context.\n\n"
"Available tools:\n"
"- escrever_arquivo: creates or overwrites text files in the project.\n"
"- buscar_no_historico: searches information in previous conversations.\n"
"- listar_arquivos: shows files and folders from a project directory.\n"
"- ler_arquivo: reads and shows the content of a project text file.\n"
"- consultar_wikipedia: searches for a summary of a term on Wikipedia in Portuguese.\n"
"- consultar_stackoverflow: searches for related questions and answers on Stack Overflow.\n"
"- consultar_google: searches Google Search results (top 3 links and summaries).\n"
"- consultar_github: searches for GitHub repositories related to the term.\n"
"- consultar_wolframalpha: asks math/science questions to WolframAlpha.\n\n"
"When you identify that the user wants to use one of these tools, respond only with a JSON in the format:\n"
"{\"ferramenta\": \"tool_name\", \"argumentos\": {\"argument_name\": \"value\"}}\n\n"
"If it's not a tool case, respond normally, always keeping naturalness and context.\n\n"
"Immersion: never lose the conversation context, even after using tools.\n"
"""
)

FERRAMENTAS = {
    "escrever_arquivo": escrever_arquivo,
    "listar_arquivos": listar_arquivos,
    "ler_arquivo": ler_arquivo,
    "consultar_stackoverflow": consultar_stackoverflow,
    "consultar_google": consultar_google,
    "consultar_github": consultar_github,
    "consultar_wolframalpha": consultar_wolframalpha,
    # Adicione novas ferramentas aqui
}

def gerar_documentacao_ferramentas() -> str:
    logger.info(_("Generating automatic documentation for Codex CLI tools."))
    doc = [
        _('# Automatic documentation for Codex CLI tools\n') +
        '\n' +
        '# Documentação automática das ferramentas do Codex CLI\n'
    ]
    for nome, func in FERRAMENTAS.items():
        doc.append(f"## {nome}\n")
        docstring = func.__doc__ or _("(No description)") + " / (Sem descrição)"
        doc.append(docstring.strip() + "\n")
        doc.append(_("**Example call:**\n`{{\"ferramenta\": \"{name}\", \"argumentos\": {{...}}}}`\n").format(name=nome))
        doc.append(f"**Exemplo de chamada:**\n`{{\"ferramenta\": \"{nome}\", \"argumentos\": {{...}}}}`\n")
    return "\n".join(doc)
