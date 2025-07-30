import pandas as pd
import importlib.resources

def load_residue_data(
    nacyl=None,
    sphingoid=None
    ):
    """
    Loads residue data and returns:
      - residues_smiles: dict for glycan_nomenclature_to_smiles
      - residues_properties: dict for reaction processing

    Parameters
    ----------
    path : str
        TSV file with residue definitions
    nacyl : str
        SMILES for n-acyl chain (replaces [C:1000001])
    sphingoid : str
        SMILES for sphingoid base (replaces [C:1000002])

    Returns
    -------
    residues_smiles : dict
    residues_properties : dict
    """
    df = pd.read_csv(importlib.resources.files("glycosphingotool.data").joinpath("residue_to_sugar_nucleotide.tsv"), sep="\t")

    # build residues_smiles
    smiles_residues = df[['Residue', 'SMILES residue']].dropna()
    smiles_corrected = [
        s.replace('(*)','').replace('*','')
         .replace('[C:1000001]', nacyl)
         .replace('[C:1000002]', sphingoid)
        for s in smiles_residues['SMILES residue']
    ]
    residue_names = [
        n.replace('Ac-O-9-','AcONine')
        for n in smiles_residues['Residue']
    ]
    residues_smiles = dict(zip(residue_names, smiles_corrected))

    # build residues_properties
    residues_properties = {}
    for i, row in df.iterrows():
        residues_properties[row['Residue']] = {
            'chebi1': row.get('CHEBI ID participant 1', None),
            'smiles1': row.get('SMILES participant 1', None),
            'name1': row.get('Name participant 1', None),
            'chebi2': row.get('CHEBI ID participant 2', None),
            'smiles2': row.get('SMILES participant 2', None),
            'name2': row.get('Name participant 2', None),
        }

    return residues_smiles, residues_properties