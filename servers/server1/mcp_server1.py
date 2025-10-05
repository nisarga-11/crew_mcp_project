from mcp_server_base import MCPServer
from agents.backup_restore_agent1 import BackupRestoreAgent1

agent1 = BackupRestoreAgent1()

mcp_server1 = MCPServer(
    name="agent1",
    agent=agent1,
    host="127.0.0.1",
    port=5001
)

if __name__ == "__main__":
    mcp_server1.start()
    print("[MCPServer1] Running... Press Ctrl+C to exit.")
    while True:
        pass