import gettext
import os

# Caminho para os arquivos de tradução (.mo)
LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
DEFAULT_LANG = os.getenv('CODEX_LANG', 'pt_BR')

# Inicializa o gettext
try:
    t = gettext.translation('messages', LOCALE_DIR, languages=[DEFAULT_LANG])
    _ = t.gettext
except FileNotFoundError:
    _ = lambda s: s  # fallback: retorna a string original

# Uso: from locales.i18n import _
# print(_('Mensagem traduzível'))
