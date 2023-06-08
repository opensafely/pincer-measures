import yaml
from python_mermaid.diagram import MermaidDiagram, Node, Link


def load_yaml(file_name):
    """
    Load a YAML file and return the data.

    Args:
        file_name (str): The name of the YAML file to load.

    Returns:
        dict: The data loaded from the YAML file.
    """
    with open(file_name, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def create_diagram(actions):
    """
    Create a mermaid diagram based on the given actions.

    Args:
        actions (dict): A dictionary containing the actions.

    Returns:
        MermaidDiagram: The created diagram.
    """
    nodes_list = []
    links_list = []

    # Loop through each action in the actions dictionary.
    for key, value in actions.items():
        # Create a node for each action and add it to the nodes list.
        nodes_list.append(Node(key))

        # If the action has dependencies ('needs'), create links and add them to the links list.
        if value.get('needs'):
            for item in value['needs']:
                links_list.append(Link(Node(item), Node(key)))


    return MermaidDiagram(title="Project Pipeline", nodes=nodes_list, links=links_list)


if __name__ == "__main__":
    
    data = load_yaml("project.yaml")
    actions = data.get('actions', {})
    chart = create_diagram(actions)
    text = f"""```mermaid\n{chart}\n```"""

    with open("project.dag.md", "w") as text_file:
        text_file.write(text)
