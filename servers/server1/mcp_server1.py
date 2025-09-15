# servers/server1/mcp_server1.py
from mcp_server_base import MCPServer
from agents.backup_restore_agent1 import BackupRestoreAgent1

# Configuration for server1
STANZA = "db1"
agent1 = BackupRestoreAgent1(name="agent1", stanza=STANZA)

mcp_server1 = MCPServer(agent=agent1, host="127.0.0.1", port=5001)

if __name__ == "__main__":
    mcp_server1.start()
    print("[MCPServer1] Running... Press Ctrl+C to exit.")
    while True:
        pass  # keep the main thread alive
