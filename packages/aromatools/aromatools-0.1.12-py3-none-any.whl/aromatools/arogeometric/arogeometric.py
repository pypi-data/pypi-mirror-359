#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import math
import numpy as np
import networkx as nx
import contextlib
import glob
import os
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from art import text2art
from ase.data import covalent_radii, atomic_numbers

# Diccionarios de parámetros
R_opt = {'HOMA': {'CC': 1.388, 'CN': 1.334, 'NN': 1.309, 'CO': 1.265},
         'HOMER': {'CC': 1.437, 'CN': 1.39, 'NN': 1.375, 'CO': 1.379},
         'HOMAC': {'CC': 1.392, 'CN': 1.333, 'NN': 1.318, 'CO': 1.315, 'SiSi': 2.163, 'CSi': 1.752}}

alpha = {'HOMA': {'CC': 257.7, 'CN': 93.52, 'NN': 130.33, 'CO': 157.38},
         'HOMER': {'CC': 950.74, 'CN': 506.43, 'NN': 187.36, 'CO': 164.96},
         'HOMAC': {'CC': 153.37, 'CN': 111.83, 'NN': 98.99, 'CO': 335.16, 'SiSi': 325.6, 'CSi': 115.41}}

def arogeometric():
    text_ascci = text2art("AROGEOMETRIC 1.0", font='old banner')
    print("\n" + text_ascci)
    welcome = """
    Welcome to AroGeometric — Geometric Aromaticity Index Calculator
    Authors: Fernando Martinez-Villarino and Gabriel Merino
    Cinvestav Mérida, 2024

    This tool allows you to compute geometric-based aromaticity indices for a set of molecules in .xyz files.
    You can choose among three different indices:

    • HOMA (HOMA93): 0 = non-aromatic, 1 = aromatic.
    • HOMAc:       -1 = antiaromatic, 0 = non-aromatic, 1 = aromatic.
    • HOMER:       Excited-state version of HOMAc.

    Use as: aroegeometric.py [HOMA|HOMER|HOMAc]
    """
    print(welcome)

def parse_xyz(file_xyz):
    with open(file_xyz, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    natoms = int(lines[0])
    atoms = []
    for i in range(2, 2 + natoms):
        parts = lines[i].split()
        if len(parts) < 4:
            continue
        symbol = parts[0].capitalize()
        if symbol == 'H':
            continue
        try:
            x, y, z = map(float, parts[1:4])
            atoms.append((symbol, x, y, z))
        except ValueError:
            print(f"Error: Invalid coordinates at line {i+1}.")
            sys.exit(1)
    return atoms

def build_graph(atoms, tol=0.15):
    G = nx.Graph()
    for idx, (sym, _, _, _) in enumerate(atoms):
        G.add_node(idx, element=sym)
    for i in range(len(atoms)):
        sym1, x1, y1, z1 = atoms[i]
        r1 = covalent_radii[atomic_numbers[sym1]]
        for j in range(i + 1, len(atoms)):
            sym2, x2, y2, z2 = atoms[j]
            r2 = covalent_radii[atomic_numbers[sym2]]
            dist = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)
            if dist <= r1 + r2 + tol:
                bond_type = ''.join(sorted(sym1 + sym2))
                G.add_edge(i, j, length=dist, bond_type=bond_type)
    return G

def compute_index(G, atoms, index_type, filename):
    print(f"\nProcessing: {filename}")
    rings = nx.minimum_cycle_basis(G)
    print(f"Number of rings detected: {len(rings)}")
    ring_indices = []

    for idx, ring in enumerate(rings, start=1):
        ring_atoms = ring + [ring[0]]
        ring_bonds = []

        for i in range(len(ring)):
            a1, a2 = ring_atoms[i], ring_atoms[i+1]
            if G.has_edge(a1, a2):
                data = G[a1][a2]
                bond_type = data['bond_type']
                dist = data['length']

                if bond_type not in R_opt[index_type]:
                    continue

                print(f"Ring {idx}: bond {bond_type} with distance {dist:.4f} Å")

                if bond_type == 'SiSi':
                    print(f"Ring {idx} contains Si-Si bond: distance = {dist:.4f} Å")

                Ropt = R_opt[index_type][bond_type]
                a = alpha[index_type][bond_type]
                ring_bonds.append((bond_type, dist, Ropt, a))

        if not ring_bonds:
            print(f"Ring {idx}: No valid bonds for index {index_type}.")
            continue

        n = len(ring_bonds)
        total = sum(a * (dist - Ropt)**2 for _, dist, Ropt, a in ring_bonds)
        index_value = 1.0 - (1.0 / n) * total
        print(f"{index_type} index for ring {idx}: {index_value:.4f}")
        ring_indices.append((idx, index_value))

    return rings, ring_indices

