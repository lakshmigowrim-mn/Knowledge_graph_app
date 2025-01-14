import networkx as nx

def add_batch_relationships(graph, dataset):
    for record in dataset:
        source = record['source']
        target = record['target']
        relation = record['relation']
        graph.add_edge(source, target, relation=relation)

def visualize_graph(graph):
    # Use a basic visualization technique (can improve later)
    import matplotlib.pyplot as plt
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color="lightblue", node_size=500)
    plt.show()
