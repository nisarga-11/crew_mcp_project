# run_project.py
import threading
import time
import requests
from servers.server1.mcp_server1 import MCPServer, STANZA as STANZA1
from servers.server2.mcp_server2 import MCPServer, STANZA as STANZA2

from agents.backup_restore_agent1 import BackupRestoreAgent1
from agents.backup_restore_agent2 import BackupRestoreAgent2

# ----------------------------
# MCP Server Initialization
# ----------------------------
AGENT1_PORT = 5001
AGENT2_PORT = 5002
SERVER_HOST = "localhost"

# Create agents
agent1 = BackupRestoreAgent1(name="agent1", stanza=STANZA1)
agent2 = BackupRestoreAgent2(name="agent2", stanza=STANZA2)

# Create MCP servers
mcp_server1 = MCPServer(agent=agent1, host=SERVER_HOST, port=AGENT1_PORT)
mcp_server2 = MCPServer(agent=agent2, host=SERVER_HOST, port=AGENT2_PORT)

# ----------------------------
# Start servers in separate threads
# ----------------------------
def start_mcp_server(server):
    thread = threading.Thread(target=server.start)
    thread.daemon = True
    thread.start()
    time.sleep(2)  # Slight delay to ensure server starts

print("Starting MCP servers...")
start_mcp_server(mcp_server1)
start_mcp_server(mcp_server2)
print("All MCP servers started.\n")

# ----------------------------
# Simple CLI Orchestrator
# ----------------------------
def orchestrator():
    print("🚀 Main Orchestrator running. Available commands: backup, restore, list, exit")
    while True:
        cmd = input("Enter command: ").strip().lower()
        if cmd == "exit":
            print("Exiting orchestrator...")
            break

        if cmd.startswith("backup"):
            # Backup both agents
            for port, agent_name in [(AGENT1_PORT, "agent1"), (AGENT2_PORT, "agent2")]:
                try:
                    response = requests.post(
                        f"http://{SERVER_HOST}:{port}/execute",
                        json={"action": "backup"}
                    )
                    print(f"[{agent_name}] {response.json().get('result')}")
                except Exception as e:
                    print(f"[{agent_name}] Backup failed: {e}")

        elif cmd.startswith("list"):
            # List backups for both agents
            for port, agent_name in [(AGENT1_PORT, "agent1"), (AGENT2_PORT, "agent2")]:
                try:
                    response = requests.post(
                        f"http://{SERVER_HOST}:{port}/execute",
                        json={"action": "list"}
                    )
                    print(f"[{agent_name}] Backups: {response.json().get('result')}")
                except Exception as e:
                    print(f"[{agent_name}] List failed: {e}")

        elif cmd.startswith("restore"):
            # Command format: restore agent1 <backup_name>
            parts = cmd.split()
            if len(parts) >= 3:
                target_agent = parts[1]
                backup_name = " ".join(parts[2:])  # allow backup names with spaces
                port = AGENT1_PORT if target_agent == "agent1" else AGENT2_PORT
                try:
                    response = requests.post(
                        f"http://{SERVER_HOST}:{port}/execute",
                        json={"action": "restore", "backup_name": backup_name}
                    )
                    print(f"[{target_agent}] {response.json().get('result')}")
                except Exception as e:
                    print(f"[{target_agent}] Restore failed: {e}")
            else:
                print("Invalid restore command. Usage: restore agent1 <backup_name>")

        else:
            print("Unknown command. Use backup, restore, list, exit.")

# Start orchestrator
orchestrator()
