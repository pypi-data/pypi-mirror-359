# kfp_doctor/config_generator.py
"""
Configuration generator for creating optimal kfp-doctor configurations.
"""

import yaml
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ConfigTemplate:
    """Configuration template for different environments."""
    name: str
    description: str
    checks: Dict[str, Any]
    settings: Dict[str, Any]

class ConfigGenerator:
    """Generate optimal configurations for different use cases."""
    
    def __init__(self):
        self.templates = {
            "development": ConfigTemplate(
                name="Development Environment",
                description="Relaxed settings for development pipelines",
                checks={
                    "MISSING_RESOURCES": {"enabled": True, "severity": "WARNING"},
                    "LATEST_IMAGE_TAG": {"enabled": True, "severity": "WARNING"},
                    "NO_RETRY_POLICY": {"enabled": True, "severity": "WARNING"},
                    "PRIVILEGED_CONTAINER": {"enabled": True, "severity": "WARNING"},
                    "RUN_AS_ROOT": {"enabled": False, "severity": "WARNING"},
                    "HARDCODED_SECRET": {"enabled": True, "severity": "WARNING"},
                    "UNUSED_COMPONENT": {"enabled": True, "severity": "WARNING"},
                    "EXCESSIVE_RESOURCES": {
                        "enabled": True, 
                        "severity": "WARNING",
                        "max_cpu": "16",
                        "max_memory": "32Gi"
                    },
                    "MISSING_LIMITS": {"enabled": False, "severity": "WARNING"},
                    "INSECURE_IMAGE_REGISTRY": {"enabled": False, "severity": "WARNING"}
                },
                settings={
                    "fail_on_error": False,
                    "auto_backup": True
                }
            ),
            "staging": ConfigTemplate(
                name="Staging Environment",
                description="Balanced settings for staging pipelines",
                checks={
                    "MISSING_RESOURCES": {"enabled": True, "severity": "ERROR"},
                    "LATEST_IMAGE_TAG": {"enabled": True, "severity": "ERROR"},
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
                    "INSECURE_IMAGE_REGISTRY": {"enabled": False, "severity": "WARNING"}
                },
                settings={
                    "fail_on_error": True,
                    "auto_backup": True
                }
            ),
            "production": ConfigTemplate(
                name="Production Environment",
                description="Strict settings for production pipelines",
                checks={
                    "MISSING_RESOURCES": {"enabled": True, "severity": "ERROR"},
                    "LATEST_IMAGE_TAG": {"enabled": True, "severity": "ERROR"},
                    "NO_RETRY_POLICY": {"enabled": True, "severity": "ERROR"},
                    "PRIVILEGED_CONTAINER": {"enabled": True, "severity": "ERROR"},
                    "RUN_AS_ROOT": {"enabled": True, "severity": "ERROR"},
                    "HARDCODED_SECRET": {"enabled": True, "severity": "ERROR"},
                    "UNUSED_COMPONENT": {"enabled": True, "severity": "ERROR"},
                    "EXCESSIVE_RESOURCES": {
                        "enabled": True, 
                        "severity": "ERROR",
                        "max_cpu": "4",
                        "max_memory": "8Gi"
                    },
                    "MISSING_LIMITS": {"enabled": True, "severity": "ERROR"},
                    "INSECURE_IMAGE_REGISTRY": {
                        "enabled": True, 
                        "severity": "ERROR",
                        "allowed_registries": [
                            "gcr.io/your-project",
                            "us-central1-docker.pkg.dev/your-project",
                            "docker.io/library"
                        ]
                    }
                },
                settings={
                    "fail_on_error": True,
                    "auto_backup": True
                }
            ),
            "security-focused": ConfigTemplate(
                name="Security-Focused",
                description="Maximum security settings",
                checks={
                    "MISSING_RESOURCES": {"enabled": True, "severity": "ERROR"},
                    "LATEST_IMAGE_TAG": {"enabled": True, "severity": "ERROR"},
                    "NO_RETRY_POLICY": {"enabled": True, "severity": "WARNING"},
                    "PRIVILEGED_CONTAINER": {"enabled": True, "severity": "ERROR"},
                    "RUN_AS_ROOT": {"enabled": True, "severity": "ERROR"},
                    "HARDCODED_SECRET": {"enabled": True, "severity": "ERROR"},
                    "UNUSED_COMPONENT": {"enabled": True, "severity": "WARNING"},
                    "EXCESSIVE_RESOURCES": {
                        "enabled": True, 
                        "severity": "WARNING",
                        "max_cpu": "2",
                        "max_memory": "4Gi"
                    },
                    "MISSING_LIMITS": {"enabled": True, "severity": "ERROR"},
                    "INSECURE_IMAGE_REGISTRY": {
                        "enabled": True, 
                        "severity": "ERROR",
                        "allowed_registries": [
                            "gcr.io/your-secure-project"
                        ]
                    }
                },
                settings={
                    "fail_on_error": True,
                    "auto_backup": True
                }
            ),
            "cost-optimized": ConfigTemplate(
                name="Cost-Optimized",
                description="Focus on resource efficiency and cost reduction",
                checks={
                    "MISSING_RESOURCES": {"enabled": True, "severity": "ERROR"},
                    "LATEST_IMAGE_TAG": {"enabled": True, "severity": "WARNING"},
                    "NO_RETRY_POLICY": {"enabled": True, "severity": "WARNING"},
                    "PRIVILEGED_CONTAINER": {"enabled": True, "severity": "WARNING"},
                    "RUN_AS_ROOT": {"enabled": True, "severity": "WARNING"},
                    "HARDCODED_SECRET": {"enabled": True, "severity": "WARNING"},
                    "UNUSED_COMPONENT": {"enabled": True, "severity": "ERROR"},
                    "EXCESSIVE_RESOURCES": {
                        "enabled": True, 
                        "severity": "ERROR",
                        "max_cpu": "1",
                        "max_memory": "2Gi"
                    },
                    "MISSING_LIMITS": {"enabled": True, "severity": "ERROR"},
                    "INSECURE_IMAGE_REGISTRY": {"enabled": False, "severity": "WARNING"}
                },
                settings={
                    "fail_on_error": True,
                    "auto_backup": True
                }
            )
        }
    
    def generate_config(self, template_name: str, custom_overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate configuration based on template and overrides."""
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(self.templates.keys())}")
        
        template = self.templates[template_name]
        config = {
            "# Configuration generated by kfp-doctor": None,
            "# Template": template.name,
            "# Description": template.description,
            "checks": template.checks.copy()
        }
        
        # Apply custom overrides
        if custom_overrides:
            for key, value in custom_overrides.items():
                if key in config["checks"]:
                    if isinstance(value, dict):
                        config["checks"][key].update(value)
                    else:
                        config["checks"][key] = value
                else:
                    config[key] = value
        
        return config
    
    def analyze_pipeline_for_config(self, components: List[Dict], issues: List[Dict]) -> Dict[str, Any]:
        """Analyze a pipeline and suggest optimal configuration settings."""
        suggestions = {
            "recommended_template": "staging",
            "custom_overrides": {},
            "reasoning": []
        }
        
        # Analyze component complexity
        if len(components) > 10:
            suggestions["recommended_template"] = "production"
            suggestions["reasoning"].append("Large pipeline (>10 components) suggests production-grade requirements")
        
        # Analyze resource usage
        high_resource_components = 0
        for component in components:
            resources = component.get("container", {}).get("resources", {})
            requests = resources.get("requests", {})
            
            cpu_request = requests.get("cpu", "")
            memory_request = requests.get("memory", "")
            
            # Simple heuristic for high resource usage
            if ("4" in cpu_request or "8" in cpu_request) or ("8Gi" in memory_request or "16Gi" in memory_request):
                high_resource_components += 1
        
        if high_resource_components > len(components) * 0.3:  # More than 30% are high-resource
            suggestions["custom_overrides"]["EXCESSIVE_RESOURCES"] = {
                "max_cpu": "16",
                "max_memory": "32Gi"
            }
            suggestions["reasoning"].append("High resource usage detected - relaxed resource limits recommended")
        
        # Analyze security issues
        security_issues = [i for i in issues if i["severity"] == "ERROR" and 
                          any(sec_word in i["message"].lower() for sec_word in ["privileged", "root", "secret"])]
        
        if len(security_issues) > 2:
            suggestions["recommended_template"] = "security-focused"
            suggestions["reasoning"].append("Multiple security issues found - security-focused template recommended")
        
        # Check for cost-related issues
        resource_issues = [i for i in issues if "resource" in i["message"].lower()]
        if len(resource_issues) > len(components) * 0.5:  # More than 50% have resource issues
            suggestions["recommended_template"] = "cost-optimized"
            suggestions["reasoning"].append("Many resource-related issues - cost optimization recommended")
        
        return suggestions
    
    def get_available_templates(self) -> Dict[str, str]:
        """Get list of available templates with descriptions."""
        return {name: template.description for name, template in self.templates.items()}
    
    def save_config(self, config: Dict[str, Any], filepath: str):
        """Save configuration to file."""
        # Remove comment keys for actual YAML output
        clean_config = {k: v for k, v in config.items() if not k.startswith("#")}
        
        # Add header comment
        header = f"""# kfp-doctor configuration file
# Generated on: {yaml.dump({'timestamp': 'auto-generated'}).split(':')[1].strip()}
# Template: {config.get('# Template', 'custom')}
# Description: {config.get('# Description', 'Custom configuration')}

"""
        
        with open(filepath, "w") as f:
            f.write(header)
            yaml.dump(clean_config, f, default_flow_style=False, sort_keys=False)

def generate_optimal_config(components: List[Dict], issues: List[Dict], template_name: str = None) -> tuple:
    """
    Generate an optimal configuration based on pipeline analysis.
    
    Returns:
        tuple: (config_dict, suggestions_dict)
    """
    generator = ConfigGenerator()
    
    # Get suggestions based on analysis
    suggestions = generator.analyze_pipeline_for_config(components, issues)
    
    # Use provided template or recommended one
    final_template = template_name or suggestions["recommended_template"]
    
    # Generate config with suggested overrides
    config = generator.generate_config(final_template, suggestions["custom_overrides"])
    
    return config, suggestions 