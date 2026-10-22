# Set up the BESD MCP server with your AI assistant

The **Building Energy Standards Data (BESD) MCP server** lets an AI assistant look up
prescriptive building energy code requirements (lighting power densities, ventilation rates,
HVAC equipment efficiencies, envelope U-factors and more) from ASHRAE 90.1, ASHRAE 62.1,
ASHRAE 189.1 and IECC, instead of answering from memory.

You do not need to install or configure anything yourself. Your AI assistant does it.

## What you need

- An AI coding assistant that can run commands on your computer and supports MCP servers:
  **Claude Code**, **GitHub Copilot in VS Code**, or **OpenAI Codex CLI**. Others work if they
  support MCP over stdio.
- An internet connection for the setup. The server itself needs no account, API key or
  network access once it is installed.

## How to use this file

1. Open your AI assistant. For Claude Code or Codex, open a terminal and start it. For Copilot,
   open VS Code and switch Copilot Chat to **Agent** mode.
2. Copy the prompt below and paste it into the assistant.
3. Answer its questions and approve the commands it asks to run.

```text
Set up the Building Energy Standards Data (BESD) MCP server for me. Follow the section
"Instructions for the AI assistant" in this file:
https://raw.githubusercontent.com/pnnl/building-energy-standards-data/develop/SETUP-WITH-AI.md
If you cannot open links, tell me and I will paste the file's contents instead.
Work step by step, tell me what you are about to change, and ask me before you install
software or edit any configuration file.
```

## What will happen

The assistant will, with your approval:

