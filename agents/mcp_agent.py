import os
import argparse
from crewai import Crew, Agent, Process
from crewai_tools import Tool
from agents.backup_restore_agent import PgbackrestBackupTool, PgbackrestRestoreTool, get_backup_restore_agent

parser = argparse.ArgumentParser(description='Run a CrewAI MCP agent.')
parser.add_argument('--env_file', type=str, required=True, help='Path to the .env file for this agent.')
args = parser.parse_args()

env_vars = {}
try:
    with open(args.env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip().strip('"').strip("'")
except FileNotFoundError:
    print(f"Error: The .env file '{args.env_file}' was not found.")
    exit(1)

SERVER_HOST = env_vars.get("SERVER_HOST")
STANZA_NAME = env_vars.get("STANZA_NAME")
PG_PATH = env_vars.get("PG_PATH")
AGENT_ROLE = env_vars.get("AGENT_ROLE")
mcp_port_str = env_vars.get("MCP_PORT")

if mcp_port_str is None:
    print("ERROR: MCP_PORT is not set in the .env file. Please check the file.")
    exit()

MCP_PORT = int(mcp_port_str)

def backup_wrapper(type: str = 'incremental'):
    return PgbackrestBackupTool()._run(host=SERVER_HOST, stanza=STANZA_NAME, type=type)

def restore_wrapper(set_id: str, pg_path: str):
    return PgbackrestRestoreTool()._run(host=SERVER_HOST, stanza=STANZA_NAME, set_id=set_id, pg_path=pg_path)

backup_tool = Tool(
    name=f"Backup Tool for {STANZA_NAME}",
    func=backup_wrapper,
    description=f"Performs a pgbackrest backup for the '{STANZA_NAME}' stanza on {SERVER_HOST}."
)

restore_tool = Tool(
    name=f"Restore Tool for {STANZA_NAME}",
    func=restore_wrapper,
    description=f"Restores a pgbackrest backup for the '{STANZA_NAME}' stanza on {SERVER_HOST}."
)

agent = get_backup_restore_agent(AGENT_ROLE, SERVER_HOST, [backup_tool, restore_tool])

crew = Crew(
    agents=[agent],
    tasks=[],
    process=Process.sequential
)

crew.mcp_host(
    host="0.0.0.0",
    port=MCP_PORT
)