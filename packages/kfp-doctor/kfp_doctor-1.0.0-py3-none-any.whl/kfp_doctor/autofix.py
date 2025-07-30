"""
Auto-fix capabilities for common pipeline issues.
"""

import copy
import yaml
from typing import Dict, List, Any, Optional

class PipelineAutoFixer:
    """Automatically fix common pipeline issues."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fixes_applied = []
    
    def fix_missing_resources(self, component: Dict[str, Any]) -> bool:
        """Add missing resource requests."""
        container = component.get("container", {})
        resources = container.get("resources", {})
        requests = resources.get("requests", {})
        
        fixes_made = False
        
        if "cpu" not in requests:
            requests["cpu"] = "1"
            fixes_made = True
            self.fixes_applied.append(f"Added CPU request '1' to {component['name']}")
        
        if "memory" not in requests:
            requests["memory"] = "1Gi"
            fixes_made = True
            self.fixes_applied.append(f"Added memory request '1Gi' to {component['name']}")
        
        if fixes_made:
            resources["requests"] = requests
            container["resources"] = resources
            component["container"] = container
        
        return fixes_made
    
    def fix_missing_limits(self, component: Dict[str, Any]) -> bool:
        """Add missing resource limits."""
        container = component.get("container", {})
        resources = container.get("resources", {})
        limits = resources.get("limits", {})
        requests = resources.get("requests", {})
        
        fixes_made = False
        
        if "cpu" not in limits and "cpu" in requests:
            # Set limit to 2x request
            cpu_request = requests["cpu"]
            if cpu_request.endswith("m"):
                cpu_limit = str(int(cpu_request[:-1]) * 2) + "m"
            else:
                cpu_limit = str(int(float(cpu_request) * 2))
            limits["cpu"] = cpu_limit
            fixes_made = True
            self.fixes_applied.append(f"Added CPU limit '{cpu_limit}' to {component['name']}")
        
        if "memory" not in limits and "memory" in requests:
            # Set limit to 2x request
            memory_request = requests["memory"]
            if memory_request.endswith("Gi"):
                memory_limit = str(int(memory_request[:-2]) * 2) + "Gi"
            elif memory_request.endswith("Mi"):
                memory_limit = str(int(memory_request[:-2]) * 2) + "Mi"
            else:
                memory_limit = memory_request  # Fallback
            limits["memory"] = memory_limit
            fixes_made = True
            self.fixes_applied.append(f"Added memory limit '{memory_limit}' to {component['name']}")
        
        if fixes_made:
            resources["limits"] = limits
            container["resources"] = resources
            component["container"] = container
        
        return fixes_made
    
    def fix_retry_policy(self, component: Dict[str, Any]) -> bool:
        """Add missing retry policy."""
        if not component.get("retryStrategy"):
            component["retryStrategy"] = {"limit": "3"}
            self.fixes_applied.append(f"Added retry policy (limit: 3) to {component['name']}")
            return True
        return False
    
    def fix_security_context(self, component: Dict[str, Any]) -> bool:
        """Fix security context issues."""
        container = component.get("container", {})
        security_context = container.get("securityContext", {})
        
        fixes_made = False
        
        # Fix privileged containers
        if security_context.get("privileged"):
            security_context["privileged"] = False
            fixes_made = True
            self.fixes_applied.append(f"Disabled privileged mode for {component['name']}")
        
        # Fix root user
        run_as_user = security_context.get("runAsUser")
        if run_as_user is None or run_as_user == 0:
            security_context["runAsUser"] = 1000
            fixes_made = True
            self.fixes_applied.append(f"Set runAsUser to 1000 for {component['name']}")
        
        if fixes_made:
            container["securityContext"] = security_context
            component["container"] = container
        
        return fixes_made
    
    def fix_image_tags(self, component: Dict[str, Any]) -> bool:
        """Fix latest image tags."""
        container = component.get("container", {})
        image = container.get("image", "")
        
        if image.endswith(":latest"):
            # Replace :latest with a common stable version
            if "python" in image:
                fixed_image = image.replace(":latest", ":3.9")
            elif "ubuntu" in image:
                fixed_image = image.replace(":latest", ":20.04")
            elif "alpine" in image:
                fixed_image = image.replace(":latest", ":3.16")
            else:
                fixed_image = image.replace(":latest", ":stable")
            
            container["image"] = fixed_image
            component["container"] = container
            self.fixes_applied.append(f"Updated image tag from {image} to {fixed_image} for {component['name']}")
            return True
        
        return False
    
    def fix_hardcoded_secrets(self, component: Dict[str, Any]) -> bool:
        """Convert hardcoded secrets to secretKeyRef."""
        container = component.get("container", {})
        env_vars = container.get("env", [])
        
        secret_keywords = ["SECRET", "PASSWORD", "API_KEY", "TOKEN", "ACCESS_KEY"]
        fixes_made = False
        
        for env_var in env_vars:
            var_name = env_var.get("name", "").upper()
            if any(keyword in var_name for keyword in secret_keywords):
                if "value" in env_var and "valueFrom" not in env_var:
                    # Convert to secretKeyRef
                    secret_name = f"{component['name']}-secrets"
                    key_name = var_name.lower().replace("_", "-")
                    
                    env_var.pop("value", None)
                    env_var["valueFrom"] = {
                        "secretKeyRef": {
                            "name": secret_name,
                            "key": key_name
                        }
                    }
                    fixes_made = True
                    self.fixes_applied.append(
                        f"Converted hardcoded secret '{var_name}' to secretKeyRef in {component['name']}"
                    )
        
        if fixes_made:
            container["env"] = env_vars
            component["container"] = container
        
        return fixes_made
    
    def apply_fixes(self, pipeline: Dict[str, Any], components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply all available fixes to the pipeline."""
        self.fixes_applied = []
        
        # Work on a copy to avoid modifying the original
        fixed_pipeline = copy.deepcopy(pipeline)
        
        # Find and update components in the pipeline structure
        templates = fixed_pipeline.get("spec", {}).get("templates", [])
        
        for template in templates:
            if "container" in template:
                component_name = template.get("name", "")
                
                # Find matching component
                matching_component = None
                for comp in components:
                    if comp["name"] == component_name:
                        matching_component = comp
                        break
                
                if matching_component:
                    # Apply fixes to the template directly
                    self.fix_missing_resources(template)
                    self.fix_missing_limits(template)
                    self.fix_retry_policy(template)
                    self.fix_security_context(template)
                    self.fix_image_tags(template)
                    self.fix_hardcoded_secrets(template)
        
        return fixed_pipeline
    
    def generate_fix_summary(self) -> Dict[str, Any]:
        """Generate a summary of fixes applied."""
        return {
            "total_fixes": len(self.fixes_applied),
            "fixes_applied": self.fixes_applied,
            "categories": {
                "resources": len([f for f in self.fixes_applied if "resource" in f.lower() or "cpu" in f.lower() or "memory" in f.lower()]),
                "security": len([f for f in self.fixes_applied if "security" in f.lower() or "privileged" in f.lower() or "runAsUser" in f.lower()]),
                "reliability": len([f for f in self.fixes_applied if "retry" in f.lower()]),
                "images": len([f for f in self.fixes_applied if "image" in f.lower()]),
                "secrets": len([f for f in self.fixes_applied if "secret" in f.lower()])
            }
        }

def auto_fix_pipeline(pipeline: Dict[str, Any], components: List[Dict[str, Any]], config: Dict[str, Any]) -> tuple:
    """
    Auto-fix pipeline issues and return the fixed pipeline and summary.
    
    Returns:
        tuple: (fixed_pipeline, fix_summary)
    """
    fixer = PipelineAutoFixer(config)
    fixed_pipeline = fixer.apply_fixes(pipeline, components)
    fix_summary = fixer.generate_fix_summary()
    
    return fixed_pipeline, fix_summary 