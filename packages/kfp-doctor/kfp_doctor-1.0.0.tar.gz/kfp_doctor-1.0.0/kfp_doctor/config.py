# kfp_doctor/config.py
import os
import yaml

DEFAULT_CONFIG = {
    "checks": {
        "MISSING_RESOURCES": {"enabled": True, "severity": "ERROR"},
        "LATEST_IMAGE_TAG": {"enabled": True, "severity": "WARNING"},
        "NO_RETRY_POLICY": {"enabled": True, "severity": "WARNING"},
        "PRIVILEGED_CONTAINER": {"enabled": True, "severity": "ERROR"},
        "RUN_AS_ROOT": {"enabled": True, "severity": "WARNING"},
        "HARDCODED_SECRET": {"enabled": True, "severity": "ERROR"},
        "UNUSED_COMPONENT": {"enabled": True, "severity": "WARNING"},
        "EXCESSIVE_RESOURCES": {
            "enabled": True, 
            "severity": "WARNING",
            "max_cpu": "8",
            "max_memory": "16Gi"
        },
        "MISSING_LIMITS": {"enabled": True, "severity": "WARNING"},
        "INSECURE_IMAGE_REGISTRY": {
            "enabled": False,  # Disabled by default since it requires configuration
            "severity": "WARNING",
            "allowed_registries": [
                "gcr.io",
                "us-docker.pkg.dev",
                "docker.io"
            ]
        },
    }
}

def load_config(path: str = ".") -> dict:
    """Loads the .kfp-doctor.yaml file from the given path."""
    config_path = os.path.join(path, ".kfp-doctor.yaml")
    if not os.path.exists(config_path):
        return DEFAULT_CONFIG

    try:
        with open(config_path, "r") as f:
            user_config = yaml.safe_load(f)
    except yaml.YAMLError:
        # If the config is invalid, fall back to defaults
        return DEFAULT_CONFIG

    # Deep merge user config into defaults
    config = DEFAULT_CONFIG.copy()
    if user_config and "checks" in user_config:
        for check, settings in user_config["checks"].items():
            if check in config["checks"]:
                config["checks"][check].update(settings)
            else:
                # Allow custom checks from user config
                config["checks"][check] = settings
    
    return config
