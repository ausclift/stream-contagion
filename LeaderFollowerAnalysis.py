import json
import networkx as nx
import matplotlib.pyplot as plt

with open("events.json", "r") as f:
    data = json.load(f)

# Create directed graph
G = nx.DiGraph()

# Process each event
for event in data:
    leaders = event["leaders"]
    followers = event["followers"]
    
    # Add edges with weights
    for leader in leaders:
        for follower in followers:
            if G.has_edge(follower, leader):
                # Increment weight if edge exists
                G[follower][leader]["weight"] += 1
            else:
                # Add new edge
                G.add_edge(follower, leader, weight=1)

# Plot the graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)  # Unsure of best visualization layout
edges = G.edges(data=True)
weights = [data["weight"] for _, _, data in edges]  # Extract weights

# Draw graph with weights
nx.draw(
    G,
    pos,
    node_color="lightblue",
    node_size=2,
    edge_color="gray",
    width=weights  # Edge width proportional to weight
)

plt.title("Directed Graph with Weighted Edges", fontsize=16)
plt.show()
