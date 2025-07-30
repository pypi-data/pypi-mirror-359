"""
Core module for Codex CLI: constants, tool registry, and utilities.
"""
from .integrations.wikipedia import consultar_wikipedia
from .integrations.stackoverflow import consultar_stackoverflow
from .integrations.google import consultar_google
from .integrations.github import consultar_github
from .integrations.wolframalpha import consultar_wolframalpha
from .database import buscar_no_historico
from typing import Any, Optional, Union
import pathlib
import os
import logging
from .log_config import setup_logging
from .locales.i18n import _

# Global logging configuration
setup_logging()

logger = logging.getLogger("codex.cli_core")

def escrever_arquivo(nome_do_arquivo: str, conteudo: str) -> str:
    """Create or overwrite a text file in the project.
    
    Args:
        nome_do_arquivo: Name of the file to create/write
        conteudo: Content to write to the file
        
    Returns:
        A status message indicating success or error
    """
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

def listar_arquivos(caminho: str = ".", **kwargs: Any) -> str:
    """List files and folders in a project directory.
    
    Args:
        caminho: Path to the directory to list (default: current directory)
        
    Returns:
        A string with the list of files and folders, or error message
    """
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

def ler_arquivo(nome_do_arquivo: str, **kwargs: Any) -> str:
    """Read and display the content of a text file from the project.
    
    Args:
        nome_do_arquivo: Name of the file to read
        
    Returns:
        The file content or error message
    """
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

import sys

def checar_api_key():
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        print(_("CRITICAL ERROR: API key not found. Please set GOOGLE_API_KEY environment variable."))
        sys.exit(1)
    return API_KEY

PROMPT_MESTRA = _(
    """
You are Codex, an AI programming partner agent for Montezuma (🇧🇷 Proudly made in Brazil).
Your role is to help in a practical, objective, and immersive way, always keeping the conversation context.

You have access to several tools through the official Gemini Function Calling system:
- escrever_arquivo: creates or overwrites text files in the project
- buscar_no_historico: searches information in previous conversations  
- listar_arquivos: shows files and folders from a project directory
- ler_arquivo: reads and shows the content of a project text file
- consultar_wikipedia: searches for a summary of a term on Wikipedia in Portuguese
- consultar_stackoverflow: searches for related questions and answers on Stack Overflow
- consultar_google: searches Google Search results (top 3 links and summaries)
- consultar_github: searches for GitHub repositories related to the term
- consultar_wolframalpha: asks math/science questions to WolframAlpha

When the user requests something that requires using one of these tools, call the appropriate function.
For general conversation, respond naturally without using tools.

Always maintain context and provide helpful, natural responses in Portuguese.
"""
)

FERRAMENTAS = {
    "escrever_arquivo": escrever_arquivo,
    "listar_arquivos": listar_arquivos,
    "ler_arquivo": ler_arquivo,
    "buscar_no_historico": buscar_no_historico,
    "consultar_stackoverflow": consultar_stackoverflow,
    "consultar_google": consultar_google,
    "consultar_github": consultar_github,
    "consultar_wolframalpha": consultar_wolframalpha,
    "consultar_wikipedia": consultar_wikipedia,  # Adicionado para garantir execução
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
