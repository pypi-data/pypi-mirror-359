# kfp_doctor/analyzer.py
"""
Advanced pipeline analysis features including performance, cost, and complexity analysis.
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

@dataclass
class ResourceUsage:
    """Resource usage information for a component."""
    cpu_request: float
    memory_request_gb: float
    cpu_limit: float
    memory_limit_gb: float
    estimated_cost_per_hour: float

@dataclass
class ComplexityMetrics:
    """Pipeline complexity metrics."""
    total_components: int
    max_parallelism: int
    dependency_depth: int
    cyclic_dependencies: bool
    complexity_score: float

@dataclass
class PerformanceInsights:
    """Performance analysis insights."""
    bottleneck_components: List[str]
    resource_imbalance: List[str]
    optimization_suggestions: List[str]
    estimated_runtime_minutes: int

class PipelineAnalyzer:
    """Advanced pipeline analyzer for performance, cost, and complexity analysis."""
    
    def __init__(self):
        # Cost estimates per hour (example rates - customize for your cloud provider)
        self.cost_rates = {
            "cpu_per_core": 0.048,  # $0.048 per vCPU hour
            "memory_per_gb": 0.0065,  # $0.0065 per GB hour
        }
    
    def parse_cpu_value(self, cpu_str: str) -> float:
        """Parse CPU value to float (cores)."""
        if not cpu_str:
            return 0.0
        
        cpu_str = cpu_str.strip()
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000
        else:
            return float(cpu_str)
    
    def parse_memory_value(self, memory_str: str) -> float:
        """Parse memory value to float (GB)."""
        if not memory_str:
            return 0.0
            
        memory_str = memory_str.strip()
        if memory_str.endswith('Gi'):
            return float(memory_str[:-2])
        elif memory_str.endswith('Mi'):
            return float(memory_str[:-2]) / 1024
        elif memory_str.endswith('G'):
            return float(memory_str[:-1])
        elif memory_str.endswith('M'):
            return float(memory_str[:-1]) / 1024
        else:
            return float(memory_str) / (1024**3)  # Assume bytes
    
    def analyze_resource_usage(self, components: List[Dict]) -> List[ResourceUsage]:
        """Analyze resource usage for all components."""
        usage_data = []
        
        for component in components:
            resources = component.get("container", {}).get("resources", {})
            requests = resources.get("requests", {})
            limits = resources.get("limits", {})
            
            cpu_request = self.parse_cpu_value(requests.get("cpu", "0"))
            memory_request = self.parse_memory_value(requests.get("memory", "0"))
            cpu_limit = self.parse_cpu_value(limits.get("cpu", str(cpu_request * 2)))
            memory_limit = self.parse_memory_value(limits.get("memory", str(memory_request * 2)))
            
            # Estimate cost per hour
            cost_per_hour = (
                cpu_request * self.cost_rates["cpu_per_core"] +
                memory_request * self.cost_rates["memory_per_gb"]
            )
            
            usage = ResourceUsage(
                cpu_request=cpu_request,
                memory_request_gb=memory_request,
                cpu_limit=cpu_limit,
                memory_limit_gb=memory_limit,
                estimated_cost_per_hour=cost_per_hour
            )
            usage_data.append(usage)
        
        return usage_data
    
    def calculate_complexity_metrics(self, components: List[Dict], used_templates: set) -> ComplexityMetrics:
        """Calculate pipeline complexity metrics."""
        total_components = len(components)
        
        # Simple complexity scoring
        complexity_score = total_components * 1.0
        
        # Add penalty for unused components
        unused_components = len(components) - len(used_templates)
        complexity_score += unused_components * 0.5
        
        # Add penalty for missing retry policies
        no_retry_count = sum(1 for c in components if not c.get("retry_strategy"))
        complexity_score += no_retry_count * 0.3
        
        return ComplexityMetrics(
            total_components=total_components,
            max_parallelism=min(total_components, 10),  # Simplified
            dependency_depth=max(3, total_components // 3),  # Simplified
            cyclic_dependencies=False,  # TODO: Implement cycle detection
            complexity_score=round(complexity_score, 2)
        )
    
    def analyze_performance(self, components: List[Dict], usage_data: List[ResourceUsage]) -> PerformanceInsights:
        """Analyze performance characteristics and provide insights."""
        bottlenecks = []
        imbalances = []
        suggestions = []
        
        # Identify resource-heavy components
        for i, (component, usage) in enumerate(zip(components, usage_data)):
            name = component["name"]
            
            # Check for high resource usage
            if usage.cpu_request > 4:
                bottlenecks.append(f"{name} (High CPU: {usage.cpu_request} cores)")
            if usage.memory_request_gb > 8:
                bottlenecks.append(f"{name} (High Memory: {usage.memory_request_gb}GB)")
            
            # Check for resource imbalances
            if usage.cpu_limit > usage.cpu_request * 3:
                imbalances.append(f"{name}: CPU limit much higher than request")
            if usage.memory_limit_gb > usage.memory_request_gb * 3:
                imbalances.append(f"{name}: Memory limit much higher than request")
            
            # Generate optimization suggestions
            if usage.cpu_request > 8:
                suggestions.append(f"Consider breaking down {name} into smaller components")
            if not component.get("retry_strategy"):
                suggestions.append(f"Add retry policy to {name} for better resilience")
        
        # Estimate runtime (simplified)
        max_cpu = max([u.cpu_request for u in usage_data] + [1])
        estimated_runtime = int(30 + (max_cpu * 5))  # Simplified estimation
        
        return PerformanceInsights(
            bottleneck_components=bottlenecks,
            resource_imbalance=imbalances,
            optimization_suggestions=suggestions,
            estimated_runtime_minutes=estimated_runtime
        )
    
    def generate_cost_report(self, components: List[Dict], usage_data: List[ResourceUsage]) -> Dict[str, Any]:
        """Generate detailed cost analysis report."""
        total_cost_per_hour = sum(u.estimated_cost_per_hour for u in usage_data)
        
        # Cost breakdown by component
        cost_breakdown = []
        for component, usage in zip(components, usage_data):
            cost_breakdown.append({
                "component": component["name"],
                "cpu_cores": usage.cpu_request,
                "memory_gb": usage.memory_request_gb,
                "cost_per_hour": round(usage.estimated_cost_per_hour, 4),
                "cost_per_day": round(usage.estimated_cost_per_hour * 24, 2),
                "cost_per_month": round(usage.estimated_cost_per_hour * 24 * 30, 2)
            })
        
        return {
            "total_cost_per_hour": round(total_cost_per_hour, 4),
            "total_cost_per_day": round(total_cost_per_hour * 24, 2),
            "total_cost_per_month": round(total_cost_per_hour * 24 * 30, 2),
            "component_breakdown": cost_breakdown,
            "optimization_potential": round(total_cost_per_hour * 0.2, 4)  # Assume 20% optimization potential
        }

def analyze_pipeline(components: List[Dict], used_templates: set) -> Dict[str, Any]:
    """Main function to analyze pipeline comprehensively."""
    analyzer = PipelineAnalyzer()
    
    # Perform various analyses
    usage_data = analyzer.analyze_resource_usage(components)
    complexity = analyzer.calculate_complexity_metrics(components, used_templates)
    performance = analyzer.analyze_performance(components, usage_data)
    cost_report = analyzer.generate_cost_report(components, usage_data)
    
    return {
        "resource_usage": usage_data,
        "complexity_metrics": complexity,
        "performance_insights": performance,
        "cost_analysis": cost_report
    } 