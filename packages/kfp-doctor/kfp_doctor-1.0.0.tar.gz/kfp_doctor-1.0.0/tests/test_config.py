import pytest
import tempfile
import yaml
import os
from kfp_doctor.config import load_config, DEFAULT_CONFIG

class TestKfpDoctorConfig:
    def test_default_config_loading(self):
        """Test loading default config when no .kfp-doctor.yaml exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = load_config(temp_dir)
            
            assert config == DEFAULT_CONFIG
            assert "checks" in config
            assert "MISSING_RESOURCES" in config["checks"]
            assert config["checks"]["MISSING_RESOURCES"]["enabled"] is True

    def test_custom_config_loading(self):
        """Test loading and merging custom configuration."""
        custom_config = {
            "checks": {
                "MISSING_RESOURCES": {"enabled": False},
                "LATEST_IMAGE_TAG": {"severity": "ERROR"}
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, ".kfp-doctor.yaml")
            with open(config_file, "w") as f:
                yaml.dump(custom_config, f)
            
            config = load_config(temp_dir)
            
            # Check that custom settings override defaults
            assert config["checks"]["MISSING_RESOURCES"]["enabled"] is False
            assert config["checks"]["LATEST_IMAGE_TAG"]["severity"] == "ERROR"
            
            # Check that non-overridden settings remain default
            assert config["checks"]["PRIVILEGED_CONTAINER"]["enabled"] is True

    def test_partial_config_override(self):
        """Test that partial configuration overrides work correctly."""
        custom_config = {
            "checks": {
                "EXCESSIVE_RESOURCES": {
                    "max_cpu": "4",
                    "max_memory": "8Gi"
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, ".kfp-doctor.yaml")
            with open(config_file, "w") as f:
                yaml.dump(custom_config, f)
            
            config = load_config(temp_dir)
            
            # Check that custom values are applied
            assert config["checks"]["EXCESSIVE_RESOURCES"]["max_cpu"] == "4"
            assert config["checks"]["EXCESSIVE_RESOURCES"]["max_memory"] == "8Gi"
            
            # Check that other properties remain default
            assert config["checks"]["EXCESSIVE_RESOURCES"]["enabled"] is True
            assert config["checks"]["EXCESSIVE_RESOURCES"]["severity"] == "WARNING"

    def test_invalid_yaml_config(self):
        """Test handling of invalid YAML in config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, ".kfp-doctor.yaml")
            with open(config_file, "w") as f:
                f.write("invalid: yaml: content: [unclosed")
            
            config = load_config(temp_dir)
            
            # Should fall back to default config
            assert config == DEFAULT_CONFIG

    def test_empty_config_file(self):
        """Test handling of empty config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, ".kfp-doctor.yaml")
            with open(config_file, "w") as f:
                f.write("")
            
            config = load_config(temp_dir)
            
            # Should fall back to default config
            assert config == DEFAULT_CONFIG

    def test_custom_check_addition(self):
        """Test adding custom checks via configuration."""
        custom_config = {
            "checks": {
                "CUSTOM_CHECK": {
                    "enabled": True,
                    "severity": "WARNING",
                    "custom_param": "value"
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, ".kfp-doctor.yaml")
            with open(config_file, "w") as f:
                yaml.dump(custom_config, f)
            
            config = load_config(temp_dir)
            
            # Check that custom check is added
            assert "CUSTOM_CHECK" in config["checks"]
            assert config["checks"]["CUSTOM_CHECK"]["enabled"] is True
            assert config["checks"]["CUSTOM_CHECK"]["custom_param"] == "value"

    def test_registry_configuration(self):
        """Test configuration of allowed registries."""
        custom_config = {
            "checks": {
                "INSECURE_IMAGE_REGISTRY": {
                    "enabled": True,
                    "allowed_registries": [
                        "my-registry.com",
                        "trusted-registry.io"
                    ]
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, ".kfp-doctor.yaml")
            with open(config_file, "w") as f:
                yaml.dump(custom_config, f)
            
            config = load_config(temp_dir)
            
            allowed_registries = config["checks"]["INSECURE_IMAGE_REGISTRY"]["allowed_registries"]
            assert "my-registry.com" in allowed_registries
            assert "trusted-registry.io" in allowed_registries

    def test_resource_limits_configuration(self):
        """Test configuration of resource limits."""
        custom_config = {
            "checks": {
                "EXCESSIVE_RESOURCES": {
                    "max_cpu": "16",
                    "max_memory": "32Gi"
                }
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, ".kfp-doctor.yaml")
            with open(config_file, "w") as f:
                yaml.dump(custom_config, f)
            
            config = load_config(temp_dir)
            
            assert config["checks"]["EXCESSIVE_RESOURCES"]["max_cpu"] == "16"
            assert config["checks"]["EXCESSIVE_RESOURCES"]["max_memory"] == "32Gi"

    def test_severity_levels(self):
        """Test configuration of different severity levels."""
        custom_config = {
            "checks": {
                "MISSING_RESOURCES": {"severity": "WARNING"},
                "LATEST_IMAGE_TAG": {"severity": "ERROR"},
                "RUN_AS_ROOT": {"severity": "INFO"}
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, ".kfp-doctor.yaml")
            with open(config_file, "w") as f:
                yaml.dump(custom_config, f)
            
            config = load_config(temp_dir)
            
            assert config["checks"]["MISSING_RESOURCES"]["severity"] == "WARNING"
            assert config["checks"]["LATEST_IMAGE_TAG"]["severity"] == "ERROR"
            assert config["checks"]["RUN_AS_ROOT"]["severity"] == "INFO"

    def test_disable_all_checks(self):
        """Test disabling all checks."""
        custom_config = {
            "checks": {
                check_name: {"enabled": False} 
                for check_name in DEFAULT_CONFIG["checks"].keys()
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, ".kfp-doctor.yaml")
            with open(config_file, "w") as f:
                yaml.dump(custom_config, f)
            
            config = load_config(temp_dir)
            
            for check_name, check_config in config["checks"].items():
                assert check_config["enabled"] is False

if __name__ == "__main__":
    pytest.main([__file__]) 