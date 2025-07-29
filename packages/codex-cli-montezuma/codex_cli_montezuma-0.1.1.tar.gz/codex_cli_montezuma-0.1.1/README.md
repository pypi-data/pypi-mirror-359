# Codex CLI – Ferramentas de IA, APIs e Automação

[![PyPI](https://img.shields.io/pypi/v/codex-cli-montezuma)](https://pypi.org/project/codex-cli-montezuma/)

---

## 🌐 Documentação Multilíngue | Multilingual Documentation

> **Selecione o idioma / Select your language:**
>
> - 🇧🇷 [Documentação em Português (docs/pt/README.md)](docs/pt/README.md)
> - 🇺🇸 [Documentation in English (docs/en/README.md)](docs/en/README.md)

---

> **Índice Rápido da Documentação (PT)**
> - [Índice Visual](docs/indice_visual.md)
> - [Guia Global de Contribuição](docs/guia_contribuicao.md)
> - [Índice Geral](docs/indice_geral.md)
> - [Checklist de PR](docs/checklist_pr.md)
> - [Roadmap](docs/roadmap.md)
> - [Diário de Bordo](docs/diario_de_bordo.md)
> - [Próxima Missão](docs/proxima_missao.md)
> - [Guia de Testes](docs/guia_didatico/como_escrever_testes.md)
> - [Ferramentas Externas](docs/guia_didatico/ferramentas_externas.md)
> - [Documentação Automática](docs/guia_didatico/auto_documentacao_ferramentas.md)
> - [Leitura de Arquivos](docs/guia_didatico/ler_arquivo.md)
> - [Percepção de Arquivos](docs/guia_didatico/percepcao_arquivos.md)
> - [pytest](docs/guia_didatico/pytest.md)

> **Quick Documentation Index (EN)**
> - [Visual Index](docs/en/indice_visual.md)
> - [Global Contribution Guide](docs/en/guia_contribuicao.md)
> - [General Index](docs/en/indice_geral.md)
> - [PR Checklist](docs/en/checklist_pr.md)
> - [Roadmap](docs/en/roadmap.md)
> - [Logbook](docs/en/diario_de_bordo.md)
> - [Next Mission](docs/en/proxima_missao.md)
> - [Testing Guide](docs/en/guia_didatico/como_escrever_testes.md)
> - [External Tools](docs/en/guia_didatico/ferramentas_externas.md)
> - [Automatic Documentation](docs/en/guia_didatico/auto_documentacao_ferramentas.md)
> - [File Reading](docs/en/guia_didatico/ler_arquivo.md)
> - [File Perception](docs/en/guia_didatico/percepcao_arquivos.md)
> - [pytest](docs/en/guia_didatico/pytest.md)

---

## Instalação Rápida

```bash
pip install codex-cli-montezuma
```

Acesse o pacote no PyPI: https://pypi.org/project/codex-cli-montezuma/

> **Nota:** Para uma instalação completa com todas as dependências de desenvolvimento, use:
> 
> ```bash
> pip install -r requirements-dev.txt
> ```

## Funcionalidades Principais
- Armazena conversas e histórico em SQLite.
- Busca por palavras-chave no histórico.
- Interação com IA Gemini (Google) via CLI.
- Ferramentas integradas:
  - **escrever_arquivo**: cria/sobrescreve arquivos de texto.
  - **listar_arquivos**: lista arquivos e pastas do projeto.
  - **ler_arquivo**: lê arquivos de texto do projeto.
  - **consultar_wikipedia**: busca resumos na Wikipedia.
  - **consultar_stackoverflow**: busca perguntas e respostas técnicas.
  - **consultar_google**: retorna os 3 primeiros resultados do Google Search.
  - **consultar_github**: mostra repositórios populares sobre um termo.
  - **consultar_wolframalpha**: responde perguntas matemáticas/científicas.
- **Personalização dinâmica das respostas**: o agente adapta o tom, exemplos e dicas conforme o perfil do usuário, tornando as respostas mais relevantes e alinhadas ao seu estilo e necessidades.

## Como Usar
1. Instale as dependências:
   ```bash
   pip install -r requirements-dev.txt
   ```
2. Configure as variáveis de ambiente necessárias:
   ```bash
   export GOOGLE_API_KEY='sua-api-key-gemini'
   export GOOGLE_SEARCH_API_KEY='sua-api-key-google-search'
   export GOOGLE_SEARCH_CX='seu-cx-google-search'
   export GITHUB_TOKEN='seu-token-github'  # (opcional, para mais requisições)
   export WOLFRAMALPHA_APPID='seu-appid-wolframalpha'
   ```
3. Inicialize o banco de dados:
   ```bash
   python database.py
   ```
4. Rode o CLI:
   ```bash
   python cli_agent.py
   ```

## Exemplos de Uso
- "Codex, crie um arquivo chamado 'exemplo.txt' com o conteúdo 'olá mundo'"
- "Liste os arquivos da pasta docs"
- "Leia o arquivo README.md"
- "Pesquise no Google por 'Python asyncio'"
- "Busque repositórios sobre 'machine learning' no GitHub"
- "Qual a raiz quadrada de 144 no WolframAlpha?"
- "O que significa API segundo a Wikipedia?"
- "Como faço um request HTTP em Python? (Stack Overflow)"
- "Codex, me dê dicas personalizadas para estudar Python à noite."

Veja mais exemplos e dicas em `docs/guia_didatico/ferramentas_externas.md`.

## Personalização Dinâmica
O Codex analisa seu histórico de uso, temas frequentes, horários e preferências para adaptar:
- O tom das respostas (mais formal, objetivo, motivacional, etc.)
- Exemplos práticos alinhados ao seu perfil
- Dicas e sugestões contextuais

Você pode visualizar seu perfil com:
```bash
python cli_agent.py --perfil-usuario
```
E exportar o histórico para fine-tuning futuro:
```bash
python cli_agent.py --exportar-jsonl
```

## Roadmap
Consulte o [roadmap completo](docs/roadmap.md) para próximos passos, visão de futuro e evolução do projeto.



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
