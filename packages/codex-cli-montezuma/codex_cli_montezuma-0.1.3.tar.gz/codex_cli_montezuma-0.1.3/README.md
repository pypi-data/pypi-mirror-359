# Codex CLI: Seu Assistente de IA e Automação no Terminal

[![PyPI](https://img.shields.io/pypi/v/codex-cli-montezuma)](https://pypi.org/project/codex-cli-montezuma/)

**Codex CLI** é uma poderosa ferramenta de linha de comando projetada para desenvolvedores, engenheiros de dados e entusiastas de automação. Integre a inteligência artificial do Google Gemini diretamente no seu fluxo de trabalho, automatize tarefas repetitivas e consulte uma variedade de fontes de informação sem sair do terminal.

Com uma arquitetura extensível e foco na produtividade, o Codex CLI armazena seu histórico de interações, permite a busca por conversas passadas e oferece um conjunto de ferramentas integradas para interagir com seu sistema de arquivos e APIs externas.

---

## 🌐 Documentação Completa (Multilíngue)

Para uma experiência completa, incluindo guias de instalação, configuração de API e tutoriais detalhados, por favor, selecione seu idioma:

- 🇧🇷 [**Documentação em Português**](docs/pt/README.md)
- 🇺🇸 [**Documentation in English**](docs/en/README.md)

---

## Instalação Rápida

```bash
pip install codex-cli-montezuma
```

## Configuração Rápida de API Keys

Para usar todas as funcionalidades do Codex CLI, configure suas chaves de API:

```bash
# Configuração automática (recomendado)
./scripts/setup-api-keys.sh

# Ou configure manualmente:
export GOOGLE_API_KEY="sua_chave_aqui"
export GOOGLE_SEARCH_CX="seu_search_engine_id_aqui"
```

> 📚 **Guia completo**: [docs/pt/configuracao-api-keys.md](docs/pt/configuracao-api-keys.md)

---

## Funcionalidades Principais

- **Inteligência Artificial Integrada:** Converse com o modelo de linguagem **Google Gemini** para gerar código, obter explicações, traduzir textos e muito mais.
- **Histórico de Conversas:** Todas as suas interações são salvas localmente em um banco de dados SQLite, permitindo que você revise e busque por informações importantes a qualquer momento.
- **Sistema de Ferramentas Extensível:**
  - `escrever_arquivo`: Crie ou modifique arquivos no seu projeto.
  - `listar_arquivos`: Navegue pela estrutura de diretórios.
  - `ler_arquivo`: Leia o conteúdo de arquivos de texto.
  - `consultar_wikipedia`: Obtenha resumos rápidos da Wikipedia.
  - `consultar_stackoverflow`: Encontre soluções para problemas de programação.
  - `consultar_google`: Realize buscas na web.
  - E muito mais!
- **Suporte Multilíngue:** A interface e a documentação estão disponíveis em Português e Inglês.
- **Automação de Tarefas:** Use o Codex para automatizar scripts, gerar relatórios e interagir com seu ambiente de desenvolvimento.

---

## Logging Estruturado e Depuração

O Codex CLI utiliza logging estruturado e configurável em todos os módulos, facilitando depuração, auditoria e integração com ferramentas externas.

- O logging é centralizado em `src/log_config.py`.
- Por padrão, logs são enviados para o console, mas você pode configurar para arquivo ou outros destinos.
- Níveis suportados: DEBUG, INFO, WARNING, ERROR, CRITICAL.
- Todos os módulos usam `logger = logging.getLogger("codex.nome_do_modulo")` para rastreabilidade.

**Como customizar o logging:**

```python
from src.log_config import setup_logging
setup_logging(level="DEBUG", log_file="codex.log")
```

Ou defina variáveis de ambiente para ajustar o nível globalmente.

---

## Arquitetura e Boas Práticas
- Código modularizado em `src/` (core, integrações, sugestões, banco, etc).
- Todas as funções principais usam type hints e docstrings.
- Logging estruturado em todos os fluxos.
- Testes automatizados com pytest e mocks para integrações externas.
- Automação de build, testes e limpeza via Makefile e scripts.
- Extensibilidade planejada via sistema de plugins (em desenvolvimento).

---

## Para Desenvolvedores
- Siga o padrão de logging e type hints em todo novo código.
- Consulte `src/log_config.py` para configurar logs.
- Veja exemplos de testes e patches em `tests/` e `docs/guia_didatico/como_escrever_testes.md`.
- Documentação de cada ferramenta é gerada automaticamente em `docs/guia_didatico/auto_documentacao_ferramentas.md`.
- Para criar novas integrações, siga o padrão de `src/integrations/` e registre no dicionário `FERRAMENTAS`.

---

## Publicação no PyPI e Uso como API

Veja o guia completo em [`docs/publicacao_pypi_api.md`](docs/publicacao_pypi_api.md).

### Resumo rápido:

**Publicar no PyPI:**
```bash
pip install build twine
python -m build
# Para o PyPI oficial:
twine upload dist/*
# Para o TestPyPI:
twine upload --repository testpypi dist/*
```

**Expor como API (FastAPI):**
```python
from fastapi import FastAPI, Request
from codex.cli_agent import main as codex_main

app = FastAPI()

@app.post("/codex/")
async def codex_endpoint(request: Request):
    data = await request.json()
    resposta = codex_main(**data)
    return {"resposta": resposta}
```

Veja detalhes, exemplos e links oficiais no guia acima.

---

## Sumário das Mudanças Recentes (2025)

- **Modularização total:** Código reorganizado em `src/` com separação clara de integrações, core, sugestões e banco.
- **Type hints e docstrings:** Todo o código principal agora segue tipagem estática e documentação de funções.
- **Logging estruturado:** Todos os módulos usam logging centralizado e configurável via `src/log_config.py`.
- **Testes automatizados:** Cobertura total com pytest, incluindo mocks para integrações externas.
- **Automação:** Makefile e scripts para build, testes, limpeza e geração de documentação.
- **Extensibilidade:** Estrutura pronta para plugins e novas integrações.
- **Documentação didática:** Todos os guias, exemplos e auto-documentação atualizados.
- **Personalização dinâmica:** Respostas do agente adaptam tom, exemplos e dicas conforme perfil do usuário.
- **CLI aprimorado:** Sugestões inteligentes, exportação de histórico, relatórios e perfil do usuário.

Consulte o diário de bordo (`docs/diario_de_bordo.md`) para histórico detalhado e decisões de arquitetura.

---

## Privacidade e Histórico

- O histórico de conversas do Codex CLI é salvo **localmente** no arquivo `memoria_codex.db` na pasta onde o comando é executado.
- **Apenas quem tem acesso ao arquivo .db pode ver o histórico.**
- O histórico **não é enviado para a internet** nem compartilhado entre usuários diferentes, a menos que o arquivo seja copiado manualmente.
- Para resetar seu histórico, basta apagar o arquivo `memoria_codex.db`.
- Em ambientes multiusuário, recomenda-se rodar o CLI em pastas separadas para cada usuário.

> Para planos de segurança avançada (criptografia, proteção por senha, etc), consulte o roadmap ou entre em contato com o mantenedor.

---

Projeto didático, aberto a sugestões e contribuições!

## Licença
MIT License. Consulte o arquivo `LICENSE` para mais detalhes.
