import os
import pandas as pd
import networkx as nx
from algorithm import fluid_communities

def main():
    comp_dir = "competition"
    result_dir = "result"
    os.makedirs(result_dir, exist_ok=True)

    graph_files = [f for f in os.listdir(comp_dir) if f.endswith(".csv")]

    for file_name in graph_files:
        path = os.path.join(comp_dir, file_name)
        prefix = file_name.replace(".csv", "")
        
        try:
            df_adj = pd.read_csv(path, header=None)
            G = nx.from_pandas_adjacency(df_adj)
        except Exception as e:
            print(f"Skipping {file_name}: Could not parse as adjacency matrix.")
            continue

        # If 'K=' is in the filename, use that value. 
        # Otherwise, find the best K
        if "K=" in file_name:
            k_value = int(file_name.split("K=")[1].split(".")[0])
        else:
            # Paper mentions choosing k based on modularity when unknown
            best_mod = -1
            k_value = 2
            for k_test in range(2, 15):
                mapping = fluid_communities(G, k_test)
                comms = {}
                for n, c in mapping.items():
                    comms.setdefault(c, set()).add(n)
                mod = nx.community.modularity(G, list(comms.values()))
                if mod > best_mod:
                    best_mod = mod
                    k_value = k_test

        print(f"Processing {prefix}: {G.number_of_nodes()} nodes, K={k_value}")

        # handling disconnected components
        full_mapping = {}
        comm_offset = 0
        for comp_nodes in nx.connected_components(G):
            subG = G.subgraph(comp_nodes).copy()
            comp_k = max(1, round(k_value * (len(comp_nodes) / G.number_of_nodes())))
            comp_k = min(comp_k, len(comp_nodes))
            
            comp_mapping = fluid_communities(subG, comp_k)
            for node, cid in comp_mapping.items():
                if cid is not None:
                    full_mapping[node] = cid + comm_offset
            comm_offset += comp_k

        result_df = pd.DataFrame(list(full_mapping.items()), columns=["node", "community"]).sort_values("node")
        result_df.to_csv(os.path.join(result_dir, f"{prefix}.csv"), header=False, index=False)

if __name__ == "__main__":
    main()