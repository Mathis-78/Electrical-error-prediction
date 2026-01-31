import node
import functions
import random
import numpy as np

def run_simulation(steps=2000, number=20, nodes_path="params.txt"):
    nodes_list = functions.import_nodes(nodes_path)
    nodes_dict = {int(n.id): n for n in nodes_list}

    X_data = []
    Y_data = []

    connections = [(i, i + 1) for i in range(number - 1)]
    for _ in range(5):
        a, b = random.randint(0, number - 1), random.randint(0, number - 1)
        if a != b:
            connections.append((a, b))

    neighbors_map = functions.build_adjacency_list(connections)

    for t in range(1, steps + 1):

        X_t = functions.snapshot_features(nodes_list, neighbors_map)

        failed_before = {int(n.id): bool(n.failed) for n in nodes_list}

        for n in nodes_list:
            nid = int(n.id)
            f, t_avg, nc = functions.get_node_context(nid, neighbors_map, nodes_dict)
            n.update_physics(t, f, t_avg, nc)
            n.check_failure()

        newly_failed = [int(n.id) for n in nodes_list if n.failed and not failed_before[int(n.id)]]

        if newly_failed:
            
            y_t = newly_failed[0]
            X_data.append(X_t)
            Y_data.append(y_t)

    return X_data, Y_data


if __name__ == "__main__":
    X = []
    Y = []
    n_simu = 1000

    for i in range(n_simu):
        print(f"Enregistrement simulation {i}")
        Xi, Yi = run_simulation()
        X.extend(Xi)
        Y.extend(Yi)

    X = np.array(X, dtype=np.float32) 
    Y = np.array(Y, dtype=np.int64)   

    np.savez_compressed("dataset.npz", X=X, y=Y)
    print("Saved dataset.npz")
    print("X shape:", X.shape, "| Y shape:", Y.shape)
