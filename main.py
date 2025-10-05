import requests
import os

# MCP server URLs
MCP1_URL = "http://localhost:5001/execute"
MCP2_URL = "http://localhost:5002/execute"


def send_request(mcp_url, action, backup_name=""):
    """Send a POST request to an MCP server."""
    payload = {"action": action}
    if backup_name:
        payload["backup_name"] = backup_name
    try:
        response = requests.post(mcp_url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Server returned status {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def main_orchestrator():
    print("🚀 Main Orchestrator running. Available commands: backup, restore, list, exit")

    while True:
        command = input("Enter command: ").strip().lower()
        if command == "exit":
            print("Exiting orchestrator...")
            break
        elif command == "backup":
            print("Triggering backup on both agents...")
            res1 = send_request(MCP1_URL, "backup")
            res2 = send_request(MCP2_URL, "backup")
            print(f"Agent1: {res1.get('backup', res1.get('error'))}")
            print(f"Agent2: {res2.get('backup', res2.get('error'))}")

        elif command == "list":
            print("Listing all backups from both agents...")
            res1 = send_request(MCP1_URL, "list")
            res2 = send_request(MCP2_URL, "list")
            print(f"Agent1 backups: {res1.get('backups', res1.get('error'))}")
            print(f"Agent2 backups: {res2.get('backups', res2.get('error'))}")

        elif command.startswith("restore"):
            parts = command.split()
            if len(parts) != 3:
                print("Usage: restore <agent1|agent2> <backup_name>")
                continue
            agent, backup_name = parts[1], parts[2]
            if agent == "agent1":
                res = send_request(MCP1_URL, "restore", backup_name)
                print(res.get("restore", res.get("error")))
            elif agent == "agent2":
                res = send_request(MCP2_URL, "restore", backup_name)
                print(res.get("restore", res.get("error")))
            else:
                print("Invalid agent. Choose 'agent1' or 'agent2'.")

        else:
            print("Unknown command. Available commands: backup, restore, list, exit")
