from typing import Any, Dict, List, Optional
import os
import requests
import logging
from codex.log_config import setup_logging

setup_logging()

logger = logging.getLogger("codex.github")

def consultar_github(termo: str, **kwargs: Any) -> str:
    """Search GitHub repositories related to a term.
    
    Args:
        termo: The term to search for on GitHub
        
    Returns:
        GitHub repository results with names, links and descriptions
    """
    if not termo or not isinstance(termo, str) or not termo.strip():
        logger.warning("Nenhum termo informado para consulta.")
        return "[ERRO]: Nenhum termo informado para consulta."
    url: str = f"https://api.github.com/search/repositories?q={termo}&sort=stars&order=desc&per_page=3"
    headers: Dict[str, str] = {"Accept": "application/vnd.github+json"}
    token: Optional[str] = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        logger.info("GITHUB_TOKEN não configurado - usando limite público da API.")
    try:
        resp = requests.get(url, headers=headers, timeout=7)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        items: List[Dict[str, Any]] = data.get("items", [])
        if not items:
            logger.info(f"Nenhum repositório encontrado para '{termo}' no GitHub.")
            return f"[INFO]: Nenhum repositório encontrado para '{termo}' no GitHub."
        resultados: List[str] = []
        for item in items:
            nome: Optional[str] = item.get("full_name", "[Sem nome]")
            link: Optional[str] = item.get("html_url", "[Sem link]")
            desc: Optional[str] = item.get("description", "[Sem descrição]")
            desc_str: str = desc if desc is not None else ""
            if desc_str and len(desc_str) > 300:
                desc_str = desc_str[:300] + '...'
            resultados.append(f"- {nome}\n{link}\n{desc_str}")
        logger.debug(f"Resultados GitHub para '{termo}': {resultados}")
        return f"GitHub – Repositórios para '{termo}':\n" + "\n\n".join(resultados)
    except requests.exceptions.Timeout:
        logger.error("Timeout ao consultar o GitHub.")
        return "[ERRO DA FERRAMENTA]: Timeout ao consultar o GitHub. Tente novamente mais tarde."
    except Exception as e:
        logger.error(f"Erro ao consultar GitHub: {e}")
        return f"[ERRO DA FERRAMENTA]: {e}"
