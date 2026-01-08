import networkx as nx
import random

def fluid_communities(G, k):
    nodes = list(G.nodes())
    seeds = random.sample(nodes, k)
    node_to_comm = {n: i for i, n in enumerate(seeds)}
    comm_to_nodes = [{n} for n in seeds]
    
    for n in set(nodes) - set(seeds):
        node_to_comm[n] = None

    # Iterative Propagation until stability 
    changed = True
    while changed:
        changed = False
        shuffled_nodes = nodes[:]
        random.shuffle(shuffled_nodes)
        
        for v in shuffled_nodes:
            # Calculate aggregated densities in ego network 
            ego = list(G.neighbors(v)) + [v]
            densities = {}
            for n in ego:
                c = node_to_comm[n]
                if c is not None:
                    densities[c] = densities.get(c, 0) + (1.0 / len(comm_to_nodes[c]))
            
            if not densities: continue
            
            # Find candidates with max density
            max_d = max(densities.values())
            candidates = [c for c, d in densities.items() if d == max_d]
            
            curr = node_to_comm[v]
            # Keep if current is valid, else pick random new
            if curr not in candidates:
                new_c = random.choice(candidates)
                if curr is not None: comm_to_nodes[curr].remove(v)
                node_to_comm[v] = new_c
                comm_to_nodes[new_c].add(v)
                changed = True
                
    return {n: c + 1 for n, c in node_to_comm.items()}