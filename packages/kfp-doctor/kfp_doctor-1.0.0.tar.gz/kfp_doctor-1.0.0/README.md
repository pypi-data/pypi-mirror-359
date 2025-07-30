# 🩺 kfp-doctor

A comprehensive linter for healthy Kubeflow Pipelines with advanced analysis and auto-fix capabilities.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Key Features in v1.0.0

- 🔧 **Auto-fix capabilities** - Automatically fix common pipeline issues
- 📊 **Advanced analysis** - Performance, cost, and complexity analysis
- 🎯 **Smart config generation** - Environment-specific configurations
- 💰 **Cost estimation** - Per-component cost analysis and optimization
- ⚡ **Performance insights** - Bottleneck detection and runtime estimation
- 🎨 **Rich UI enhancements** - Progress indicators, detailed reporting

## 🚀 Features

### Core Linting (10 Comprehensive Checks)
- ✅ **Resource validation** - Missing/excessive CPU and memory requests
- 🔒 **Security checks** - Privileged containers, root users, hardcoded secrets
- 🏷️ **Image best practices** - Latest tags, registry validation
- 🛡️ **Reliability** - Retry policies, resource limits
- 📊 **Pipeline structure** - Unused components, dependency analysis

### Advanced Analysis
- 💰 **Cost Analysis** - Hourly/daily/monthly cost estimation with optimization suggestions
- ⚡ **Performance Insights** - Bottleneck detection, resource imbalance identification
- 📈 **Complexity Metrics** - Pipeline complexity scoring and dependency analysis
- 🎯 **Runtime Estimation** - Predicted execution time based on resource allocation

### Automation Features
- 🔧 **Auto-fix** - Automatically resolve common issues like missing resources, security contexts
- 🎯 **Smart Config Generation** - Environment-specific configurations (dev/staging/prod)
- 📋 **Template System** - Pre-built configurations for different use cases
- 🔄 **Pipeline Analysis** - Intelligent config recommendations based on your pipeline

### Developer Experience
- 🎨 **Rich Console UI** - Beautiful tables, progress indicators, color-coded output
- 📊 **Multiple Output Formats** - Console, JSON, YAML for CI/CD integration
- 🔍 **Verbose Mode** - Real-time check execution visibility
- 💡 **Comprehensive Help** - Built-in documentation and examples

## 📦 Installation

```bash
pip install kfp-doctor
```

## 🎯 Quick Start

### 1. Basic Pipeline Check
```bash
# Check your pipeline
kfp-doctor check my-pipeline.yaml

# Verbose mode with real-time progress
kfp-doctor check my-pipeline.yaml --verbose
```

### 2. Generate Optimal Configuration
```bash
# Generate config for your environment
kfp-doctor generate-config --template production

# Smart config based on your pipeline
kfp-doctor generate-config --analyze-pipeline my-pipeline.yaml
```

### 3. Auto-fix Common Issues
```bash
# Preview what would be fixed
kfp-doctor fix my-pipeline.yaml --dry-run

# Apply fixes with backup
kfp-doctor fix my-pipeline.yaml --backup
```

### 4. Advanced Analysis
```bash
# Performance and cost analysis
kfp-doctor analyze my-pipeline.yaml --include-cost --include-performance

# Export analysis results
kfp-doctor analyze my-pipeline.yaml --output json --output-file analysis.json
```

## 🛠️ Commands

### `check` - Pipeline Linting
Comprehensive pipeline validation with 10 built-in checks.

```bash
kfp-doctor check pipeline.yaml [OPTIONS]

Options:
  --config, -c PATH           Custom configuration file
  --output, -o FORMAT        Output format: console, json, yaml
  --output-file PATH         Save results to file
  --fail-on LEVEL           When to exit with error: error, warning, never
  --verbose, -v              Show detailed check execution
  --dry-run                  Preview what would be checked
```

### `analyze` - Advanced Analysis
Performance, cost, and complexity analysis with optimization insights.

```bash
kfp-doctor analyze pipeline.yaml [OPTIONS]

Options:
  --include-cost             Include detailed cost analysis
  --include-performance      Include performance insights
  --output FORMAT           Output format: console, json, yaml
  --output-file PATH        Save analysis to file
```

**Sample Output:**
```
📊 Pipeline Complexity Analysis
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric            ┃  Value  ┃ Assessment ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ Total Components  │    3    │            │
│ Dependency Depth  │    3    │            │
│ Max Parallelism   │    3    │            │
│ Complexity Score  │   3.0   │   Simple   │
└───────────────────┴─────────┴────────────┘

💰 Cost Analysis
┌─ Cost Summary ─────────────────────────────────────┐
│ 💵 Estimated Cost per Hour: $0.1495               │
│ 📅 Estimated Cost per Day: $3.59                  │
│ 📅 Estimated Cost per Month: $107.64              │
│ 🎯 Optimization Potential: $0.0299/hour           │
└────────────────────────────────────────────────────┘
```

