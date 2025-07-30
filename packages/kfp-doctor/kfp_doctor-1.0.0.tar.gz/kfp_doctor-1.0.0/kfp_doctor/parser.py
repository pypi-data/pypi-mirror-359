# kfp_doctor/parser.py

def get_components_from_argo_workflow(pipeline: dict) -> dict:
    """
    Parses a KFP-generated Argo Workflow dictionary and extracts a standardized
    list of container components and the DAG structure.

    Args:
        pipeline: The loaded pipeline YAML as a dictionary.

    Returns:
        A dictionary containing the list of components and the set of used templates.
    """
    components = []
    templates = pipeline.get("spec", {}).get("templates", [])
    dag_template = next((t for t in templates if "dag" in t), None)
    used_templates = set()

    if dag_template:
        tasks = dag_template.get("dag", {}).get("tasks", [])
        for task in tasks:
            used_templates.add(task.get("template"))

    for template in templates:
        if "container" in template:
            components.append({
                "name": template.get("name", "(unnamed)"),
                "container": template.get("container", {}),
                "retry_strategy": template.get("retryStrategy"),
            })
            
    return {"components": components, "used_templates": used_templates}