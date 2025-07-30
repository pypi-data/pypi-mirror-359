import re
import pandas as pd
from rxnsmiles2rinchi import RInChI
from .dataio import load_residue_data
from .nomenclature import glycan_nomenclature_to_smiles
from rdkit import Chem
from rxnsmiles2rinchi import RInChI

def generate_reactions(compound_glyconomenclature, 
                       nacyl=None, 
                       sphingoid=None,
                       output_tsv = 'reactions.tsv'):
    
    _, residues_properties = load_residue_data(nacyl=nacyl, sphingoid=sphingoid)

    total_reactions = []
    reactions = enumerate_reactions_as_glyconomenclature(compound_glyconomenclature)
    total_reactions.extend(reactions)

    # store results in DataFrame instead of file
    results_df = pd.DataFrame(columns=["glyco_nomenclature", "rxnSMILES"])

    for reaction in total_reactions:
        rxnsmiles = nomenclature_reaction_to_biochem_structures(
            reaction,
            residues_properties,
            nacyl=nacyl,
            sphingoid=sphingoid,
        )
        reaction_cmp_names = nomenclature_reaction_to_full_reaction(
            reaction,
            residues_properties
        )
        results_df.loc[len(results_df)] = [reaction_cmp_names, rxnsmiles]
    
    rinchi=RInChI()
    results_df.drop_duplicates(subset=["glyco_nomenclature"], inplace=True)
        # add RInChI and RInChIKey columns
    results_df[["RInChI", "RInChIKey"]] = results_df.progress_apply(
        lambda row: rxnsmiles_to_rinchi(row["rxnSMILES"], rinchi),
        axis=1,
        result_type="expand"
    )

    results_df.drop_duplicates(subset=['RInChIKey'], inplace=True)

    print('After dropping duplicate RInChIKey', len(results_df))
    results_df.to_csv(output_tsv, sep='\t', index=False)

#________________________________________________________________________
# Enumerate reactions as glyconomenclature
#________________________________________________________________________

def enumerate_reactions_as_glyconomenclature(compound_glyconomenclature):

    final_result = []
    final_single_sugars = []

    results, single_sugars, intermediates = process_compound(compound_glyconomenclature)
    final_result.extend(results)
    final_single_sugars.extend(single_sugars)
    non_decomposed_intermediates = set(intermediates)-set([compound_glyconomenclature])
    
    # Process the compounds
    while len(non_decomposed_intermediates)>0:
        intermediates_total = []
        for intermediate in non_decomposed_intermediates:
            results, single_sugars, intermediates = process_compound(intermediate)
            final_result.extend(results)
            final_single_sugars.extend(single_sugars)
            intermediates_total.extend(intermediates)
        non_decomposed_intermediates = set(intermediates_total)-set(compound_glyconomenclature)-set(non_decomposed_intermediates)

    def unique( seq ):
        seen = set()
        for item in seq:
            if item not in seen:
                seen.add( item )
                yield item

    final_result[:] = unique(final_result)
    #print(f'reactions_enumerated for {compound_glyconomenclature}:', len(final_result))

    return final_result

def process_compound(compound):
    reactions = []
    single_sugars = []
    intermediates = []
    # Find the first part with #-# and split based on it
    match = re.search(r'(.*?)([\d]+\-[\d]+)(.*)', compound)
    if match:

        first_part = match.group(1)
        rest = match.group(3)

        # Create the reaction format
        intermediate = clean_reaction(rest)
        reaction = f"{first_part} + {intermediate} => {compound}".replace('  ', ' ')
        
        #reaction = clean_reaction(reaction)
        reactions.append(reaction)
        single_sugars.append(first_part)
        intermediates.append(intermediate)
    
    match_branch_1 = re.search(r'(.*)(\[)(.*?)([\d]+\-[\d]+)(.*)', compound)
    if match_branch_1:
        pre_part = match_branch_1.group(1)
        first_part = match_branch_1.group(3)
        rest = match_branch_1.group(5)

        # Create the reaction format
        intermediate = f"{pre_part}[{rest}"
        intermediate = clean_reaction(intermediate)
        reaction = f"{first_part} + {intermediate} => {compound}"
        
        #reaction = clean_reaction(reaction)
        reactions.append(reaction)
        single_sugars.append(first_part)
        intermediates.append(intermediate)

    match_branch_2_options = re.findall(r'(\()(.*?)([\d]+\-[\d]+)', compound)
    for match_branch_2 in match_branch_2_options:
        match_sugar = match_branch_2[1]
        match_remaining = compound.replace(''.join(match_branch_2), '(').replace('()', '')
        intermediate = match_remaining
        intermediate = clean_reaction(intermediate)
        reaction = f"{match_sugar} + {intermediate} => {compound}"
        
        #reaction = clean_reaction(reaction)
        reactions.append(reaction)
        single_sugars.append(match_sugar)
        intermediates.append(intermediate)

    match_branch_3 = re.search(r'(.*)(\{[a-zA-Z]+[\d\-\d]+)(.*)', compound)
    if match_branch_3:
        pre_part = match_branch_3.group(1)
        first_part = match_branch_3.group(2)
        rest = match_branch_3.group(3)

        # Create the reaction format
        intermediate = f"{pre_part}{{{rest}"
        intermediate = clean_reaction(intermediate)
        reaction = f"{first_part[1:-3]} + {intermediate} => {compound}".replace('()', '')
        
        #reaction = clean_reaction(reaction)
        reactions.append(reaction)
        single_sugars.append(first_part[1:-3])
        intermediates.append(intermediate)

    if any(i.startswith('(') for i in single_sugars):
        print(compound)
        print(single_sugars)
        exit()

    return reactions, single_sugars, intermediates

