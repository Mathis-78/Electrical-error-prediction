import streamlit as st
import trainingmodel
import functions
import time
import random
import networkx as nx
import plotly.graph_objects as go
import numpy as np
import pandas as pd

st.set_page_config(layout="wide", page_title="Simulateur")

# Chargement du modèle
Brain = trainingmodel.Neural_Network()
functions.import_network(Brain, "modele1.npz")

st.title("Simulateur Réseau & Benchmark IA")

col1, col2 = st.columns([1, 4])

with col1:
    st.subheader("Paramètres")
    run = st.checkbox("Lancer la Session")
    #Nombre de simulations défini
    num_sims = st.number_input("Nombre de simulations", min_value=1, max_value=1000, value=5)
    steps = st.slider("Durée par simulation (steps)", 100, 2000, 500)
    speed = st.slider("Vitesse d'affichage (ms)", 0, 500, 50) 
    
    st.divider()
    sim_info_box = st.empty()
    stats_box = st.empty()
    accuracy_box = st.empty()

with col2:
    chart_box = st.empty() 
    st.divider()
    st.subheader("Analyse IA en temps réel")
    pred_top_box = st.empty()
    pred_details_box = st.empty()

if run:
    #Stockage des scores
    session_hits = [] # Liste pour stocker 1 (juste) ou 0 (faux)
    SCALERS = functions.get_exact_scalers_from_dataset("dataset.npz")
    
    progress_bar = st.progress(0)
    
    # Boucle sur le nombre de simulations demandées
    for sim_idx in range(num_sims):
        sim_number = sim_idx + 1
        sim_info_box.info(f"Simulation {sim_number} / {num_sims}")
        
        # Initialisation du graphe
        nodes_list = functions.import_nodes("params.txt")
        nodes_dict = {n.id: n for n in nodes_list}
        
        connections = [(i, i+1) for i in range(19)]
        for _ in range(5):
            a, b = random.randint(0, 19), random.randint(0, 19)
            if a != b: connections.append((a, b))
        
        neighbors_map = functions.build_adjacency_list(connections)

        # Layout graphique
        G = nx.Graph()
        G.add_edges_from(connections)
        pos = nx.spring_layout(G, seed=42)
        
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None]) 
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#888'), hoverinfo='none', mode='lines')

        # Boucle temporelle
        for t in range(1, steps + 1):
            
            # 1. PRÉDICTION AVANT MISE A JOUR
            # On capture l'état pour savoir qui est déjà mort
            failed_before = {n.id: n.failed for n in nodes_list}
            
            snapshot = functions.snapshot_features(nodes_list, neighbors_map)
            input_vec = functions.normalize_live_data(snapshot, SCALERS)
            pred_probs = Brain.forward(input_vec)[0]
            predicted_node_id = np.argmax(pred_probs)
            max_risk_value = pred_probs[predicted_node_id] * 100

            # 2. MISE A JOUR PHYSIQUE
            for n in nodes_list:
                f, t_avg, nc = functions.get_node_context(n.id, neighbors_map, nodes_dict)
                n.update_physics(t, f, t_avg, nc)
                n.check_failure()

            # 3.VÉRIFICATION
            # On regarde quels noeuds viennent de mourir à cet instant t
            newly_failed = [n.id for n in nodes_list if n.failed and not failed_before[n.id]]
            
            if newly_failed:
                # La "vérité terrain" est le premier noeud qui a lâché
                actual_failure = newly_failed[0]
                
                # Si l'IA avait pointé ce noeud du doigt, c'est gagné
                if predicted_node_id == actual_failure:
                    session_hits.append(1)
                    st.toast(f"Panne du Nœud {actual_failure} anticipée !")
                else:
                    session_hits.append(0)
                    st.toast(f"Panne du Nœud {actual_failure} (IA prévoyait {predicted_node_id})")

            # AFFICHAGE 
            if t % 10 == 0:
                # Calcul de l'accuracy en temps réel
                current_acc = np.mean(session_hits) * 100 if session_hits else 0.0
                accuracy_box.metric("Précision Session", f"{current_acc:.1f}%", f"{len(session_hits)} pannes")

                node_x, node_y, node_colors, node_texts = [], [], [], []
                for n in nodes_list:
                    node_x.append(pos[n.id][0])
                    node_y.append(pos[n.id][1])
                    if n.failed: col = 'red'
                    elif n.id == predicted_node_id: col = '#FF00FF' # Prédiction IA en Magenta
                    elif n.temp > (n.params["T_max"] * 0.8): col = 'orange'
                    else: col = 'green'
                    node_colors.append(col)
                    node_texts.append(f"ID: {n.id}<br>Temp: {n.temp:.1f}°C")

                node_trace = go.Scatter(
                    x=node_x, y=node_y, mode='markers+text',
                    text=[str(n.id) for n in nodes_list], textposition="top center",
                    hovertext=node_texts, hoverinfo='text',
                    marker=dict(size=25, color=node_colors, line_width=2))

                fig = go.Figure(data=[edge_trace, node_trace], layout=go.Layout(
                    showlegend=False, hovermode='closest', margin=dict(b=0,l=0,r=0,t=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False), height=500))

                with chart_box: st.plotly_chart(fig, use_container_width=True)
                
                stats_box.markdown(f"**Step:** {t}/{steps}<br>**Pannes:** {sum(1 for n in nodes_list if n.failed)}")
                
                # Tableau des risques
                if max_risk_value > 50: msg_color = "red"
                else: msg_color = "green"
                
                pred_top_box.markdown(f"<h3 style='text-align: center; color: {msg_color};'>IA : Nœud {predicted_node_id} ({max_risk_value:.1f}%)</h3>", unsafe_allow_html=True)
                
                df_risks = pd.DataFrame({
                    "Nœud": [f"N{i}" for i in range(20)],
                    "Risque": pred_probs,
                    "Temp": [n.temp for n in nodes_list]
                }).sort_values(by="Risque", ascending=False)
                
                with pred_details_box:
                    st.dataframe(df_risks, column_config={"Risque": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1)}, use_container_width=True, height=200, hide_index=True)

                time.sleep(speed / 1000)
        
        progress_bar.progress((sim_idx + 1) / num_sims)

    #Affichage final du tableau numpy
    st.success("Session terminée !")
    
    results_array = np.array(session_hits)
    
    st.divider()
    st.header("Bilan de la Session")
    
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        final_acc = np.mean(results_array) * 100 if len(results_array) > 0 else 0
        st.metric("Accuracy Finale", f"{final_acc:.2f}%")
        st.write(f"Nombre total de pannes détectées : {len(results_array)}")
        
    with col_res2:
        st.write("Tableau Numpy des résultats (1=Succès, 0=Echec) :")
        st.code(str(results_array)) 