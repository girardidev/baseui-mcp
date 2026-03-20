# BaseUI MCP Server

**Date:** 2026-03-20
**Status:** Draft

## Context

Este projeto foi clonado do repositório "DaisyUI MCP Server" e está sendo adaptado para servir documentação do **BaseUI** em vez do DaisyUI. O BaseUI é uma biblioteca de componentes React (não CSS classes), então o formato da documentação e a arquitetura do servidor MCP precisam ser diferentes do original.

O objetivo é criar um servidor MCP que forneça ferramentas ricas para que IAs possam consultar e utilizar componentes BaseUI de forma eficiente.

## Requirements

1. **Renomear servidor** de "DaisyUI MCP Server" para "BaseUI MCP Server"
2. **Adaptar update_components.py** para buscar do llms.txt do BaseUI (`https://base-ui.com/llms.txt`)
3. **Manter formato similar** ao DaisyUI: extrair seções de componentes em arquivos .md individuais
4. **Gerar components_index.json** com metadados estruturados (props, variantes, etc.)
5. **Modernizar mcp_server.py** com ferramentas MCP mais ricas:
   - `list_components()` - lista componentes com descrições
   - `get_component(name)` - documentação completa do componente
   - `search_components(query)` - busca por componentes por props/funcionalidade
   - `get_component_api(name)` - retorna API de props do componente
6. **Atualizar README.md** para refletir o novo propósito
7. **Atualizar Dockerfile** e docker-compose.yml se necessário
8. **Suportar ~40+ componentes** do BaseUI

## Assumptions

- O formato do llms.txt do BaseUI segue a mesma estrutura (headers `### Component`) que o DaisyUI
- Os componentes serão salvos em `/components/` como Markdown
- O servidor usa FastMCP como framework MCP
- Não há necessidade de autenticação ou configuração complexa

## Chosen approach

### Arquitetura API-driven (Solução 3)

A abordagem escolhida implica em:

1. **Script de update aprimorado**: `update_components.py` vai buscar o llms.txt do BaseUI, extrair cada seção de componente e salvar em `.md`, além de gerar um `components_index.json` com metadados estruturados

2. **MCP Server rico**: O servidor vai expor não apenas `list_components` e `get_component`, mas também `search_components` (para buscar componentes por funcionalidade) e `get_component_api` (para ver props disponíveis)

3. **Index JSON**: Um arquivo `components_index.json` será gerado com estrutura:
```json
{
  "components": {
    "button": {
      "name": "Button",
      "description": "A high-quality, unstyled React button component...",
      "url": "https://base-ui.com/react/components/button.md",
      "props": ["focusableWhenDisabled", "nativeButton", "className", "style", "render"],
      "dataAttributes": ["data-disabled"]
    }
  }
}
```

**Por que esta abordagem:** Permite um MCP mais inteligente que pode fazer buscas semânticas e fornecer informações detalhadas de API, diferenciando este servidor de implementações mais simples.

## Implementation plan (high level)

1. **Adaptar update_components.py**
   - Mudar URL de fetch para base-ui.com/llms.txt
   - Adaptar parsing para novo formato
   - Gerar both .md files AND components_index.json

2. **Modernizar mcp_server.py**
   - Renomear para "BaseUI MCP Server"
   - Carregar components_index.json
   - Adicionar ferramentas: search_components, get_component_api
   - Manter list_components e get_component

3. **Executar update_components.py**
   - Baixar todos os componentes do BaseUI
   - Gerar index JSON

4. **Atualizar README.md**
   - Documentar novo propósito e ferramentas
   - Remover referências ao DaisyUI

5. **Atualizar arquivos de suporte**
   - Dockerfile (se necessário renomear imagem)
   - docker-compose.yml
   - requirements.txt (manter fastmcp)

6. **Commit e revisão**

## Open questions

- O BaseUI usa `### Component` ou outro header no llms.txt? (Assumido: similar ao DaisyUI com `### Component`)
- Devemos manter compatibilidade com o formato DaisyUI nos .md ou criar formato novo? (Decisão: manter formato similar)

## Out of scope

- Não vamos modificar a estrutura de diretórios drasticamente
- Não vamos adicionar autenticação ou configuração complexa
- Não vamos criar um servidor HTTP separado (usa FastMCP diretamente)
- Não vamos suportar outras bibliotecas de componentes além do BaseUI