### `fix` - Auto-fix Issues
Automatically resolve common pipeline issues.

```bash
kfp-doctor fix pipeline.yaml [OPTIONS]

Options:
  --output-file, -o PATH     Write fixed pipeline to file
  --dry-run                  Show what would be fixed
  --backup                   Create backup of original file
```

**Auto-fix Capabilities:**
- ✅ Add missing resource requests and limits
- ✅ Fix security contexts (disable privileged, set runAsUser)
- ✅ Update image tags from `:latest` to specific versions
- ✅ Add retry policies for reliability
- ✅ Convert hardcoded secrets to secretKeyRef

### `generate-config` - Configuration Generator
Create optimal configurations for different environments.

```bash
kfp-doctor generate-config [OPTIONS]

Options:
  --template, -t NAME        Template: development, staging, production, security-focused, cost-optimized
  --output-file, -o PATH     Output file (default: .kfp-doctor.yaml)
  --analyze-pipeline PATH    Analyze pipeline to suggest optimal config
  --list-templates          Show available templates
```

**Available Templates:**
- 🔧 **development** - Relaxed settings for development
- ⚖️ **staging** - Balanced settings for staging
- 🏭 **production** - Strict settings for production
- 🔒 **security-focused** - Maximum security settings
- 💰 **cost-optimized** - Resource efficiency focused

### `list-checks` - Check Documentation
View all available checks with descriptions and configuration.

```bash
kfp-doctor list-checks
```

### `help` - Comprehensive Help
Feature overview, examples, and quick start guide.

```bash
kfp-doctor help --examples
```

## ⚙️ Configuration

### Basic Configuration
Create `.kfp-doctor.yaml` in your project root:

```yaml
checks:
  MISSING_RESOURCES:
    enabled: true
    severity: ERROR
  LATEST_IMAGE_TAG:
    enabled: true
    severity: ERROR
  EXCESSIVE_RESOURCES:
    enabled: true
    severity: WARNING
    max_cpu: "8"
    max_memory: "16Gi"
  INSECURE_IMAGE_REGISTRY:
    enabled: true
    severity: ERROR
    allowed_registries:
      - "gcr.io/your-project"
      - "docker.io/library"
```

### Environment-Specific Configs
Generate optimized configurations for different environments:

```bash
# Development environment (relaxed)
kfp-doctor generate-config --template development

# Production environment (strict)
kfp-doctor generate-config --template production

# Security-focused environment
kfp-doctor generate-config --template security-focused
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
- name: Lint Kubeflow Pipeline
  run: |
    pip install kfp-doctor
    kfp-doctor check compiled-pipeline.yaml --output json --fail-on error
```

### GitLab CI
```yaml
lint-pipeline:
  script:
    - pip install kfp-doctor
    - kfp-doctor check compiled-pipeline.yaml --fail-on error
  artifacts:
    reports:
      junit: pipeline-report.xml
```

## 📊 All Available Checks

| Check | Description | Configurable |
|-------|-------------|--------------|
| `MISSING_RESOURCES` | Ensures all components have CPU and memory requests | ✅ |
| `MISSING_LIMITS` | Ensures components have resource limits | ✅ |
| `EXCESSIVE_RESOURCES` | Warns about over-provisioned resources | ✅ |
| `LATEST_IMAGE_TAG` | Warns against using `:latest` image tags | ✅ |
| `NO_RETRY_POLICY` | Checks for retry policies | ✅ |
| `PRIVILEGED_CONTAINER` | Detects privileged containers | ✅ |
| `RUN_AS_ROOT` | Warns about root user execution | ✅ |
| `HARDCODED_SECRET` | Identifies hardcoded secrets | ✅ |
| `UNUSED_COMPONENT` | Finds unused pipeline components | ✅ |
| `INSECURE_IMAGE_REGISTRY` | Validates image registries | ✅ |

## 📈 Example Workflows

### Development Workflow
```bash
# 1. Generate development config
kfp-doctor generate-config --template development

# 2. Check pipeline during development
kfp-doctor check pipeline.yaml --verbose

# 3. Auto-fix common issues
kfp-doctor fix pipeline.yaml --backup

# 4. Analyze performance
kfp-doctor analyze pipeline.yaml --include-performance
```

### Production Deployment
```bash
# 1. Generate production config
kfp-doctor generate-config --template production

# 2. Strict production check
kfp-doctor check pipeline.yaml --config .kfp-doctor.yaml --fail-on error

# 3. Cost analysis before deployment
kfp-doctor analyze pipeline.yaml --include-cost --output-file cost-report.json
```

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the Kubeflow community
- Inspired by pipeline best practices and production experience
- Designed for developer productivity and operational excellence
