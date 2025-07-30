# database.py - AI memory management module

from typing import Any, List, Optional, Dict
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import TYPE_CHECKING
import logging
from .log_config import setup_logging
from .locales.i18n import _

# Global logging configuration
setup_logging()

# Added 'check_same_thread=False' for Flask compatibility
DATABASE_URL = "sqlite:///memoria_codex.db?check_same_thread=False" 
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

logger = logging.getLogger("codex.database")

if TYPE_CHECKING:
    class ConversaBase:
        id: int
        timestamp: datetime.datetime
        role: str
        content: str
else:
    ConversaBase = object

class Conversa(Base):  # type: ignore[misc,valid-type]
    __tablename__ = 'conversas'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    role = Column(String(50))
    content = Column(Text)

def criar_banco_e_tabelas() -> None:
    logger.info(_("Creating database and tables if needed..."))
    Base.metadata.create_all(bind=engine)
    logger.info(_("Database and tables ready."))

def carregar_historico(db_session: Any, n_mensagens: int = 50) -> List[Conversa]:
    historico = db_session.query(Conversa).order_by(Conversa.id.desc()).limit(n_mensagens).all()
    logger.debug(_("History loaded: {n} messages.").format(n=len(historico)))
    return list(reversed(historico))

def buscar_no_historico(termo: str, **kwargs: Any) -> str:
    """Search for information in previous conversations.
    
    Args:
        termo: The term to search for in conversation history
        
    Returns:
        Search results from conversation history
    """
    logger.info(_("Buscando no histórico por termo: '{term}'...").format(term=termo))
    db_session = kwargs.get('db_session')
    if not db_session:
        # Try to create a session if not provided
        try:
            db_session = Session()
            should_close = True
        except Exception as e:
            logger.error(f"Could not create database session: {e}")
            return _("[ERROR]: Database session not available.")
    else:
        should_close = False
    
    try:
        termo_para_busca = f"%{termo}%"
        resultados = db_session.query(Conversa).filter(Conversa.content.like(termo_para_busca)).all()
        logger.info(_("{n} resultados encontrados para '{term}'.").format(n=len(resultados), term=termo))
        
        if not resultados:
            return _("[INFO]: No results found for '{term}' in conversation history.").format(term=termo)
        
        output = [_("Search results for '{term}':").format(term=termo)]
        for resultado in resultados[:5]:  # Limite a 5 resultados
            output.append(f"- {resultado.content[:100]}...")
        
        return "\n".join(output)
    except Exception as e:
        logger.error(f"Error searching history: {e}")
        return _("[ERROR]: Error searching conversation history.")
    finally:
        if should_close and db_session:
            db_session.close()

def perguntas_mais_frequentes(db_session: Any, limite: int = 3) -> List[str]:
    """
    Retorna as perguntas/comandos mais frequentes do usuário no histórico.
    """
    from sqlalchemy import func
    resultados = (
        db_session.query(Conversa.content, func.count(Conversa.content).label('freq'))
        .filter(Conversa.role == 'user')
        .group_by(Conversa.content)
        .order_by(func.count(Conversa.content).desc())
        .limit(limite)
        .all()
    )
    logger.debug(f"Perguntas mais frequentes: {resultados}")
    return [r[0] for r in resultados]

def gerar_relatorio_uso(db_session: Any, n_mensagens: int = 100) -> str:
    """
    Gera um relatório automático de uso e aprendizado do Codex CLI.
    """
    from collections import Counter
    historico = db_session.query(Conversa).order_by(Conversa.id).limit(n_mensagens).all()
    total = len(historico)
    perguntas = [msg.content for msg in historico if msg.role == 'user']
    respostas = [msg.content for msg in historico if msg.role == 'model']
    horarios = [msg.timestamp.hour for msg in historico]
    palavras = []
    for p in perguntas:
        palavras.extend(p.lower().split())
    freq_perguntas = Counter(perguntas).most_common(5)
    freq_palavras = Counter(palavras).most_common(5)
    freq_horarios = Counter(horarios).most_common(3)
    relatorio = [
        f"Total de interações: {total}",
        f"Perguntas mais frequentes: {[p for p, _ in freq_perguntas]}",
        f"Palavras mais recorrentes: {[w for w, _ in freq_palavras]}",
        f"Horários de pico de uso: {[h for h, _ in freq_horarios]}",
    ]
    logger.info(f"Relatório de uso gerado para {total} interações.")
    return "\n".join(relatorio)

def exportar_historico_jsonl(db_session: Any, caminho_arquivo: str = "historico_codex.jsonl", n_mensagens: int = 1000) -> str:
    """
    Exports the interaction history (prompt/response) in JSONL format for future fine-tuning.
    Each line: {"prompt": ..., "completion": ...}
    """
    historico = db_session.query(Conversa).order_by(Conversa.id).limit(n_mensagens).all()
    pares = []
    buffer = None
    for msg in historico:
        if msg.role == 'user':
            buffer = msg.content
        elif msg.role == 'model' and buffer:
            pares.append({"prompt": buffer, "completion": msg.content})
            buffer = None
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        for par in pares:
            import json
            f.write(json.dumps(par, ensure_ascii=False) + "\n")
    logger.info(f"Exportação concluída: {len(pares)} pares salvos em {caminho_arquivo}")
    return f"Exportação concluída: {len(pares)} pares salvos em {caminho_arquivo}"

def perfil_usuario(db_session: Any, n_mensagens: int = 200) -> Dict[str, Any]:
    """
    Analyzes the history and returns a summarized user profile: themes, tone, times, etc.
    """
    from collections import Counter
    historico = db_session.query(Conversa).order_by(Conversa.id).limit(n_mensagens).all()
    perguntas = [msg.content for msg in historico if msg.role == 'user']
    palavras = []
    for p in perguntas:
        palavras.extend(p.lower().split())
    temas = Counter([w for w in palavras if len(w) > 4]).most_common(5)
    horarios = [msg.timestamp.hour for msg in historico if msg.role == 'user']
    freq_horarios = Counter(horarios).most_common(2)
    perfil = {
        "temas_mais_frequentes": [t for t, _ in temas],
        "horarios_mais_ativos": [h for h, _ in freq_horarios],
        "total_perguntas": len(perguntas)
    }
    logger.info(f"Summarized user profile generated: {perfil}")
    return perfil

if __name__ == "__main__":
    print(_("Initializing database infrastructure..."))
    criar_banco_e_tabelas()
    print(_("Memory infrastructure ready."))