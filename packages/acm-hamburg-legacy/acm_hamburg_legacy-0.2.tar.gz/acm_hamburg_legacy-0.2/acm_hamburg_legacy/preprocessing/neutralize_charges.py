from typing import List, Tuple

from nerdd_module.preprocessing import Step
from rdkit.Chem import AllChem, Mol

from acm_hamburg_legacy.rule_sets.neutralization_reactions import neutralization_reactions


class NeutralizeCharges(Step):
    """
    Neutralizes the molecules according to the patterns defined in
    ruleSets.neutralizationPatterns.
    """

    def __init__(self):
        super().__init__()

    def _run(self, mol: Mol) -> Tuple[Mol, List[str]]:
        errors = []
        for reactant, product in neutralization_reactions:
            while mol and mol.HasSubstructMatch(reactant):
                rms = AllChem.ReplaceSubstructs(mol, reactant, product)
                mol = rms[0]
                try:
                    mol.UpdatePropertyCache()
                    if not mol:
                        errors.append("N1")
                except ValueError:
                    mol = None

        return mol, errors
