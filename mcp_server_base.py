import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

class MCPServer:
    def __init__(self, name, agent, host="127.0.0.1", port=5000):
        self.name = name
        self.agent = agent
        self.host = host
        self.port = port
        self.server = HTTPServer((self.host, self.port), self._make_handler())
        self.thread = None

    def _make_handler(self):
        agent = self.agent

        class RequestHandler(BaseHTTPRequestHandler):
            def _set_headers(self):
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()

            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                data = self.rfile.read(length).decode("utf-8")
                try:
                    payload = json.loads(data)
                except Exception as e:
                    self._set_headers()
                    self.wfile.write(json.dumps({"error": f"Invalid JSON: {e}"}).encode())
                    return

                results = {}

                # --- Batch request ---
                if "actions" in payload and isinstance(payload["actions"], list):
                    for i, action_item in enumerate(payload["actions"]):
                        results[f"task_{i+1}"] = self._execute_action(agent, action_item)
                else:
                    # --- Single request ---
                    results = self._execute_action(agent, payload)

                self._set_headers()
                self.wfile.write(json.dumps({"result": results}).encode())

            def log_message(self, format, *args):
                # silence default HTTP logs
                return

            def _execute_action(self, agent, payload):
                action = payload.get("action")
                if not action:
                    return "⚠️ No action provided"

                db_name = payload.get("db_name")
                backup_name = payload.get("backup_name")
                backup_type = payload.get("backup_type", "full")
                recent = payload.get("recent", False)

                if action == "backup":
                    return agent.perform_backup(backup_type=backup_type, db_name=db_name)

                elif action == "list":
                    return agent.list_backups()

                elif action == "restore":
                    return agent.perform_restore(backup_name=backup_name, db_name=db_name, recent=recent)

                else:
                    return f"⚠️ Unknown action '{action}'"


        return RequestHandler

    def start(self):
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"[MCPServer:{self.name}] Listening on {self.host}:{self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print(f"[MCPServer:{self.name}] Stopped")