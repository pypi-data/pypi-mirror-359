from typing import Any, Optional
import os
import requests
import logging
from urllib.parse import quote
from codex.log_config import setup_logging

setup_logging()

logger = logging.getLogger("codex.wolframalpha")

def consultar_wolframalpha(termo: str, **kwargs: Any) -> str:
    """Query WolframAlpha for mathematical, scientific or general questions.
    
    Args:
        termo: The question or term to query WolframAlpha
        
    Returns:
        WolframAlpha answer or error message
    """
    appid: Optional[str] = os.getenv("WOLFRAMALPHA_APPID")
    if not termo or not isinstance(termo, str) or not termo.strip():
        logger.warning("Nenhum termo informado para consulta.")
        return "[ERRO]: Nenhum termo informado para consulta."
    if not appid:
        logger.error("WOLFRAMALPHA_APPID não configurado.")
        return "[ERRO]: Para usar WolframAlpha, configure a variável WOLFRAMALPHA_APPID. Obtenha em: https://products.wolframalpha.com/api/"
    url: str = f"https://api.wolframalpha.com/v1/result?i={quote(termo)}&appid={appid}"
    try:
        resp = requests.get(url, timeout=7)
        if resp.status_code == 501:
            logger.info(f"WolframAlpha não sabe responder a '{termo}'.")
            return f"[INFO]: WolframAlpha não sabe responder a '{termo}'."
        resp.raise_for_status()
        resposta: str = resp.text
        if len(resposta) > 1200:
            logger.info(f"Resposta muito grande para '{termo}', truncando.")
            resposta = resposta[:1200] + '...'
        logger.debug(f"Resposta WolframAlpha para '{termo}': {resposta[:100]}...")
        return f"WolframAlpha – Resposta para '{termo}':\n{resposta}"
    except requests.exceptions.Timeout:
        logger.error("Timeout ao consultar o WolframAlpha.")
        return "[ERRO DA FERRAMENTA]: Timeout ao consultar o WolframAlpha. Tente novamente mais tarde."
    except Exception as e:
        logger.error(f"Erro ao consultar WolframAlpha: {e}")
        return f"[ERRO DA FERRAMENTA]: {e}"
