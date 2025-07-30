import click
import importlib.resources
from .nomenclature import glycan_nomenclature_to_smiles
from .reactions import generate_reactions
from .utils import sphingomapkey_to_reactions, sphingomapkey_to_structures
import os

@click.group()
def cli():
    pass

@cli.command()
@click.argument("nomenclature")
@click.option("--nacyl", required=True, help="n-acyl chain SMILES")
@click.option("--sphingoid", required=True, help="sphingoid base SMILES")
def convert(nomenclature, nacyl, sphingoid):
    """
    Convert glycan nomenclature to SMILES
    """
    smiles = glycan_nomenclature_to_smiles(nomenclature, nacyl=nacyl, sphingoid=sphingoid)
    click.echo(smiles)

@cli.command()
@click.argument("nomenclature")
@click.option("--nacyl", required=True)
@click.option("--sphingoid", required=True)
@click.option("--output-folder", required=True)
def generate(nomenclature, nacyl, sphingoid, output_folder):
    """
    Generate the reaction producing the compound
    """
    os.makedirs(output_folder, exist_ok=True)
    generate_reactions(nomenclature, nacyl=nacyl, sphingoid=sphingoid, output_tsv = os.path.join(output_folder, 'reactions.tsv'))

@cli.command()
@click.option(
    "--input-xls",
    default=importlib.resources.files("glycosphingotool.assets").joinpath('SphingomapkeyV1.4.xls'),
    type=click.Path(exists=True),
    required=True,
    help="Path to SphingoMapKey Excel file",
)
@click.option(
    "--output-folder",
    type=click.Path(file_okay=False, dir_okay=True),
    required=True,
    help="Directory to store outputs"
)
@click.option(
    "--nacyl",
    default="CCCCCCCCCCCCCCC",
    help="SMILES for n-acyl chain"
)
@click.option(
    "--sphingoid",
    default="[C@H](O)/C=C/CCCCCCCCCCCCC",
    help="SMILES for sphingoid base"
)
def process_all(input_xls, output_folder, nacyl, sphingoid):
    """
    Process the full SphingoMapKey input and generate reactions + structures
    """

    os.makedirs(output_folder, exist_ok=True)
    
    click.echo(f"Processing full SphingoMapKey from {input_xls}")

    # run reactions
    sphingomapkey_to_reactions(
        input_xls=input_xls,
        nacyl=nacyl,
        sphingoid=sphingoid,
        output_tsv=os.path.join(output_folder, 'sphingomapkey with reaction structures.tsv')
    )

    # run structures
    sphingomapkey_to_structures(nacyl=nacyl,
                                sphingoid=sphingoid, 
                                output_tsv=os.path.join(output_folder, 'SphingomapkeyV1.4.tsv'))
    structures_path = os.path.join(output_folder, 'SphingomapkeyV1.4.tsv')
    click.echo(f"Structures saved to {structures_path}")

if __name__ == "__main__":
    cli()