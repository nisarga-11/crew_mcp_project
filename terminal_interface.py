import os
import sys
import signal
import requests

# MCP agent configuration for your setup
AGENTS = {
    "mydb": {"name": "agent1", "port": 5001, "stanza": "mydb_stanza"},
    "projectdb": {"name": "agent2", "port": 5002, "stanza": "projectdb_stanza"},
}


class TerminalInterface:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        print("\nShutting down gracefully...")
        self.running = False
        sys.exit(0)

    def print_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════╗
║           Postgres Backup & Restore System                   ║
║                     CrewAI MCP Edition                       ║
╚══════════════════════════════════════════════════════════════╝

Two agents are available:
- Agent 1: mydb (primary)
- Agent 2: projectdb (secondary)

Commands examples:
- "backup mydb / projectdb / both"
- "restore mydb / projectdb"
- "list backups mydb / projectdb / both"

Type 'quit' or 'exit' to close the application.
"""
        print(banner)

    def print_agent_status(self):
        print("\n" + "=" * 60)
        print("AGENT STATUS")
        print("=" * 60)
        for key, agent in AGENTS.items():
            try:
                r = requests.get(f"http://localhost:{agent['port']}/status", timeout=2).json()
                print(f"{agent['name'].capitalize()} ({key}): {r.get('agent_name', agent['name'])}")
                print(f"  Database: {r.get('stanza', agent['stanza'])}")
                print(f"  Current Task: {r.get('current_task', 'Idle')}")
            except Exception as e:
                print(f"{agent['name'].capitalize()} ({key}): Error fetching status ({e})")
            print()
        print("=" * 60)

    def parse_input(self, user_input: str):
        """Determine target agents and action from user input."""
        user_input = user_input.lower()
        targets = []

        if "mydb" in user_input or "primary" in user_input:
            targets.append("mydb")
        if "projectdb" in user_input or "secondary" in user_input:
            targets.append("projectdb")
        if "both" in user_input or "all" in user_input:
            targets = ["mydb", "projectdb"]

        action = None
        if "backup" in user_input:
            action = "backup"
        elif "restore" in user_input:
            action = "restore"
        elif "list" in user_input:
            action = "list"

        return targets, action

    def process_user_input(self, user_input: str):
        targets, action = self.parse_input(user_input)

        if not targets:
            print("Cannot determine target agent from input.")
            return
        if not action:
            print("Cannot determine action from input.")
            return

        for t in targets:
            agent = AGENTS[t]
            data = {"action": action}

            # Handle restore: fetch latest backup automatically if not specified
            if action == "restore":
                try:
                    resp = requests.post(f"http://localhost:{agent['port']}/execute", json={"action": "list"}, timeout=5)
                    backups = resp.json().get("result", [])
                    if not backups:
                        print(f"No backups found for {t}. Skipping restore.")
                        continue
                except Exception as e:
                    print(f"Error fetching backups for {t}: {e}")
                    continue

                latest_backup = sorted(backups)[-1]
                print(f"Latest backup for {t}: {latest_backup}")
                backup_name = input(f"Enter backup name to restore (press Enter to use latest): ").strip()
                if not backup_name:
                    backup_name = latest_backup

                data["backup_name"] = backup_name

            # Send command to agent
            try:
                resp = requests.post(f"http://localhost:{agent['port']}/execute", json=data, timeout=15)
                result = resp.json()
                print(f"\nResponse from {agent['name']} ({t}): {result}")
            except Exception as e:
                print(f"\nError sending command to {agent['name']} ({t}): {e}")

    def run(self):
        self.print_banner()
        self.print_agent_status()

        while self.running:
            try:
                user_input = input("\nEnter your request: ").strip()
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                if not user_input:
                    continue
                if user_input.lower() in ["status", "s"]:
                    self.print_agent_status()
                    continue

                self.process_user_input(user_input)

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit gracefully.")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")


if __name__ == "__main__":
    interface = TerminalInterface()
    interface.run()
