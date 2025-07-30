import re

def scan_env_file(env_path):
    """
    Scan a .env file for sensitive keys and return them as a dictionary.
    Sensitive keys include those containing SECRET, KEY, TOKEN, PASSWORD, etc.
    """
    sensitive_patterns = re.compile(r"(SECRET|KEY|TOKEN|PASSWORD|PRIVATE|API|ACCESS)", re.IGNORECASE)
    secrets = {}
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    if sensitive_patterns.search(key):
                        secrets[key.strip()] = value.strip()
        if not secrets:
            return "No sensitive keys found."
        return secrets
    except FileNotFoundError:
        return f"File not found: {env_path}"
    except Exception as e:
        return f"Error scanning file: {e}" 