def draw_molecular_graph3D(G, atoms, rings, project_name, ring_indices):
    index_lookup = dict(ring_indices)
    node_xyz = []
    node_labels = []
    pos = {}  # posiciones aproximadas basadas en coordenadas 2D proyectadas
    for idx, (_, x, y, z) in enumerate(atoms):
        pos[idx] = (x, y)  # solo tomamos x-y para un gráfico 2D

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=False, node_size=300, node_color='lightblue', edge_color='gray')
    
    labels = {i: atoms[i][0] for i in range(len(atoms))}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)

    for i, ring in enumerate(rings, start=1):
        x_coords = [pos[a][0] for a in ring]
        y_coords = [pos[a][1] for a in ring]
        centroid = (sum(x_coords) / len(ring), sum(y_coords) / len(ring))
        index_value = index_lookup.get(i, None)
        if index_value is not None:
            # label = f"{i} ({index_value:.3f})"
            # plt.text(centroid[0], centroid[1], label, fontsize=10, fontweight='bold', color='red')

    plt.title(f"Molecular Graph: {project_name}")
    plt.axis('off')
    plt.savefig("graph_output.png", dpi=300)
    plt.close()

def draw_molecular_graph_3d(G, atoms, index_lookup=None, project_name="Molecule"):
    node_xyz = []
    node_labels = []
    
    for idx, (symbol, x, y, z) in enumerate(atoms):
        node_xyz.append((x, y, z))
        node_labels.append(symbol)

    edge_x = []
    edge_y = []
    edge_z = []

    for edge in G.edges():
        x0, y0, z0 = node_xyz[edge[0]]
        x1, y1, z1 = node_xyz[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        edge_z += [z0, z1, None]

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='gray', width=2),
        hoverinfo='none'
    )

    node_x = [x for x, y, z in node_xyz]
    node_y = [y for x, y, z in node_xyz]
    node_z = [z for x, y, z in node_xyz]

    text_labels = []
    for i, label in enumerate(node_labels):
        text = label
        text_labels.append(text)

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        marker=dict(size=6, color='skyblue', line=dict(width=1)),
        text=text_labels,
        textposition="top center",
        hoverinfo='text'
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=f"3D Molecular Graph: {project_name}",
        showlegend=False,
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )
    fig.show()

def main():
    if len(sys.argv) != 2:
        arogeometric()
        sys.exit(1)

    index_type = sys.argv[1].upper()
    if index_type not in R_opt:
        print("Error: Invalid index type. Choose from HOMA, HOMER, HOMAC.")
        sys.exit(1)

    xyz_files = sorted(glob.glob("*.xyz"))
    if not xyz_files:
        print("No .xyz files found in the current directory.")
        sys.exit(1)

    ascci_title = text2art("AroGeometric", font='big')

    print()
    print(f"AroGeometric 2025, output file — {index_type}")
    print(ascci_title)
    print("Theoretical and Computational Chemistry Group")
    print("Centro de Investigacion y de Estudios Avanzados — Unidad Merida")
    print("Merida, Yucatan, Mexico\n")

    print("---------------------------------Cite this work as---------------------------------")
    print("AroGeometric 2025, Fernando Martinez-Villarino and G. Merino, Cinvestav, Merida, YUC, Mexico, 2025")
    print("-----------------------------------------------------------------------------------\n")

    print("Copyright (C) 1943, Cinvestav. All Rights Reserved")

    print(f"Total XYZ files found: {len(xyz_files)}\n")

    for file_xyz in xyz_files:
        atoms = parse_xyz(file_xyz)
        G = build_graph(atoms)
        rings, ring_indices = compute_index(G, atoms, index_type, file_xyz)
        base_name = os.path.splitext(os.path.basename(file_xyz))[0]
        draw_molecular_graph(G, atoms, rings, base_name, ring_indices)

    print("\n")
    print("************************************ AroGeometric terminated normally! ************************************\n")

