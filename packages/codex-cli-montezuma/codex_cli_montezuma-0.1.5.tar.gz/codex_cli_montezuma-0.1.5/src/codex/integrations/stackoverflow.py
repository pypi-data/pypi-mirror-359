from typing import Any, Dict, Optional
import requests
import re
import logging
from codex.log_config import setup_logging
from ..locales.i18n import _

setup_logging()

logger = logging.getLogger("codex.stackoverflow")

def consultar_stackoverflow(termo: str, **kwargs: Any) -> str:
    """Search Stack Overflow for questions and answers related to a term.
    
    Args:
        termo: The term to search for on Stack Overflow
        
    Returns:
        Stack Overflow results with titles, links, and answers
    """
    if not termo or not isinstance(termo, str) or not termo.strip():
        logger.warning("Nenhum termo informado para busca.")
        return "[ERRO]: Nenhum termo informado para busca."
    url: str = (
        f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={termo}&site=stackoverflow&filter=!9_bDDxJY5"
    )
    try:
        resp = requests.get(url, timeout=7)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        if not data.get("items"):
            logger.info("Nenhuma pergunta encontrada para '{term}' no Stack Overflow.".format(term=termo))
            return "[INFO]: Nenhuma pergunta encontrada para '{term}' no Stack Overflow.".format(term=termo)
        pergunta: Dict[str, Any] = data["items"][0]
        titulo: Optional[str] = pergunta.get("title")
        link: Optional[str] = pergunta.get("link")
        id_pergunta: Optional[Any] = pergunta.get("question_id")
        url_respostas: str = f"https://api.stackexchange.com/2.3/questions/{id_pergunta}/answers?order=desc&sort=votes&site=stackoverflow&filter=withbody"
        try:
            resp2 = requests.get(url_respostas, timeout=7)
            resp2.raise_for_status()
            respostas: Any = resp2.json().get("items", [])
            if respostas:
                resposta: Optional[str] = respostas[0].get("body", _("[No answer]"))
                resposta_limpa: str = re.sub(r'<.*?>', '', resposta or "")
                if len(resposta_limpa) > 1200:
                    resposta_limpa = resposta_limpa[:1200] + '...'
            else:
                resposta_limpa = _("[No answer available]")
        except requests.exceptions.Timeout:
            logger.error(_("Timeout while fetching answer from Stack Overflow."))
            resposta_limpa = _("[TOOL ERROR]: Timeout while fetching answer from Stack Overflow.")
        except Exception as e:
            logger.error(_("Error fetching answer from Stack Overflow: {err}").format(err=e))
            resposta_limpa = _("[TOOL ERROR]: {err}").format(err=e)
        logger.debug(f"Pergunta: {titulo}, Link: {link}, Resposta: {resposta_limpa[:100]}...")
        return f"Stack Overflow – {titulo}\n{link}\nResposta mais votada:\n{resposta_limpa}"
    except requests.exceptions.Timeout:
        logger.error("Timeout ao consultar o Stack Overflow.")
        return "[ERRO DA FERRAMENTA]: Timeout ao consultar o Stack Overflow. Tente novamente mais tarde."
    except Exception as e:
        logger.error(f"Erro ao consultar Stack Overflow: {e}")
        return f"[ERRO DA FERRAMENTA]: {e}"
