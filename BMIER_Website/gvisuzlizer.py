import graphviz

# Create a new graph
g = graphviz.Digraph(name='cluster', format='png')

# Create subgraphs for the primary cluster
gpu_cluster = graphviz.Digraph(name='gpu_cluster', graph_attr={'rankdir': 'LR'})

# Add nodes for each server to the appropriate subgraph
# Edge Cluster
edge_cluster = graphviz.Digraph(name='edge_cluster', graph_attr={'rankdir': 'LR'})
edge_cluster.node('CM4', shape='ellipse')
edge_cluster.node('Nano', shape='ellipse')
edge_cluster.node('Switch 3', shape='rectangle')
edge_cluster.node('Bluefield 2', shape='ellipse')
edge_cluster.node('Bluefield 4', shape='ellipse')
edge_cluster.node('Orin 1', shape='ellipse')
edge_cluster.node('Orin 2', shape='ellipse')

# Edge Cluster Connections
edge_cluster.edge('CM4', 'Switch 3', label='PCIe Gen 2 x1')
edge_cluster.edge('Nano', 'Switch 3', label='PCIe Gen 2 x1')
edge_cluster.edge('Switch 3', 'Orin 1', label='PCIe Gen 2 x1')
edge_cluster.edge('Switch 3', 'Orin 2', label='PCIe Gen 2 x1')
edge_cluster.edge('Orin 1', 'Switch 3', label='PCIe Gen 2 x1')
edge_cluster.edge('Orin 2', 'Switch 3', label='PCIe Gen 2 x1')
edge_cluster.edge('Orin 1', 'Bluefield 2', label='PCIe Gen 4 x8')
edge_cluster.edge('Orin 2', 'Bluefield 4', label='PCIe Gen 4 x8')
edge_cluster.edge('Bluefield 2', 'Orin 1', label='PCIe Gen 4 x8')
edge_cluster.edge('Bluefield 4', 'Orin 2', label='PCIe Gen 4 x8')
edge_cluster.edge('Bluefield 1', 'Bluefield 2', label='Infiniband 25gbps')
edge_cluster.edge('Bluefield 1', 'Bluefield 4', label='Infiniband 25gbps')
edge_cluster.edge('Bluefield 3', 'Bluefield 4', label='Infiniband 25gbps')
edge_cluster.edge('Bluefield 3', 'Bluefield 2', label='Infiniband 25gbps')
edge_cluster.edge('Bluefield 2', 'Bluefield 1', label='Infiniband 25gbps')
edge_cluster.edge('Bluefield 4', 'Bluefield 1', label='Infiniband 25gbps')
edge_cluster.edge('Bluefield 4', 'Bluefield 3', label='Infiniband 25gbps')
edge_cluster.edge('Bluefield 2', 'Bluefield 3', label='Infiniband 25gbps')

# Primary Cluster
gpu_cluster.node('Server', shape='ellipse')
gpu_cluster.node('Bluefield 1', shape='ellipse')
gpu_cluster.node('Bluefield 3', shape='ellipse')
edge_cluster.node('Orin 1', shape='ellipse')
edge_cluster.node('Orin 2', shape='ellipse')
gpu_cluster.node('Switch 1', shape='rectangle')
gpu_cluster.node('Switch 2', shape='rectangle')

# Primary Cluster Connections
gpu_cluster.edge('Switch 1', 'Server', label='PCIe Gen 3 x8')
gpu_cluster.edge('Switch 2', 'Server', label='PCIe Gen 3 x8')
gpu_cluster.edge('Server', 'Switch 1', label='PCIe Gen 3 x8')
gpu_cluster.edge('Server', 'Switch 2', label='PCIe Gen 3 x8')
gpu_cluster.edge('Switch 1', 'Bluefield 1', label='PCIe Gen 3 x8')
gpu_cluster.edge('Switch 2', 'Bluefield 3', label='PCIe Gen 3 x8')
gpu_cluster.edge('Bluefield 1', 'Switch 1', label='PCIe Gen 3 x8')
gpu_cluster.edge('Bluefield 3', 'Switch 2', label='PCIe Gen 3 x8')

g.subgraph(gpu_cluster)
g.subgraph(edge_cluster)

# OOB Management
# All nodes are fully connected via the OOB Management Network

# Render the graph
g.render(view=True)
