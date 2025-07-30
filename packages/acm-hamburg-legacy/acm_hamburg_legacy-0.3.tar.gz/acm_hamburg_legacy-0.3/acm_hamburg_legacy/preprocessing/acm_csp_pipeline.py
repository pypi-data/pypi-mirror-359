from nerdd_module.preprocessing import (
    FilterByElement,
    FilterByWeight,
    GetParentMol,
    Pipeline,
    StandardizeWithCsp,
)

from .canonicalize_tautomer import CanonicalizeTautomer
from .do_smiles_roundtrip import DoSmilesRoundtrip

__all__ = ["AcmCspPipeline"]


class AcmCspPipeline(Pipeline):
    def __init__(
        self,
        min_weight=150,
        max_weight=1500,
        allowed_elements=[
            "H",
            "B",
            "C",
            "N",
            "O",
            "F",
            "Si",
            "P",
            "S",
            "Cl",
            "Se",
            "Br",
            "I",
        ],
        remove_invalid_molecules=False,
        remove_stereo=True,
    ):
        super().__init__(
            steps=[
                DoSmilesRoundtrip(remove_stereo=remove_stereo),
                StandardizeWithCsp(),
                GetParentMol(),
                FilterByWeight(
                    min_weight=min_weight,
                    max_weight=max_weight,
                    remove_invalid_molecules=remove_invalid_molecules,
                ),
                FilterByElement(
                    allowed_elements, remove_invalid_molecules=remove_invalid_molecules
                ),
                CanonicalizeTautomer(
                    remove_stereo=remove_stereo,
                    remove_invalid_molecules=remove_invalid_molecules,
                ),
                DoSmilesRoundtrip(remove_stereo=False),
            ]
        )