def clean_reaction(text):
    if text.startswith('('):
        text = text.replace('(','',1).replace(')','',1)
    if text.startswith('[') :
        text = text.replace('[','',1).replace(']','',1)
    if text.startswith('{') :
        text = text.replace('{','',1).replace('}','',1)

    # Replace [...]
    text = re.sub(r'\[([^\[\]()]+)\]', r'(\1)', text)
    # Replace [(...)...]
    text = re.sub(r'\[\((.*?)\)(.*?)\]', r'(\1\2)', text)
    # Replace {[...()...]...}
    text = re.sub(r'\{\[([^{}]*)\]([^{}]*)\}', r'[\1\2]', text)
    # Replace {...()...} without square brackets inside
    text = re.sub(r'\{([^{}\[\]]*\([^{}\[\]]*\)[^{}\[\]]*)\}', r'[\1]', text)   

    if text.startswith('[') or text.startswith('{') or text.startswith('('):
        text = clean_reaction(text)

    return text

#________________________________________________________________________
# Convert reaction into structure
#________________________________________________________________________

def nomenclature_reaction_to_biochem_structures(nomenclature_reaction, 
                                                residues_properties, 
                                                nacyl=None, 
                                                sphingoid=None):
    reactant_smiles = []
    product_smiles = []

    reactants = nomenclature_reaction.split(' => ')[0].split(' + ')
    product = nomenclature_reaction.split(' => ')[1]

    smiles_NDP_sugar = residues_properties[reactants[0]]['smiles1']
    smiles_NDP = residues_properties[reactants[0]]['smiles2']

    reactant_smiles.append(smiles_NDP_sugar)
    reactant_smiles.append(glycan_nomenclature_to_smiles(reactants[1],nacyl=nacyl, sphingoid=sphingoid))

    product_smiles.append(smiles_NDP)
    product_smiles.append(glycan_nomenclature_to_smiles(product,nacyl=nacyl, sphingoid=sphingoid))
    product_smiles.append('[H+]')
    try:
        return '.'.join(reactant_smiles)+'>>'+'.'.join(product_smiles)
    except:
        print(nomenclature_reaction, reactant_smiles, product_smiles)

def nomenclature_reaction_to_full_reaction(nomenclature_reaction, residues_properties):
    reactant_names = []
    product_names = []

    reactants = nomenclature_reaction.split(' => ')[0].split(' + ')
    product = nomenclature_reaction.split(' => ')[1]

    name_NDP_sugar = residues_properties[reactants[0]]['name1']
    name_NDP = residues_properties[reactants[0]]['name2']

    reactant_names.append(name_NDP_sugar)
    reactant_names.append(reactants[1])

    product_names.append(name_NDP)
    product_names.append(product)
    product_names.append('H+')

    return ' + '.join(reactant_names)+' => '+' + '.join(product_names)


## RINCHI

def rxnsmiles_to_rinchi(SMILES, rinchi):
    try:
        return rinchi.rxn_smiles_to_rinchi_rinchikey(SMILES)
    except:
        reactants = SMILES.split('>>')[0].split('.')
        products = SMILES.split('>>')[1].split('.')
        for reactant in reactants:
            molobj = Chem.MolFromSmiles(reactant)
            if not molobj:
                print(reactant)
        for product in products:
            molobj = Chem.MolFromSmiles(product)
            if not molobj:
                print(product)

        return None, None
