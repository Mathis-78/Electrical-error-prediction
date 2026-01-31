import random
import math
from pyvis.network import Network
import node
import numpy as np

def generate_random_params():
    w_load = random.uniform(1.0, 3.0)
    w_temp = random.uniform(2.0, 5.0)
    w_age = random.uniform(1.0, 4.0)
    w_neighbor = random.uniform(2.0, 6.0)
    
    max_possible_risk = w_load + w_temp + w_age + w_neighbor
    
    resistance_factor = random.uniform(0.70, 0.90) 
    threshold = max_possible_risk * resistance_factor

    return {
        "A": random.uniform(10, 30),
        "B": random.uniform(40, 60),
        "omega": random.uniform(0.05, 0.2),
        "k_report": random.uniform(0.2, 0.5),
        "epsilon": random.uniform(0.5, 2.5),
        
        "a_joule": random.uniform(0.001, 0.003),
        "b_cool": random.uniform(0.05, 0.15),
        "c_diff": random.uniform(0.01, 0.05),
        "T_amb": 22.0,
        
        "E_a": random.uniform(0.4, 0.7),
        "T_ref": 22.0,
        
        "T_max": random.uniform(85.0, 120.0),
        "A_max": random.uniform(2000, 5000),
        
        # Poids
        "w_load": w_load,
        "w_temp": w_temp,
        "w_age": w_age,
        "w_neighbor": w_neighbor,
        
        "threshold": threshold
    }

def snapshot_features(nodes_list, neighbors_map):
    feats = []
    for n in nodes_list:
        feats.append([
            n.temp,
            n.load,
            n.age,
            n.neighbors_influence,
            int(n.failed),
            len(neighbors_map[int(n.id)])
        ])
    return feats

def sigmoid(x, threshold,k):
    return 1 / (1 + math.exp(-k*(x - threshold)))

def print_node(node):
    print(f"=== Node {node.id} ===")
    print(f"Failed              : {node.failed}")
    print(f"Temperature (°C)    : {node.temp:.2f}")
    print(f"Previous Temp (°C)  : {node.prev_temp:.2f}")
    print(f"Load                : {node.load:.2f}")
    print(f"Age                 : {node.age:.2f}")
    print(f"Previous Age        : {node.prev_age:.2f}")
    print(f"Neighbors Influence : {node.neighbors_influence:.3f}")
    print(f"------------------------------")

def build_adjacency_list(connections):
    adj = {}
    for a, b in connections:
        if a not in adj: adj[a] = []
        if b not in adj: adj[b] = []
        adj[a].append(b)
        adj[b].append(a)
    return adj

def get_node_context(node_id, neighbors_map, nodes_dict):
    if node_id not in neighbors_map:
        return 0, 0.0, 0 

    neighbor_ids = neighbors_map[node_id]
    
    failed_count = 0
    total_temp = 0.0
    count = len(neighbor_ids)

    for nid in neighbor_ids:
        neighbor = nodes_dict[nid]
        if neighbor.failed:
            failed_count += 1
        total_temp += neighbor.temp

    avg_temp = total_temp / count if count > 0 else 0.0

    return failed_count, avg_temp, count

def visualize_system(nodes_list, connections, filename="temp_graph.html", fixed_positions=None):
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white", select_menu=False)
    
    net.toggle_physics(False) 
    
    for n in nodes_list:
        color = "#00ff00"
        if n.failed: color = "#ff0000"
        elif n.temp > (n.params["T_max"] * 0.8): color = "#ffa500"
            
        info = f"Node {n.id}\nTemp: {n.temp:.1f}\nLoad: {n.load:.1f}"
        
        x_pos, y_pos = 0, 0
        if fixed_positions and n.id in fixed_positions:
            x_pos = fixed_positions[n.id][0] * 500
            y_pos = fixed_positions[n.id][1] * 500

        net.add_node(
            n.id, 
            label=f"N{n.id}", 
            title=info, 
            color=color, 
            x=x_pos, 
            y=y_pos,
            physics=False 
        )

    for a, b in connections:
        net.add_edge(a, b, color="#cccccc")

    net.save_graph(filename)

