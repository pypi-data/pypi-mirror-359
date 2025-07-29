"""

.. module author:: Anke Wilm <wilm@zbh.uni-hamburg.de>

"""

import pandas as pd
import os
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from cheminformatics.AcmErrors import AcmEnvVarError


def _make_xyz(mol, path):
    """
    Function that creates xyz coords and writes them in a file satisfying the criteria fo rorca input

    :param mol: molecule object
    :param: path: path in which the xyz file should be stored
    :return: Boolean: Returns True, if the function was successfull, False if not
    """
    nat = mol.GetNumAtoms()
    x = []
    y = []
    z = []
    atomtypes = []
    for atom in mol.GetAtoms():
        sym = atom.GetSymbol()
        atomtypes.append(sym)
    for i in range(0, nat):
        position = mol.GetConformer().GetAtomPosition(i)
        x.append(position.x)
        y.append(position.y)
        z.append(position.z)
    xyz = np.column_stack((x, y, z))
    # write the file
    fout = open(path + "coord.xyz", "w")
    fout.write(str(nat) + "\n\n")
    for i in range(0, nat):
        fout.write(
            "{} {:06.8f} {:06.8f} {:06.8f} ".format(
                atomtypes[i], xyz[i, 0], xyz[i, 1], xyz[i, 2]
            )
            + "\n "
        )
    fout.close()
    return True


def orca_opt_geometry(
    dataBase, id_column="ID", mol_column="molecule", create_3d_mol=True
):
    """
    Function to perform orca geometry optimization

    :param dataBase: pandas data frame that includes at least one column with a molecule identifier and one column with the molecule objects
    :param id_column: string that is the key of the column that contains the molecule identifier
    :param mol_column: string that is the key of the column that contains the molecules
    :param create_3d_mol: Boolean that says weather the 3d structure should be approximated with rdkit or not
    :returns dataBase: pandas data frame that is similar to the data frame that was put into the function but that contains 3d molecules in the column mol_column and that contains one additional column 'success' which reflects weather the orca geometry calculation was success full or not
    """
    # create 3d mol (optional)
    if create_3d_mol:
        conformers = []
        for mol in dataBase[mol_column]:
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol)
            conformers.append(mol)
        dataBase[mol_column] = conformers
    # geometry optimization
    wasSuccessfull = []
    os.system("mkdir orca")
    for index, row in dataBase.iterrows():
        molpath = "orca/" + str(row[id_column]) + "/opt/"
        origin = os.getcwd()
        os.system("mkdir orca/" + str(row[id_column]))
        os.system("mkdir " + molpath)
        if _make_xyz(row[mol_column], molpath):
            print(
                "Starting geometry optimization for molecule #"
                + str(row[id_column])
                + "."
            )
            os.chdir(molpath)
            charge = Chem.rdmolops.GetFormalCharge(row[mol_column])
            inputFile = open("orca.inp", "w")
            inputFile.write("! PM3 xyzfile Opt \n\n")
            inputFile.write("*xyzfile " + str(charge) + " 1 coord.xyz\n")
            inputFile.close()
            orcaResult = os.system("$ACM_ORCA orca.inp > orca.log")
            if orcaResult == 32512:
                raise AcmEnvVarError("$ACM_ORCA")
            if os.system("grep '****ORCA TERMINATED NORMALLY****' orca.log") == "":
                wasSuccessfull.append(False)
            else:
                wasSuccessfull.append(True)
            os.chdir(origin)
        else:
            wasSuccessfull.append(False)
    dataBase["success"] = wasSuccessfull
    return dataBase


def _orca_localize_orbitals(dataBase, id_column="ID", mol_column="molecule"):
    """
    Function to perform orca orbital localization (Only works after geometry optimization.!!!!)
    The localization is only applied for molecules where 'success' is True - meaning that the geometry optimization was success full!!!

    :param dataBase: a panadas data frame that has undergone geometry optimization before
    :param id_column: string that is the key of the column that contains the molecule identifier
    :param mol_column: string that is the key of the column that contains the molecules
    :returns dataBase: pandas data frame that is similar to the data frame that was put into the function but that has an updated version of column 'success' in which a false is set on every row where either the geometry optimization or the orbital localization has failed
    """
    wasSuccessfull = []
    for index, row in dataBase.iterrows():
        if row["success"]:
            molpath = "orca/" + str(row[id_column]) + "/loc/"
            origin = os.getcwd()
            os.system("mkdir " + molpath)
            os.system("cp orca/" + str(row[id_column]) + "/opt/orca.xyz " + molpath)
            print(
                "Starting localization of orbitals for molecule #"
                + str(row[id_column])
                + "."
            )
            os.chdir(molpath)
            charge = Chem.rdmolops.GetFormalCharge(row[mol_column])
            inputFile = open("orca-loc.inp", "w")
            inputFile.write("! PM3\n\n%loc\nlocMET FB\nend\n\n")
            inputFile.write("*xyzfile " + str(charge) + " 1 orca.xyz\n")
            inputFile.close()
            orcaResult = os.system("$ACM_ORCA orca-loc.inp > orca.log")
            if orcaResult == 32512:
                raise AcmEnvVarError("$ACM_ORCA")
            if os.system("grep '****ORCA TERMINATED NORMALLY****' orca.log") == 0:
                wasSuccessfull.append(True)
            else:
                wasSuccessfull.append(False)
            os.chdir(origin)
        else:
            wasSuccessfull.append(False)
    dataBase["success"] = wasSuccessfull
    return dataBase


def opt_geometry_and_localize_orbitals(
    dataBase, id_column="ID", mol_column="molecule", create_3d_mol=True
):
    """
    Function performing orca geometry optimization followed by orbital localization

    :param dataBase: a panadas data frame that has undergone geometry optimization before
    :param id_column: string that is the key of the column that contains the molecule identifier
    :param mol_column: string that is the key of the column that contains the molecules
    :returns dataBase: pandas data frame that is similar to the data frame that was put into the function but that has an additional column 'success' in which a false is set on every row where either the geometry optimization or the orbital localization has failed and a tTrue in cases where both has been success full
    """
    dataBase = orca_opt_geometry(dataBase, id_column, mol_column, create_3d_mol)
    dataBase = _orca_localize_orbitals(dataBase, id_column, mol_column)
    return dataBase
