# KRIYEX

KRIYEX is a local-first AI desktop operating assistant built with Python and PySide6.
This initial release establishes a production-oriented foundation: a desktop chat shell,
SQLite-backed conversation persistence, an auditable permission model, and a declarative
tool registry. High-impact actions and provider integrations are intentionally not
implemented until their approval and security boundaries are designed.

## Run

```powershell
uv run kriyex
```

Or, after installing the package:

```powershell
kriyex
```

Local app data is stored in `~/.kriyex/kriyex.db`.

## Current scope

- Local chat history with streaming responses from a locally running Ollama model
- Declarative tool metadata with safety levels and permissions
- Persisted permission decisions and a SQLite audit-ready schema
- PySide6 desktop shell with Chat, Memory, Tools, Security, and Settings navigation
- Persistent task plans created with `/plan <your goal>`
- Approval gate and audit trail for tool requests
- Consent-based long-term memory with local management and export controls

## Next modules

Additional model providers, task planning, memory controls, tool execution approvals,
encrypted secrets, and automation adapters.
