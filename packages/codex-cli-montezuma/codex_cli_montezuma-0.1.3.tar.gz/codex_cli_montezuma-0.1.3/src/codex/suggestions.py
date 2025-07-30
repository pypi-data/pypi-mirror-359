from typing import Any, List, Optional
import datetime
import logging
from . import database
from .log_config import setup_logging
from .locales.i18n import _

# Global logging configuration
setup_logging()

logger = logging.getLogger("codex.suggestions")

def sugerir_pergunta_frequente(session: Any) -> Optional[str]:
    """
    Suggests to the user one of the most frequent questions/commands from history.
    """
    sugestoes: List[str] = database.perguntas_mais_frequentes(session, limite=1)
    logger.debug(_("Most frequent questions suggested: {sug}." ).format(sug=sugestoes))
    if sugestoes:
        return sugestoes[0]
    return None

def sugerir_pergunta_contextual(session: Any) -> List[str]:
    """
    Suggests a frequent question/command to the user, considering recent context and time of day.
    """
    frequentes: List[str] = database.perguntas_mais_frequentes(session, limite=3)
    hora: int = datetime.datetime.now().hour
    if hora < 12:
        sugestao_horario: str = _("Would you like to review tasks or seek inspiration to start your day?")
    elif hora < 18:
        sugestao_horario = _("Need help solving a bug or searching for a solution?")
    else:
        sugestao_horario = _("How about generating a productivity report or reviewing what was done today?")
    historico: List[Any] = database.carregar_historico(session, n_mensagens=5)
    temas_recentes: set = set()
    for msg in historico:
        if hasattr(msg, 'role') and msg.role == 'user' and hasattr(msg, 'content'):
            temas_recentes.update(str(msg.content).lower().split())
    sugestao_contexto: Optional[str] = None
    if 'bug' in temas_recentes or 'erro' in temas_recentes:
        sugestao_contexto = _("It seems you are facing a problem. Would you like to search Stack Overflow?")
    elif 'documentação' in temas_recentes or 'documentacao' in temas_recentes:
        sugestao_contexto = _("Need to generate or consult documentation for a tool?")
    logger.debug(_("Frequent: {freq}, Hour: {hour}, Recent topics: {topics}, Context suggestion: {ctx}").format(freq=frequentes, hour=hora, topics=temas_recentes, ctx=sugestao_contexto))
    sugestoes: List[str] = []
    if frequentes:
        sugestoes.append(_("Frequent question: '{q}'").format(q=frequentes[0]))
    sugestoes.append(sugestao_horario)
    if sugestao_contexto:
        sugestoes.append(sugestao_contexto)
    return sugestoes

def buscar_contexto_relevante(session: Any, pergunta_usuario: str, n: int = 5) -> List[str]:
    """
    Busca as últimas interações relevantes do histórico para compor o contexto da resposta.
    """
    historico: List[Any] = database.carregar_historico(session, n_mensagens=50)
    contexto: List[str] = []
    for msg in reversed(historico):
        if len(contexto) >= n:
            break
        if hasattr(msg, 'role') and hasattr(msg, 'content') and msg.role in ("user", "model"):
            contexto.append(f"- {msg.role}: {msg.content}")
    logger.debug(f"Contexto relevante retornado: {contexto}")
    return list(reversed(contexto))
