# Plan: baseui-mcp

**Date:** 2026-03-20
**Design doc:** docs/mastercoder/specs/2026-03-20-baseui-mcp-design.md
**Status:** In Progress

## Tasks

- id: T01
  title: Adapt update_components.py for BaseUI
  description: Modify the script to fetch from BaseUI llms.txt, parse sections correctly, generate both .md files and components_index.json with structured metadata
  files:
    - update_components.py
    - components_index.json (generated)
  depends_on: []
  imports: []
  exports:
    - components_index.json (generated)
  verify: Script runs without errors and generates components_index.json with 40+ components

- id: T02
  title: Run update_components.py to fetch BaseUI components
  description: Execute the script to download all BaseUI components and generate the component documentation files
  files:
    - components/*.md (all component files)
    - components_index.json
  depends_on: [T01]
  imports:
    - update_components.py
  exports:
    - components/*.md
    - components_index.json
  verify: 40+ .md files exist in components/ directory

- id: T03
  title: Modernize mcp_server.py for BaseUI
  description: Rename server to "BaseUI MCP Server", load components_index.json, add search_components and get_component_api tools, maintain list_components and get_component
  files:
    - mcp_server.py
  depends_on: [T02]
  imports:
    - components_index.json
  exports:
    - mcp_server.py (updated)
  verify: Server has 4 tools: list_components, get_component, search_components, get_component_api

- id: T04
  title: Update README.md
  description: Rewrite README to document BaseUI MCP Server purpose, tools, installation, Docker configuration
  files:
    - README.md
  depends_on: [T03]
  imports: []
  exports:
    - README.md (updated)
  verify: README contains no DaisyUI references, documents all 4 MCP tools

- id: T05
  title: Update Dockerfile and docker-compose.yml
  description: Update image names and configurations to reference baseui-mcp instead of daisyui-mcp
  files:
    - Dockerfile
    - docker-compose.yml
  depends_on: [T04]
  imports: []
  exports:
    - Dockerfile (updated)
    - docker-compose.yml (updated)
  verify: Files reference baseui-mcp not daisyui-mcp

- id: T06
  title: Verify and commit changes
  description: Run tests if available, verify all files are correct, commit to worktree
  files:
    - All files
  depends_on: [T05]
  imports:
    - All modified files
  exports: []
  verify: git log shows commit with all changes

## Execution order

Layer 1 (sequential): T01 → T02
Layer 2 (sequential): T03
Layer 3 (sequential): T04 → T05
Layer 4 (sequential): T06

## Notes

- Tasks are mostly sequential because each builds on the previous
- T01 and T02 must run in order (script must exist before running it)
- T03 depends on T02 because it needs the generated components_index.json
- The update_components.py script parsing may need adjustment based on actual BaseUI llms.txt format