def export_params(node, filedirectory):
    params = (
        f"A: {node.params['A']}\n"
        f"B: {node.params['B']}\n"
        f"omega: {node.params['omega']}\n"
        f"k_report: {node.params['k_report']}\n"
        f"epsilon: {node.params['epsilon']}\n"
        f"\n"
        f"a_joule: {node.params['a_joule']}\n"
        f"b_cool: {node.params['b_cool']}\n"
        f"c_diff: {node.params['c_diff']}\n"
        f"T_amb: {node.params['T_amb']}\n"
        f"\n"
        f"E_a: {node.params['E_a']}\n"
        f"T_ref: {node.params['T_ref']}\n"
        f"\n"
        f"T_max: {node.params['T_max']}\n"
        f"A_max: {node.params['A_max']}\n"
        f"\n"
        f"w_load: {node.params['w_load']}\n"
        f"w_temp: {node.params['w_temp']}\n"
        f"w_age: {node.params['w_age']}\n"
        f"w_neighbor: {node.params['w_neighbor']}\n"
        f"\n"
        f"threshold: {node.params['threshold']}\n"
    )

    with open(filedirectory, "w", encoding="utf-8") as f:
        f.write(params)

def export_nodes(nodes, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        for node_obj in nodes:
            f.write(f"[NODE {node_obj.id}]\n")
            for k, v in node_obj.params.items():
                f.write(f"{k}: {v}\n")
            f.write("\n")


def import_nodes(filepath):
    nodes = []
    current_params = None
    current_id = None

    with open(filepath, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()

            if not line:
                continue

            # Début d'un node
            if line.startswith("[NODE ") and line.endswith("]"):
                # Finaliser le précédent
                if current_params is not None and current_id is not None:
                    nodes.append(node.Node(current_id, current_params))

                # Extraire l'id
                current_id = int(line.replace("[NODE", "").replace("]", "").strip())
                current_params = {}
                continue

            # Ligne key: value
            if ":" in line and current_params is not None:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                # Cast auto
                try:
                    if any(c in value for c in ".eE"):
                        casted = float(value)
                    else:
                        casted = int(value)
                except ValueError:
                    casted = value

                current_params[key] = casted

    # Dernier node
    if current_params is not None and current_id is not None:
        nodes.append(node.Node(current_id, current_params))

    return nodes

def num_of_failed(node_list):
    n = 0
    for node in node_list:
        if (node.failed):
            n+=1
    return n

def export_network(nn_instance, filename="best_model.npz"):
    try:
        np.savez_compressed(
            filename, 
            W1=nn_instance.W1, 
            W2=nn_instance.W2, 
            W3=nn_instance.W3
        )
        print(f"Modèle sauvegardé avec succès dans : {filename}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")

def import_network(nn_instance, filename="best_model.npz"):
    try:
        data = np.load(filename)
        nn_instance.W1 = data["W1"]
        nn_instance.W2 = data["W2"]
        nn_instance.W3 = data["W3"]
        print(f"Modèle chargé avec succès depuis : {filename}")
        return True
    except FileNotFoundError:
        print(f"Fichier {filename} introuvable. Le modèle reste vierge.")
        return False
    except Exception as e:
        print(f"Erreur lors du chargement : {e}")
        return False
    
def get_exact_scalers_from_dataset(dataset_path="dataset.npz"):
    data = np.load(dataset_path)
    x_full = data["X"] 
    
    scalers = []

    for i in range(6):
        col = x_full[:, :, i]
        val_max = np.max(np.abs(col))
        if val_max == 0: val_max = 1.0
        scalers.append(val_max)
    return scalers

def normalize_live_data(snapshot, scalers):

    data = np.array(snapshot, dtype=np.float32) 
    
    # On divise chaque colonne par le scaler correspondant (FIXE)
    for i in range(6):
        data[:, i] /= scalers[i]
        
    # On aplatit pour l'IA
    return data.reshape(1, -1)