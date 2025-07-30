from typing import Any, Dict, Optional
import requests
import logging
from codex.log_config import setup_logging
from ..locales.i18n import _

setup_logging()

logger = logging.getLogger("codex.wikipedia")

def consultar_wikipedia(termo: str, **kwargs: Any) -> str:
    """Search a term on Wikipedia and return the summary.
    
    Args:
        termo: The term to search for on Wikipedia
        
    Returns:
        Wikipedia summary or error message
    """
    if not termo or not isinstance(termo, str) or not termo.strip():
        logger.warning(_("No term provided for search."))
        return _("[ERROR]: No term provided for search.")
    url: str = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{termo.replace(' ', '_')}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 404:
            logger.info(_("Not found on Wikipedia: '{term}'").format(term=termo))
            return _("[INFO]: Not found on Wikipedia: '{term}'").format(term=termo)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        resumo: Optional[str] = data.get("extract")
        if not resumo:
            logger.info(_("No summary available for '{term}'").format(term=termo))
            return _("[INFO]: No summary available for '{term}'").format(term=termo)
        if len(resumo) > 1500:
            logger.info(_("Summary too long for '{term}', truncating.").format(term=termo))
            return _("[INFO]: Summary too long, showing the first 1500 characters:\n{summary}...").format(summary=resumo[:1500])
        logger.debug(_("Summary returned for '{term}': {snippet}...").format(term=termo, snippet=resumo[:100]))
        return _("Wikipedia – {term}:\n{summary}").format(term=termo, summary=resumo)
    except requests.exceptions.Timeout:
        logger.error(_("Timeout while querying Wikipedia."))
        return _("[TOOL ERROR]: Timeout while querying Wikipedia. Please try again later.")
    except Exception as e:
        logger.error(_("Error querying Wikipedia: {err}").format(err=e))
        return _("[TOOL ERROR]: {err}").format(err=e)
