from graphviz import Digraph
import json


def to_dot(recipe: dict):
    dot = Digraph(comment=recipe['name'])

    # Set default node attributes
    dot.attr('node', style='filled')

    # Add nodes and edges
    for node in recipe['nodes']:
        if node['type'] == 'ingredient':
            label = f"{node['name_en']} ({node.get('quantity') if node.get('quantity') is not None else ''} {node.get('quantity_unit') if node.get('quantity_unit') is not None else ''})"
            dot.node(node['id'], label, shape='ellipse', fillcolor='yellow')
        else:
            label = f"{node['description']} (Action: {node['action']})"
            dot.node(node['id'], label, shape='box', fillcolor='#FFCC99')  # light orange color in hexadecimal

        # Add edges
        if node.get('next_steps'):
            for next_step in node['next_steps']:
                dot.edge(node['id'], next_step)
    return dot


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('parsed_recipe', help='Path to parsed recipe JSON')
    args = parser.parse_args()

    with open(args.parsed_recipe) as f:
        recipe = json.load(f)

    dot = to_dot(recipe)
    dot.render(args.parsed_recipe.replace('.json', ''), format='png')