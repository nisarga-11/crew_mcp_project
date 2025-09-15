# agents/backup_restore_agent1.py
from .backup_restore_base import BackupRestoreBaseAgent
from pydantic import Field
from datetime import datetime
import os

BACKUP_ROOT = os.path.join(os.getcwd(), "backups")

class BackupRestoreAgent1(BackupRestoreBaseAgent):
    agent_backup_dir: str = Field(default_factory=lambda: os.path.join(BACKUP_ROOT, "agent1"))

    def __post_init_post_parse__(self):
        os.makedirs(self.agent_backup_dir, exist_ok=True)

    def perform_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.stanza}_backup_{timestamp}"
        backup_path = os.path.join(self.agent_backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)
        with open(os.path.join(backup_path, "backup.txt"), "w") as f:
            f.write(f"Backup for {self.stanza} completed at {timestamp}\n")
        print(f"[{self.name}] Backup completed: {backup_name}")
        return backup_name

    def list_backups(self):
        if not os.path.exists(self.agent_backup_dir):
            return ["No backups found"]
        backups = [
            name for name in sorted(os.listdir(self.agent_backup_dir))
            if os.path.isdir(os.path.join(self.agent_backup_dir, name))
        ]
        return backups if backups else ["No backups found"]

    def perform_restore(self, backup_name: str):
        backup_path = os.path.join(self.agent_backup_dir, backup_name)
        if not os.path.exists(backup_path):
            return f"Backup '{backup_name}' not found"
        print(f"[{self.name}] Restoring backup: {backup_name}")
        return f"Restore completed from {backup_name}"
