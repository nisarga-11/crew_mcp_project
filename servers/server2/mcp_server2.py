from mcp_server_base import MCPServer
from agents.backup_restore_agent2 import BackupRestoreAgent2

agent2 = BackupRestoreAgent2()

mcp_server2 = MCPServer(
    name="agent2",
    agent=agent2,
    host="127.0.0.1",
    port=5002
)

if __name__ == "__main__":
    mcp_server2.start()
    print("[MCPServer2] Running... Press Ctrl+C to exit.")
    while True:
        pass