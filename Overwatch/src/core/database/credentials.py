# Credential Management for Database Connections
import os
import json
from cryptography.fernet import Fernet

# It's crucial to store this key securely, e.g., in an environment variable or a secure vault in production.
# For this example, we'll generate one if not found, but this is not secure for a real application.
ENCRYPTION_KEY_ENV_VAR = "OVERWATCH_ENCRYPTION_KEY"
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "credentials.json.enc")

class CredentialManager:
    def __init__(self):
        key = os.getenv(ENCRYPTION_KEY_ENV_VAR)
        if not key:
            # This is for demonstration only. In a real app, the key must be pre-set and securely managed.
            key = Fernet.generate_key().decode()
            print(f"WARNING: No {ENCRYPTION_KEY_ENV_VAR} found. Generated a new key. THIS IS NOT SECURE FOR PRODUCTION.")
            # In a real scenario, you might want to store this key or require it to be set.
        self.cipher_suite = Fernet(key.encode())
        self._ensure_credentials_file_exists()

    def _ensure_credentials_file_exists(self):
        os.makedirs(os.path.dirname(CREDENTIALS_FILE), exist_ok=True)
        if not os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, "wb") as f:
                encrypted_data = self.cipher_suite.encrypt(json.dumps({}).encode())
                f.write(encrypted_data)

    def _load_credentials(self) -> dict:
        try:
            with open(CREDENTIALS_FILE, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Error loading or decrypting credentials: {e}")
            # Fallback to empty dict if file is corrupted or key is wrong
            return {}

    def _save_credentials(self, credentials: dict):
        try:
            encrypted_data = self.cipher_suite.encrypt(json.dumps(credentials).encode())
            with open(CREDENTIALS_FILE, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error encrypting or saving credentials: {e}")

    def add_credential(self, name: str, details: dict):
        credentials = self._load_credentials()
        credentials[name] = details
        self._save_credentials(credentials)

    def get_credential(self, name: str) -> dict | None:
        credentials = self._load_credentials()
        return credentials.get(name)

    def remove_credential(self, name: str):
        credentials = self._load_credentials()
        if name in credentials:
            del credentials[name]
            self._save_credentials(credentials)

    def list_credential_names(self) -> list[str]:
        credentials = self._load_credentials()
        return list(credentials.keys())

# Example usage (not part of the class itself)
if __name__ == "__main__":
    # This part is for testing and won't run when imported
    # For this to run, you'd need to set OVERWATCH_ENCRYPTION_KEY environment variable
    # export OVERWATCH_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    
    if not os.getenv(ENCRYPTION_KEY_ENV_VAR):
        print(f"Please set the {ENCRYPTION_KEY_ENV_VAR} environment variable to run this example.")
        print("Example: export OVERWATCH_ENCRYPTION_KEY=$(python3.11 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\")")
    else:
        manager = CredentialManager()
        manager.add_credential("my_test_db", {"host": "localhost", "user": "test_user", "password": "test_password"})
        print("Saved credentials for my_test_db")
        retrieved_creds = manager.get_credential("my_test_db")
        print(f"Retrieved: {retrieved_creds}")
        print(f"Available credentials: {manager.list_credential_names()}")
        # manager.remove_credential("my_test_db")
        # print("Removed credentials for my_test_db")