1. Check whether [uv](https://docs.astral.sh/uv/) is installed, and install it if not. `uv`
   runs the server in its own isolated environment, so nothing is added to your system Python.
2. Download the `building-energy-standards-data` package from PyPI.
3. Build a local copy of the database (about 10 MB) in your user cache folder,
   `~/.cache/building_energy_standards_data/` (`%USERPROFILE%\.cache\...` on Windows).
4. Add one entry named `besd` to your assistant's MCP configuration.
5. Restart or reload the assistant, and test the connection with a sample question.

It does not modify any of your other MCP servers or settings.

## After setup

Ask code questions in plain language, for example:

- "What is the lighting power density for an open office in ASHRAE 90.1-2019?"
- "What is the minimum efficiency for an air-cooled chiller under 150 tons in 90.1-2022?"
- "What is the maximum roof U-factor for climate zone 5 in IECC 2021?"

To remove it later, ask your assistant to "remove the `besd` MCP server", or see the
[removal](#removal) commands at the end.

---

# Instructions for the AI assistant

*Humans can stop reading here.* Everything below is written for the AI assistant that is
setting this up.

## Ground rules

- Explain each step in one or two sentences before you do it. The user may not be technical.
- **Ask before** installing software (including `uv`) and **before** editing any configuration
  file. Show the exact change first.
- Change only what is listed here. Add a single server entry named `besd`. Do not modify,
  reorder or delete other servers or settings. If an entry named `besd` already exists, show it
  to the user and ask whether to replace it.
- When editing an existing JSON or TOML file, read it first, make a backup copy next to it
  (for example `config.toml.bak`), and merge your entry in. Never overwrite the whole file.
- The server needs **no API keys, accounts or secrets**. Do not ask for any and do not write
  any into configuration.
- Use the **stdio** transport only (the default). Do not start the server on a network port.
- If a step fails, show the user the exact error and use the troubleshooting section. Do not
  work around a failure by using broader permissions, `sudo`, or by disabling security
  features. If you are blocked, stop and tell the user what you were trying to do.

## The server command

Every client runs this same command:

```text
uvx --from "building-energy-standards-data[mcp]" besd-mcp
```

- Command: `uvx`
- Arguments: `--from`, `building-energy-standards-data[mcp]`, `besd-mcp`
- Supports Python 3.10 to 3.13. `uv` downloads a suitable Python itself if needed, so the
  user does not need to manage Python.

## Step 1: Identify the assistant and the operating system

Work out which assistant you are (Claude Code, GitHub Copilot in VS Code, or OpenAI Codex CLI)
and the operating system (macOS, Linux or Windows). Ask the user only if you cannot tell.
If the assistant is none of these, use the command above with that client's documented way of
adding a local stdio MCP server.

## Step 2: Make sure `uv` is installed

Run `uvx --version`. If it prints a version, go to step 3.

If it is missing, tell the user you need to install `uv`, get their approval, then install it:

- macOS or Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Alternatives: `brew install uv` (macOS), `winget install --id=astral-sh.uv -e` (Windows)

Then open a new shell, or follow the installer's printed instructions to update `PATH`, and run
`uvx --version` again. Note the full path from `which uvx` (macOS or Linux) or `where uvx`
(Windows). You may need it in step 5.

## Step 3: Pre-download and pre-build

The first start downloads dependencies and builds the local database. Doing that now keeps the
assistant's first connection from timing out. Run:

```text
uvx --from "building-energy-standards-data[mcp]" python -c "from building_energy_standards_data.applications.ai_agent.mcps.database import ensure_database; print(ensure_database())"
```

It prints the path of the database file (about 10 MB). This can take a minute on the first run
and is near-instant afterwards. If the user sets the `BESD_DB_PATH` environment variable, that
path is used instead of the default cache folder.

## Step 4: Check the command works

Run `uvx --from "building-energy-standards-data[mcp]" besd-mcp --help`. It should print a
usage message that starts with `usage: besd-mcp`. Do not leave the server running.

## Step 5: Register the server

Show the user the exact command or file change, get approval, then apply the section for your
assistant.

### Claude Code

```text
claude mcp add --scope user besd -- uvx --from "building-energy-standards-data[mcp]" besd-mcp
```

`--scope user` makes it available in all projects. Use `--scope project` instead if the user
wants it for the current project only (this writes `.mcp.json`, which can be committed). Verify
with `claude mcp list`: `besd` should be listed as connected.

### OpenAI Codex CLI

Edit `~/.codex/config.toml` (create it if it does not exist) and add:

```toml
[mcp_servers.besd]
command = "uvx"
args = ["--from", "building-energy-standards-data[mcp]", "besd-mcp"]
startup_timeout_sec = 60
```

The longer `startup_timeout_sec` matters, because Codex's default is 10 seconds. If a
`[mcp_servers.besd]` table already exists, ask before changing it. Verify with `codex mcp list`
or the `/mcp` command inside Codex.

### GitHub Copilot in VS Code

Use a workspace file `.vscode/mcp.json`, or the user-level file opened by the VS Code command
**MCP: Open User Configuration**. If the file exists, merge the entry into its `servers` object:

```json
{
  "servers": {
    "besd": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "building-energy-standards-data[mcp]", "besd-mcp"]
    }
  }
}
```

Then tell the user to open Copilot Chat in **Agent** mode, run **MCP: List Servers**, and start
`besd` if it is not already running. If their organization restricts MCP servers through a
Copilot policy, the server will not appear. In that case tell the user to ask their
administrator.

## Step 6: Reload and test

Some assistants only pick up new servers after a restart. Tell the user to restart or reload
the assistant if the server is not listed, and wait for them to confirm.

Then test with the BESD tools. You should see these six: `list_tables`,
`list_tables_with_descriptions`, `get_candidate_tables`, `get_table_metadata`,
`get_unique_values` and `run_sql`. Call `list_tables`. It should report **122 tables** (the
count may grow in later releases). Then answer this question using the tools:

> What is the lighting power density for an open office in ASHRAE 90.1-2019?

The expected workflow is `get_candidate_tables` (this should rank `level_3_lighting_90_1_2019`
first), then `get_table_metadata`, then `run_sql`. Report the value you found and the table it
came from.

## Step 7: Report back

Tell the user, briefly:

- which assistant you configured, and which file you changed (or which command you ran);
- that the test question worked, with the answer you got;
- that the database is cached at the path from step 3;
- that the server runs on demand when the assistant starts, and is not a background service;
- how to remove it (see below).

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `uvx: command not found` in the assistant, but it works in a terminal | The assistant was launched without your shell's `PATH` (common for VS Code opened from the Dock or Start menu). Use the **full path** to `uvx` from step 2 as the `command` value, or restart the assistant from a terminal. |
| The server times out or shows as failed on first start | The first start downloads and builds. Re-run step 3 and then reload. In Codex, confirm `startup_timeout_sec = 60`. |
| `No solution found when resolving` or "requires a different Python" | The system Python is outside 3.10 to 3.13. Add `--python 3.12` to the `uvx` arguments, right after `uvx`, and let `uv` download it. |
| The tools appear but answers are empty or wrong | The cached database may be stale or corrupt. Delete the `.db` file whose path step 3 printed (ask the user first). It is rebuilt on the next start, so re-run step 3 and reload. |
| Corporate network blocks the download | PyPI (`pypi.org`, `files.pythonhosted.org`) must be reachable. Ask the user to use their organization's PyPI mirror through `UV_INDEX_URL`. |
| Copilot does not list the server | Check that Agent mode is on, the file is valid JSON, and no organization policy blocks MCP. |

## Removal

- Claude Code: `claude mcp remove besd`
- Codex: delete the `[mcp_servers.besd]` table from `~/.codex/config.toml`
- Copilot in VS Code: delete the `besd` entry from `mcp.json`
- Optional: delete the cached database in `~/.cache/building_energy_standards_data/` and run
  `uv cache clean building-energy-standards-data` to free the downloaded package.
