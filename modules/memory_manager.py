import os
import json
import config
from modules.database_manager import DatabaseManager

class MemoryManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.old_memory_file = os.path.join(config.DATA_DIR, "memory.json")
        self._migrate_if_needed()

    def _migrate_if_needed(self):
        """Migrates data from memory.json to SQLite if DB is empty."""
        # check if history is empty
        history = self.db.get_history(limit=1)
        if not history and os.path.exists(self.old_memory_file):
            print("Migrating memory.json to database...")
            try:
                with open(self.old_memory_file, 'r') as f:
                    data = json.load(f)
                
                # Migrate User Profile
                user_profile = data.get("user_profile", {})
                for k, v in user_profile.items():
                    self.db.upsert_setting("user_profile", k, v)
                
                # Migrate Preferences
                preferences = data.get("preferences", {})
                for k, v in preferences.items():
                    self.db.upsert_setting("preferences", k, v)
                
                # Migrate History (preserve order)
                history = data.get("history", [])
                for item in history:
                    self.db.add_history(item.get("role"), item.get("content"))
                    
                print("Migration complete.")
                # We rename the old file to backup to avoid re-migration issues or confusion
                os.rename(self.old_memory_file, self.old_memory_file + ".bak")
                
            except Exception as e:
                print(f"Migration failed: {e}")

    def save_memory(self):
        """Deprecated: DB saves automatically."""
        pass

    def update_context(self, category, key, value):
        """Updates a specific memory context."""
        self.db.upsert_setting(category, key, value)

    def get_context(self, category, key=None):
        """Retrieves specific context."""
        if key:
            return self.db.get_setting(category, key)
        return self.db.get_all_settings(category)

    def add_history(self, role, content):
        """Adds a conversation turn to history."""
        self.db.add_history(role, content)

    def get_context_window(self, limit=5):
        """Retrieves the last 'limit' items from history formatted as text."""
        recent_history = self.db.get_history(limit=limit)
        context_str = ""
        for item in recent_history:
            role = item.get("role", "unknown").upper()
            content = item.get("content", "")
            context_str += f"{role}: {content}\n"
        return context_str

    def get_full_context_string(self):
        """Returns a string summary of user profile and preferences for the LLM."""
        profile = self.db.get_all_settings("user_profile")
        prefs = self.db.get_all_settings("preferences")
        
        context_str = "Persistent Memory Context:\n"
        if profile:
            context_str += "User Profile:\n"
            for k, v in profile.items():
                context_str += f"- {k}: {v}\n"
        
        if prefs:
            context_str += "Preferences:\n"
            for k, v in prefs.items():
                context_str += f"- {k}: {v}\n"
                
        return context_str
