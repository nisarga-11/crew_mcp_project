# mcp_server_base.py
from flask import Flask, request, jsonify
import threading
import time


class MCPServer:
    def __init__(self, agent, host="127.0.0.1", port=5000):
        self.agent = agent
        self.host = host
        self.port = port
        self.app = Flask(f"MCPServer-{agent.name}")
        self._setup_routes()
        self._server_thread = threading.Thread(target=self.run, daemon=True)

    def _setup_routes(self):
        @self.app.route("/execute", methods=["POST"])
        def execute():
            data = request.json
            action = data.get("action")
            backup_name = data.get("backup_name")

            if action == "backup":
                result = self.agent.perform_backup()
            elif action == "list":
                result = self.agent.list_backups()
            elif action == "restore":
                if not backup_name:
                    return jsonify({"error": "backup_name required"}), 400
                result = self.agent.perform_restore(backup_name)
            else:
                return jsonify({"error": f"Unknown action '{action}'"}), 400

            print(f"[{self.agent.name}] Action '{action}' result: {result}")
            return jsonify({"result": result})

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

    def start(self):
        print(f"[{self.agent.name}] Starting MCPServer on {self.host}:{self.port}")
        self._server_thread.start()
        time.sleep(1)  # wait for server to start
