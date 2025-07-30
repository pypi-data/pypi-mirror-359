import pandas as pd
from rdkit import Chem
from rxnsmiles2rinchi import RInChI
import importlib.resources
from tqdm import tqdm

from .reactions import rxnsmiles_to_rinchi, enumerate_reactions_as_glyconomenclature, nomenclature_reaction_to_biochem_structures, nomenclature_reaction_to_full_reaction
from .nomenclature import glycan_nomenclature_to_smiles
from .dataio import load_residue_data

tqdm.pandas()

def sphingomapkey_to_reactions(
    input_xls=importlib.resources.files("glycosphingotool.assets").joinpath('SphingomapkeyV1.4.xls'),
    output_tsv='sphingomapkey with reaction structures.tsv',
    residues_properties=None,
    nacyl=None,
    sphingoid=None
):
    """
    Process the SphingoMapKey Excel, transform to reactions, expand to rxnSMILES
    and add RInChI + RInChIKey columns directly in a pandas DataFrame.

    Parameters
    ----------
    input_xls : str
        Path to the SphingoMapKey excel file.
    residues_properties : dict
        Dictionary describing sugar nucleotide properties (e.g. from residue_to_sugar_nucleotide.tsv)
    nacyl : str
        SMILES of the n-acyl chain
    sphingoid : str
        SMILES of the sphingoid base

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - glyco_nomenclature
        - rxnSMILES
        - RInChI
        - RInChIKey
    """

    _, residues_properties = load_residue_data(nacyl=nacyl, sphingoid=sphingoid)

    print("Enumerating reactions as glycan nomenclature")

    df = pd.read_excel(input_xls, skiprows=2)
    compounds = df['Formula'].dropna().tolist()

    total_reactions = []
    for compound in tqdm(compounds):
        reactions = enumerate_reactions_as_glyconomenclature(compound)
        total_reactions.extend(reactions)

    # store results in DataFrame instead of file
    results_df = pd.DataFrame(columns=["glyco_nomenclature", "rxnSMILES"])

    print("Assigning names and structures")
    for reaction in tqdm(total_reactions):
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
    
    results_df.drop_duplicates(subset=["glyco_nomenclature"], inplace=True)
    print('After dropping duplicate glycan nomenclature reactions', len(results_df))
    
    # add RInChI and RInChIKey columns
    rinchi=RInChI()
    print("Generating RInChI")
    results_df[["RInChI", "RInChIKey"]] = results_df.progress_apply(
        lambda row: rxnsmiles_to_rinchi(row["rxnSMILES"], rinchi),
        axis=1,
        result_type="expand"
    )

    results_df.drop_duplicates(subset=['RInChIKey'], inplace=True)

    print('After dropping duplicate RInChIKey', len(results_df))
    results_df.to_csv(output_tsv, sep='\t', index=False)
    return results_df

def sphingomapkey_to_structures(
    input_xls=importlib.resources.files("glycosphingotool.assets").joinpath('SphingomapkeyV1.4.xls'),
    output_tsv='SphingomapkeyV1.4.tsv', 
    nacyl=None, 
    sphingoid=None
):
    """
    Processes the sphingomapkey Excel and assigns SMILES/InChIKey
    to every compound with Cer, GlcCer, GalCer
    and writes to a TSV.

    Parameters
    ----------
    input_xls : str
        Path to input Excel
    output_tsv : str
        Path to TSV to save results
    """

    df = pd.read_excel(input_xls, skiprows=2)
    df.dropna(subset=['Formula'], inplace=True)

    # remove any empty column
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # remove base Cer entries
    df = df[~df['Formula'].isin(['Cer', 'GlcCer', 'GalCer'])]

    df['SMILES'] = df.apply(
        lambda row: glycan_nomenclature_to_smiles(row['Formula'], nacyl=nacyl, sphingoid=sphingoid)
        if 'Cer' in row['Formula'] else 'NA',
        axis=1
    )

    df = df[df['SMILES'] != 'NA']

    df['InChIKey'] = df['SMILES'].apply(
        lambda x: Chem.MolToInchiKey(Chem.MolFromSmiles(x))
    )

    df.to_csv(output_tsv, sep="\t", index=False)
    print(f"Wrote structures to {output_tsv}")