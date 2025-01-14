from flask import Flask, request, jsonify, render_template, send_file
import networkx as nx
import io
import matplotlib.pyplot as plt
import json
import csv

app = Flask(__name__)

# Initialize the graph
graph = nx.DiGraph()

# Endpoint for adding relationships
@app.route('/add_relationship', methods=['POST'])
def add_relationship():
    data = request.json
    source = data.get('source')
    target = data.get('target')
    relation = data.get('relation')
    graph.add_edge(source, target, relation=relation)
    return jsonify({'message': 'Relationship added successfully'})

@app.route('/query', methods=['GET'])
def query_graph():
    entity = request.args.get('entity')
    if entity not in graph:
        return jsonify({'message': 'Entity not found'})

    # Gather relationships for the queried entity
    relationships = []
    for neighbor in graph[entity]:
        relation = graph[entity][neighbor].get('relation', 'Unknown')
        relationships.append({'source': entity, 'target': neighbor, 'relation': relation})
    
    # Prepare data for visualization
    nodes = [{'id': entity, 'label': entity}]
    links = [{'from': entity, 'to': neighbor, 'relation': relation} for neighbor, relation in
             [(rel['target'], rel['relation']) for rel in relationships]]
    for rel in relationships:
        nodes.append({'id': rel['target'], 'label': rel['target']})

    return jsonify({'nodes': nodes, 'links': links})

@app.route('/query_graph_visualization', methods=['GET'])
def query_graph_visualization():
    entity = request.args.get('entity')
    if entity not in graph:
        return jsonify({'message': 'Entity not found'}), 404

    # Create a subgraph for visualization
    subgraph = graph.subgraph([entity] + list(graph[entity]))

    # Calculate node sizes based on text length
    node_sizes = []
    for node in subgraph.nodes:
        node_text_length = len(node)
        # Scale size, e.g., base size of 1000 + 100 per character
        node_sizes.append(1000 + (node_text_length * 100))

    # Create a visualization
    plt.figure(figsize=(8, 8))
    pos = nx.spring_layout(subgraph)
    nx.draw(
        subgraph,
        pos,
        with_labels=True,
        node_color="lightblue",
        node_size=node_sizes,
        font_size=10
    )
    edge_labels = nx.get_edge_attributes(subgraph, 'relation')
    nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels)

    # Save the image to a BytesIO object
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Return the image as a PNG
    return send_file(img, mimetype='image/png')


ALLOWED_RELATIONSHIPS = {
    "has_skill": ("Employee", "Skill"),
    "trained_in": ("Employee", "Training Program"),
    "works_as": ("Employee", "Job Role"),
    "required_for": ("Skill", "Job Role"),
}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in request."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected."}), 400

    try:
        if file.filename.endswith('.csv'):
            data = csv.DictReader(file.stream.read().decode('utf-8').splitlines())
            for row in data:
                # Validate row fields
                if not all(k in row for k in ['source_entity', 'relationship_type', 'target_entity']):
                    return jsonify({"message": "Missing required fields in CSV."}), 400
                # Add to graph
                graph.add_edge(
                    row['source_entity'], 
                    row['target_entity'], 
                    relation=row['relationship_type']
                )

        elif file.filename.endswith('.json'):
            try:
                data = json.load(file.stream)
                for record in data:
                    # Validate record fields
                    if not all(k in record for k in ['source_entity', 'relationship_type', 'target_entity']):
                        return jsonify({"message": "Missing required fields in JSON."}), 400
                    # Add to graph
                    graph.add_edge(
                        record['source_entity'], 
                        record['target_entity'], 
                        relation=record['relationship_type']
                    )
            except json.JSONDecodeError:
                return jsonify({"message": "Invalid JSON file."}), 400

        else:
            return jsonify({"message": "Unsupported file format. Please upload CSV or JSON."}), 400

        return jsonify({"message": "File uploaded successfully!!!"}), 200

    except Exception as e:
        return jsonify({"message": f"Error processing file: {str(e)}"}), 500

# Render main page

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
