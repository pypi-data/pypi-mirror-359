import pytest
from kfp_doctor.parser import get_components_from_argo_workflow

class TestKfpDoctorParser:
    def test_simple_pipeline_parsing(self):
        """Test parsing a simple pipeline with one component."""
        pipeline = {
            "spec": {
                "templates": [
                    {
                        "name": "main",
                        "dag": {
                            "tasks": [
                                {"name": "task1", "template": "task1-template"}
                            ]
                        }
                    },
                    {
                        "name": "task1-template",
                        "container": {
                            "image": "python:3.9",
                            "command": ["echo", "hello"]
                        }
                    }
                ]
            }
        }
        
        result = get_components_from_argo_workflow(pipeline)
        
        assert len(result["components"]) == 1
        assert result["components"][0]["name"] == "task1-template"
        assert result["components"][0]["container"]["image"] == "python:3.9"
        assert "task1-template" in result["used_templates"]

    def test_multiple_components_parsing(self):
        """Test parsing a pipeline with multiple components."""
        pipeline = {
            "spec": {
                "templates": [
                    {
                        "name": "main",
                        "dag": {
                            "tasks": [
                                {"name": "task1", "template": "task1-template"},
                                {"name": "task2", "template": "task2-template"}
                            ]
                        }
                    },
                    {
                        "name": "task1-template",
                        "container": {
                            "image": "python:3.9",
                            "command": ["echo", "hello"]
                        }
                    },
                    {
                        "name": "task2-template",
                        "container": {
                            "image": "ubuntu:20.04",
                            "command": ["echo", "world"]
                        }
                    }
                ]
            }
        }
        
        result = get_components_from_argo_workflow(pipeline)
        
        assert len(result["components"]) == 2
        component_names = [c["name"] for c in result["components"]]
        assert "task1-template" in component_names
        assert "task2-template" in component_names
        assert len(result["used_templates"]) == 2

    def test_unused_component_detection(self):
        """Test detection of unused components."""
        pipeline = {
            "spec": {
                "templates": [
                    {
                        "name": "main",
                        "dag": {
                            "tasks": [
                                {"name": "task1", "template": "task1-template"}
                            ]
                        }
                    },
                    {
                        "name": "task1-template",
                        "container": {
                            "image": "python:3.9",
                            "command": ["echo", "hello"]
                        }
                    },
                    {
                        "name": "unused-template",
                        "container": {
                            "image": "python:3.9",
                            "command": ["echo", "unused"]
                        }
                    }
                ]
            }
        }
        
        result = get_components_from_argo_workflow(pipeline)
        
        assert len(result["components"]) == 2
        assert len(result["used_templates"]) == 1
        assert "task1-template" in result["used_templates"]
        assert "unused-template" not in result["used_templates"]

    def test_retry_strategy_parsing(self):
        """Test parsing of retry strategies."""
        pipeline = {
            "spec": {
                "templates": [
                    {
                        "name": "main",
                        "dag": {
                            "tasks": [
                                {"name": "task1", "template": "task1-template"}
                            ]
                        }
                    },
                    {
                        "name": "task1-template",
                        "container": {
                            "image": "python:3.9",
                            "command": ["echo", "hello"]
                        },
                        "retryStrategy": {"limit": "3"}
                    }
                ]
            }
        }
        
        result = get_components_from_argo_workflow(pipeline)
        
        assert result["components"][0]["retry_strategy"] == {"limit": "3"}

    def test_missing_retry_strategy(self):
        """Test handling of missing retry strategy."""
        pipeline = {
            "spec": {
                "templates": [
                    {
                        "name": "main",
                        "dag": {
                            "tasks": [
                                {"name": "task1", "template": "task1-template"}
                            ]
                        }
                    },
                    {
                        "name": "task1-template",
                        "container": {
                            "image": "python:3.9",
                            "command": ["echo", "hello"]
                        }
                    }
                ]
            }
        }
        
        result = get_components_from_argo_workflow(pipeline)
        
        assert result["components"][0]["retry_strategy"] is None

    def test_empty_pipeline(self):
        """Test handling of empty or minimal pipeline."""
        pipeline = {"spec": {"templates": []}}
        
        result = get_components_from_argo_workflow(pipeline)
        
        assert len(result["components"]) == 0
        assert len(result["used_templates"]) == 0

    def test_no_dag_template(self):
        """Test handling of pipeline without DAG template."""
        pipeline = {
            "spec": {
                "templates": [
                    {
                        "name": "single-template",
                        "container": {
                            "image": "python:3.9",
                            "command": ["echo", "hello"]
                        }
                    }
                ]
            }
        }
        
        result = get_components_from_argo_workflow(pipeline)
        
        assert len(result["components"]) == 1
        assert len(result["used_templates"]) == 0

    def test_complex_container_config(self):
        """Test parsing of complex container configurations."""
        pipeline = {
            "spec": {
                "templates": [
                    {
                        "name": "main",
                        "dag": {
                            "tasks": [
                                {"name": "task1", "template": "complex-template"}
                            ]
                        }
                    },
                    {
                        "name": "complex-template",
                        "container": {
                            "image": "python:3.9",
                            "command": ["python", "-c"],
                            "args": ["print('hello')"],
                            "env": [
                                {"name": "ENV_VAR", "value": "test"}
                            ],
                            "resources": {
                                "requests": {"cpu": "1", "memory": "1Gi"},
                                "limits": {"cpu": "2", "memory": "2Gi"}
                            },
                            "securityContext": {
                                "runAsUser": 1000,
                                "privileged": False
                            }
                        }
                    }
                ]
            }
        }
        
        result = get_components_from_argo_workflow(pipeline)
        
        component = result["components"][0]
        assert component["name"] == "complex-template"
        assert "env" in component["container"]
        assert "resources" in component["container"]
        assert "securityContext" in component["container"]
        assert component["container"]["securityContext"]["runAsUser"] == 1000

if __name__ == "__main__":
    pytest.main([__file__]) 