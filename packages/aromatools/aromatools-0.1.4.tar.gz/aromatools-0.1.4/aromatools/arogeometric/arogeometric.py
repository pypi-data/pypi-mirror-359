#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import math
import numpy as np
import networkx as nx
import contextlib
import glob
import os
import time
import getpass
from ase.data import covalent_radii, atomic_numbers
from art import text2art

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

def build_graph(atoms, tol=0.45):
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
    for idx, ring in enumerate(rings, start=1):
        ring_atoms = ring + [ring[0]]
        ring_bonds = []
        bond_types_in_ring = []

        for i in range(len(ring)):
            a1, a2 = ring_atoms[i], ring_atoms[i+1]
            if G.has_edge(a1, a2):
                data = G[a1][a2]
                bond_type = data['bond_type']
                dist = data['length']

                print(f"Ring {idx}: bond {bond_type} with distance {dist:.4f} Å")

                if bond_type == 'SiSi':
                    print(f"Ring {idx} contains Si-Si bond: distance = {dist:.4f} Å")

                if bond_type not in R_opt[index_type]:
                    continue

                Ropt = R_opt[index_type][bond_type]
                a = alpha[index_type][bond_type]
                bond_types_in_ring.append(bond_type)
                ring_bonds.append((bond_type, dist, Ropt, a))

        if not ring_bonds:
            print(f"Ring {idx}: No valid bonds for index {index_type}.")
            continue

        n = len(ring_bonds)
        total = sum(a * (dist - Ropt)**2 for _, dist, Ropt, a in ring_bonds)
        index_value = 1.0 - (1.0 / n) * total
        print(f"{index_type} index for ring {idx}: {index_value:.4f}")

def get_session_info():
    init_time = time.strftime("%H:%M:%S", time.localtime())
    work_direc = os.getcwd()
    user = getpass.getuser()

    session_info = f"""
    Initiation time:      {init_time}
    Working directory:    {work_direc}
    User:                 {user}
    """
    return session_info

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

    ascci_title = text2art("AROGEOMETRIC", font='big')
    session_info = get_session_info()
    
    with open("index.dat", "w") as log_file:
        with contextlib.redirect_stdout(log_file):
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
            print("Session information:")
            print(session_info + "\n")

            print(f"Total XYZ files found: {len(xyz_files)}\n")

            for file_xyz in xyz_files:
                atoms = parse_xyz(file_xyz)
                G = build_graph(atoms)
                compute_index(G, atoms, index_type, file_xyz)
                
            print("\n")
            print("************************************ AroGeometric terminated normally! ************************************\n")

    print("All calculations completed and saved to 'index.dat'")

