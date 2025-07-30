import re
import networkx as nx
from rdkit import Chem
from .dataio import load_residue_data

def glycan_nomenclature_to_smiles(nomenclature_string, nacyl='CCCCCCCCCCCCCCC', sphingoid='[C@H](O)/C=C/CCCCCCCCCCCCC'):
    # Change the part that screws up the regular expression:

    # get the structures of the residues
    residues_smiles, _ = load_residue_data(nacyl=nacyl, sphingoid=sphingoid)

    nomenclature_string = nomenclature_string.replace('Ac-O-9-','AcONine') 

    graph, labeldict = parse_to_graph(nomenclature_string)
    
    if not graph:
        return 'No match to Cer pattern'
    # nx.draw_planar(graph,labels=labeldict, with_labels = True)
    # plt.show()

    if nomenclature_string.endswith('GlcCer'):
        root_ceramide = 'GlcCer'
    elif nomenclature_string.endswith('GalCer'):
        root_ceramide = 'GalCer'

    traversal_result = custom_dfs(graph, root_ceramide)
    #print("Traversal Result:", traversal_result)

    already_met = []
    for index, node in enumerate(traversal_result):
        if node not in already_met:
            #print(node)
            #print(labeldict[node])
            if labeldict[node] == root_ceramide:
                mol_ceramide = Chem.MolFromSmiles(residues_smiles[root_ceramide], sanitize=False)
            else:
                #Chem.MolToSmiles(mol_ceramide))
                smiles_sugar = residues_smiles[labeldict[node][:-3]]
                smiles_sugar = add_prefix_to_atom_map(smiles_sugar, str(node)+'0')
                mol_sugar = Chem.MolFromSmiles(smiles_sugar, sanitize=False)
                #print(Chem.MolToSmiles(mol_sugar))
                #print()
                combined_mol = Chem.CombineMols(mol_ceramide, mol_sugar)

                combined_mol = Chem.RWMol(combined_mol)

                connection_ind_single_sugar = int(str(node)+'0'+labeldict[node][-3])

                if node==1:
                    connection_index_ceramide = int('2'+labeldict[node][-1])
                else:
                    connection_index_ceramide = int(str(traversal_result[index-1])+'02'+labeldict[node][-1])
                
                bondout = find_atom_by_map_number(combined_mol, connection_ind_single_sugar)
                bondin = find_atom_by_map_number(combined_mol, connection_index_ceramide)
                if bondout is None:
                    print(labeldict[node][:-3])
                if bondin is None:
                    print(nomenclature_string)
                combined_mol.AddBond(bondout, bondin, Chem.BondType.SINGLE)
                
                # Finalize the molecule
                mol_ceramide = combined_mol.GetMol()

                # Sanitize the molecule to update chemical properties
                #Chem.SanitizeMol(mol_ceramide)
                #mol_ceramide = combined_mol.GetMol()

            already_met.append(node)

    # Convert back to SMILES to see the result
    result_smiles = Chem.MolToSmiles(mol_ceramide)

    # remove any atom mapping from SMILES besides the atom mapping for C:1000001 and C:1000002 - connection points for lipids. 
    # C:1000001 and C:1000002 have to be turned into * (for different possible lipids)
    result_smiles = clean_smiles(result_smiles)

    return result_smiles


def parse_to_graph(input_string):
    # Regex to capture molecule parts and brackets
    parts = re.findall(r'([A-Za-z]+\d+-\d+)|([\{\[\(\)\]\}])', input_string)
    parts = [p for sub in parts for p in sub if p]
    parts.reverse()
    node_ind = 1
    graph = nx.DiGraph()  # Using directed graph to capture the flow
    stack = []  # To manage hierarchy and backtracking
    labels = {}

    # Extract the core molecule (end of the string, after the last bracket)
    match = re.search(r'[A-Z][a-z]*Cer$', input_string)
    if not match:
        return None, None
    
    core_molecule = match.group()
    labels[core_molecule]=core_molecule
    
    graph.add_node(core_molecule)

    # Initially, set the last compound to the core molecule
    last_compound = core_molecule

    for part in parts:
        if part in '{}[]()':  # Handle brackets
            if part in '}])':
                stack.append(last_compound)
            elif part in '{[(' and stack:
                last_compound = stack.pop()
            continue

        # Extract compound and indexes
        current_compound_name = part

        graph.add_edge(last_compound, node_ind)
        
        # Move "down" in the hierarchy
        last_compound = node_ind
        labels[node_ind]=current_compound_name
        node_ind+=1

    nx.set_node_attributes(graph, labels, "labels")
    return graph, labels


def custom_dfs(graph, node, visited=None, result=None):
    """
    depth first graph search
    identify the order in which the nodes have to be connected to the structure
    """
    if visited is None:
        visited = set()  # To keep track of visited nodes
    if result is None:
        result = []  # To store the traversal order

    # Mark the current node as visited and add to the result list
    visited.add(node)
    result.append(node)  # Process the node

    # Recur for all the neighbors (children in a tree context)
    for neighbor in graph.neighbors(node):
        if neighbor not in visited:
            custom_dfs(graph, neighbor, visited, result)
            result.append(node)  # Add the node again on return to represent backtracking

    return result

# Function to add 90 in front of atom map numbers
def add_prefix_to_atom_map(smiles, prefix):
    # Regular expression to find atom map numbers (e.g., :1, :23)
    modified_smiles = re.sub(r':(\d+)', lambda x: f':{prefix}{x.group(1)}', smiles)
    return modified_smiles

# Define a function to find atom by its mapping number
def find_atom_by_map_number(mol, map_number):
    #print(map_number)
    for atom in mol.GetAtoms():
        if atom.GetAtomMapNum() == map_number:
            return atom.GetIdx()
    print('atom number not found', map_number, Chem.MolToSmiles(mol))

def clean_smiles(smiles):
    # Regular expression to match atoms with optional stereochemistry and atom numbers
    # This now also ensures that stereochemistry indicators keep brackets
    atom_number_regex = r'\[([A-Z][a-z]?\@?\@?[H\d]*):(\d+)\]'

    # Function to handle atom numbers and stereochemistry
    def keep_selected_atoms(match):
        atom, number = match.groups()
        # Keep the full atom (with number) for C:1000001 and C:1000002
        if f'{atom}:{number}' in ['C:1000001', 'C:1000002']:
            return f'[{atom}:{number}]'
        # If the atom has stereochemistry (@ or @@), keep the brackets
        elif '@' in atom:
            return f'[{atom}]'
        # Otherwise, return the atom without brackets
        else:
            return atom

    # Substitute all atom numbers with the appropriate form
    cleaned_smiles = re.sub(atom_number_regex, keep_selected_atoms, smiles)

    cleaned_smiles = cleaned_smiles.replace('C:1000001','*').replace('C:1000002','*')
    cleaned_smiles = cleaned_smiles.replace('CHO', 'CO').replace('CH2O', 'CO').replace('CH2','C')

    return cleaned_smiles

