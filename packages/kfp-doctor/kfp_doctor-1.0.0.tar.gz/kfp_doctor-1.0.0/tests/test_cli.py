import pytest
import tempfile
import yaml
import json
import os
from click.testing import CliRunner
from kfp_doctor.cli import main

class TestKfpDoctorCLI:
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.runner = CliRunner()
        
        # Sample pipeline with no issues
        self.healthy_pipeline = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {"generateName": "healthy-pipeline-"},
            "spec": {
                "entrypoint": "main",
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
                            "image": "python:3.9.1",
                            "command": ["echo", "hello"],
                            "resources": {
                                "requests": {"cpu": "1", "memory": "1Gi"},
                                "limits": {"cpu": "2", "memory": "2Gi"}
                            },
                            "securityContext": {"runAsUser": 1000}
                        },
                        "retryStrategy": {"limit": "3"}
                    }
                ]
            }
        }
        
        # Pipeline with security issues
        self.insecure_pipeline = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {"generateName": "insecure-pipeline-"},
            "spec": {
                "entrypoint": "main",
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
                            "image": "python:latest",
                            "command": ["echo", "hello"],
                            "env": [
                                {"name": "DATABASE_PASSWORD", "value": "hardcoded-secret"}
                            ],
                            "securityContext": {"privileged": True, "runAsUser": 0}
                        }
                    }
                ]
            }
        }
        
        # Pipeline with excessive resources
        self.excessive_resources_pipeline = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {"generateName": "excessive-pipeline-"},
            "spec": {
                "entrypoint": "main",
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
                            "image": "python:3.9.1",
                            "command": ["echo", "hello"],
                            "resources": {
                                "requests": {"cpu": "16", "memory": "32Gi"}
                            },
                            "securityContext": {"runAsUser": 1000}
                        },
                        "retryStrategy": {"limit": "3"}
                    }
                ]
            }
        }

    def create_temp_pipeline(self, pipeline_dict):
        """Create a temporary pipeline file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(pipeline_dict, temp_file, default_flow_style=False)
        temp_file.close()
        return temp_file.name

    def test_healthy_pipeline_console_output(self):
        """Test that a healthy pipeline returns success with console output."""
        pipeline_file = self.create_temp_pipeline(self.healthy_pipeline)
        
        try:
            result = self.runner.invoke(main, ['check', pipeline_file])
            assert result.exit_code == 0
            assert "✅ All checks passed" in result.output
        finally:
            os.unlink(pipeline_file)

    def test_insecure_pipeline_finds_issues(self):
        """Test that security issues are detected."""
        pipeline_file = self.create_temp_pipeline(self.insecure_pipeline)
        
        try:
            result = self.runner.invoke(main, ['check', pipeline_file])
            assert result.exit_code == 1
            assert "privileged mode" in result.output
            assert "hardcoded secret" in result.output
            assert "latest" in result.output or ":latest" in result.output
            assert "root user" in result.output
        finally:
            os.unlink(pipeline_file)

    def test_json_output_format(self):
        """Test JSON output format."""
        pipeline_file = self.create_temp_pipeline(self.insecure_pipeline)
        
        try:
            result = self.runner.invoke(main, ['check', pipeline_file, '--output', 'json'])
            assert result.exit_code == 1
            
            # Parse JSON output
            output_data = json.loads(result.output)
            assert "issues" in output_data
            assert "summary" in output_data
            assert output_data["summary"]["total"] > 0
            assert output_data["summary"]["errors"] > 0
        finally:
            os.unlink(pipeline_file)

    def test_yaml_output_format(self):
        """Test YAML output format."""
        pipeline_file = self.create_temp_pipeline(self.insecure_pipeline)
        
        try:
            result = self.runner.invoke(main, ['check', pipeline_file, '--output', 'yaml'])
            assert result.exit_code == 1
            
            # Parse YAML output
            output_data = yaml.safe_load(result.output)
            assert "issues" in output_data
            assert "summary" in output_data
            assert output_data["summary"]["total"] > 0
        finally:
            os.unlink(pipeline_file)

    def test_output_to_file(self):
        """Test writing output to a file."""
        pipeline_file = self.create_temp_pipeline(self.insecure_pipeline)
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        output_file.close()
        
        try:
            result = self.runner.invoke(main, [
                'check', pipeline_file, 
                '--output', 'json', 
                '--output-file', output_file.name
            ])
            assert result.exit_code == 1
            assert f"Results written to {output_file.name}" in result.output
            
            # Verify file contents
            with open(output_file.name, 'r') as f:
                output_data = json.load(f)
            assert "issues" in output_data
            assert output_data["summary"]["total"] > 0
        finally:
            os.unlink(pipeline_file)
            os.unlink(output_file.name)

    def test_fail_on_warning(self):
        """Test --fail-on warning option."""
        pipeline_file = self.create_temp_pipeline(self.healthy_pipeline)
        
        # Modify to have a warning (missing retry policy)
        pipeline_dict = self.healthy_pipeline.copy()
        del pipeline_dict["spec"]["templates"][1]["retryStrategy"]
        pipeline_file = self.create_temp_pipeline(pipeline_dict)
        
        try:
            result = self.runner.invoke(main, ['check', pipeline_file, '--fail-on', 'warning'])
            assert result.exit_code == 1
        finally:
            os.unlink(pipeline_file)

    def test_fail_on_never(self):
        """Test --fail-on never option."""
        pipeline_file = self.create_temp_pipeline(self.insecure_pipeline)
        
        try:
            result = self.runner.invoke(main, ['check', pipeline_file, '--fail-on', 'never'])
            assert result.exit_code == 0
        finally:
            os.unlink(pipeline_file)

    def test_excessive_resources_check(self):
        """Test excessive resources detection."""
        pipeline_file = self.create_temp_pipeline(self.excessive_resources_pipeline)
        
        try:
            result = self.runner.invoke(main, ['check', pipeline_file])
            # Should detect excessive CPU and memory
            assert "exceeds maximum" in result.output
        finally:
            os.unlink(pipeline_file)

    def test_custom_config_file(self):
        """Test using a custom configuration file."""
        pipeline_file = self.create_temp_pipeline(self.insecure_pipeline)
        
        # Create custom config that disables some checks
        custom_config = {
            "checks": {
                "LATEST_IMAGE_TAG": {"enabled": False},
                "PRIVILEGED_CONTAINER": {"enabled": False}
            }
        }
        
        config_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(custom_config, config_file, default_flow_style=False)
        config_file.close()
        
        try:
            result = self.runner.invoke(main, ['check', pipeline_file, '--config', config_file.name])
            # Should have fewer issues since some checks are disabled
            assert "privileged mode" not in result.output
            assert "latest" not in result.output or ":latest" not in result.output
        finally:
            os.unlink(pipeline_file)
            os.unlink(config_file.name)

    def test_invalid_yaml_handling(self):
        """Test handling of invalid YAML files."""
        # Create invalid YAML file
        invalid_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        invalid_file.write("invalid: yaml: content: [unclosed")
        invalid_file.close()
        
        try:
            result = self.runner.invoke(main, ['check', invalid_file.name])
            assert result.exit_code == 1
            assert "Invalid YAML" in result.output
        finally:
            os.unlink(invalid_file.name)

    def test_missing_resources_check(self):
        """Test missing resources detection."""
        pipeline_dict = self.healthy_pipeline.copy()
        del pipeline_dict["spec"]["templates"][1]["container"]["resources"]
        pipeline_file = self.create_temp_pipeline(pipeline_dict)
        
        try:
            result = self.runner.invoke(main, ['check', pipeline_file])
            assert result.exit_code == 1
            assert "Missing resource requests" in result.output
        finally:
            os.unlink(pipeline_file)

    def test_unused_component_detection(self):
        """Test unused component detection."""
        pipeline_dict = self.healthy_pipeline.copy()
        # Add an unused template
        pipeline_dict["spec"]["templates"].append({
            "name": "unused-template",
            "container": {
                "image": "python:3.9.1",
                "command": ["echo", "unused"],
                "resources": {"requests": {"cpu": "1", "memory": "1Gi"}}
            }
        })
        pipeline_file = self.create_temp_pipeline(pipeline_dict)
        
        try:
            result = self.runner.invoke(main, ['check', pipeline_file])
            assert "unused" in result.output.lower() or "not used" in result.output
        finally:
            os.unlink(pipeline_file)

if __name__ == "__main__":
    pytest.main([__file__]) 