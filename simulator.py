import streamlit as st
import functions
import time
import random
import networkx as nx
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Simulateur")

st.title("Simulateur Réseau")

col1, col2 = st.columns([1, 4])
with col1:
    run = st.checkbox("Activer la Simulation en boucle")
    steps = st.slider("Durée par simulation", 100, 2000, 500)
    speed = st.slider("Vitesse (pause ms)", 0, 200, 50) 
    
    sim_info_box = st.empty()
    stats_box = st.empty()

with col2:
    chart_box = st.empty() 

if run:
    sim_counter = 1
    
    while True:
        sim_info_box.info(f"Lancement de la simulation #{sim_counter}...")
        number = 20
        #nodes_list = [node.Node(i, functions.generate_random_params()) for i in range(number)]
        nodes_list = functions.import_nodes("params.txt")
        nodes_dict = {n.id: n for n in nodes_list}
        
        connections = [(i, i+1) for i in range(number-1)]
        for _ in range(5):
            a, b = random.randint(0, number-1), random.randint(0, number-1)
            if a != b: connections.append((a, b))
        
        neighbors_map = functions.build_adjacency_list(connections)

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

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')

        for t in range(1, steps + 1):
            for n in nodes_list:
                f, t_avg, nc = functions.get_node_context(n.id, neighbors_map, nodes_dict)
                n.update_physics(t, f, t_avg, nc)
                n.check_failure()

            if t % 10 == 0:
                node_x = []
                node_y = []
                node_colors = []
                node_texts = []
                
                for n in nodes_list:
                    node_x.append(pos[n.id][0])
                    node_y.append(pos[n.id][1])
                    
                    if n.failed:
                        col = 'red'
                    elif n.temp > (n.params["T_max"] * 0.8):
                        col = 'orange'
                    else:
                        col = 'green'
                    node_colors.append(col)
                    
                    txt = f"ID: {n.id}<br>Temp: {n.temp:.1f}°C<br>Charge: {n.load:.1f}"
                    node_texts.append(txt)

                node_trace = go.Scatter(
                    x=node_x, y=node_y,
                    mode='markers+text',
                    text=[str(n.id) for n in nodes_list], 
                    textposition="top center",
                    hoverinfo='text',
                    hovertext=node_texts,
                    marker=dict(
                        showscale=False,
                        color=node_colors,
                        size=20, 
                        line_width=2))

                fig = go.Figure(data=[edge_trace, node_trace],
                             layout=go.Layout(
                                showlegend=False,
                                hovermode='closest',
                                margin=dict(b=0,l=0,r=0,t=0),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                height=600
                             ))

                with chart_box:
                    st.plotly_chart(fig, use_container_width=True)

                stats_box.markdown(f"**Simu:** #{sim_counter} | **Step:** {t}/{steps} | **Pannes:** {sum(1 for n in nodes_list if n.failed)}")
                
                time.sleep(speed / 1000)
        
        sim_counter += 1