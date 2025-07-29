"""

.. module author:: Anke Wilm <wilm@zbh.uni-hamburg.de>

"""

import xlsxwriter
import os
import sys
import numpy as np
import pandas as pd
import cairosvg
from rdkit.Chem import AllChem
from rdkit.Chem import MolFromSmiles
from rdkit.Chem import Draw
from rdkit.Chem import PandasTools
from rdkit.Chem.Draw import rdMolDraw2D


def write_to_excell_file(
    dataFrame,
    name_column="name",
    smiles_column="smiles",
    property_column="activity",
    savePath="resultSummary",
    plotPath="plots",
    red_criterium=1,
    green_criterium=0,
):
    """
    Function to write a basic excell file with one column for molecules name, one column for 2D depiction of the molecule and one column for a property of choice with optional conditional formatting of this column as either red or green.

    :param dataFrame: pandas data frame that includes all the information that should be contained in the excell sheet
    :param name_column: string that gives the name of the column in which the molecule names are stored
    :param smiles_column: string that gives the name of the column in which the molecule smiles are stored
    :param property_column: string that gives the name of the column in which the molecule properties are stored
    :param savePath: string that gives the path where the excell file will be stored
    :param plotPath: string that gives the name of the folder in which the plots will be stored
    :param red_criterium: integer that gives the value of the property for which the cell will be colored in red
    :param green_criterium: integer that gives the value of the property for which the cell will be colored in green
    """
    draw_2d_molecules(
        dataFrame[name_column].tolist(),
        dataFrame[smiles_column].tolist(),
        plotPath=plotPath,
        png=True,
    )
    # reorder DataFrame
    dataFrame["2D figure"] = np.nan
    dataFrame = dataFrame[[name_column, smiles_column, "2D figure", property_column]]
    dataFrame.to_csv(savePath + ".csv")
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(savePath + ".xlsx", engine="xlsxwriter")
    # Convert the dataframe to an XlsxWriter Excel object.
    dataFrame.to_excel(writer, sheet_name="Sheet1", startrow=1, header=False)
    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    worksheet = writer.sheets["Sheet1"]
    # Make the default hight of rows higher, so that figures fit in
    worksheet.set_default_row(51)
    # Add a header format.
    header_format = workbook.add_format(
        {
            "bold": True,
            "text_wrap": True,
            "valign": "vcenter",
            "border": 1,
            "bg_color": "gray",
        }
    )
    for col_num, value in enumerate(dataFrame.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)
    worksheet.set_row(0, 40)
    # format columns
    worksheet.set_column("A:A", None, None, {"hidden": 1})
    worksheet.set_column("B:B", 40)  # name
    worksheet.set_column("C:C", None, None, {"hidden": 1})  # smiles
    worksheet.set_column("D:D", 21)  # picture
    worksheet.set_column("E:E", 18)  # property
    # set different formats
    red_format = workbook.add_format({"bg_color": "red"})
    green_format = workbook.add_format({"bg_color": "lime"})
    # set different conditions
    worksheet.conditional_format(
        "E1:E" + str(len(dataFrame["2D figure"]) + 1),
        {
            "type": "formula",
            "criteria": "$E1=" + str(red_criterium),
            "format": red_format,
        },
    )
    worksheet.conditional_format(
        "E1:E" + str(len(dataFrame["2D figure"]) + 1),
        {
            "type": "formula",
            "criteria": "$E1=" + str(green_criterium),
            "format": green_format,
        },
    )
    # insert images
    for index in range(len(dataFrame["2D figure"])):
        print(index)
        cell = "D" + str(index + 2)
        path = plotPath + "/" + str(dataFrame[name_column].tolist()[index]) + ".png"
        worksheet.insert_image(
            cell, path, {"positioning": 1, "x_scale": 0.3, "y_scale": 0.3}
        )
    # Freeze first row (header)
    worksheet.freeze_panes(1, 0)
    workbook.close()


def draw_2d_molecules(list_of_names, list_of_smiles, plotPath="plots", png=False):
    """
    Function that draws 2d molecules.

    :param list_of_names: A list that contains the names of the files in which the pictures should be stored
    :param list_of_smiles: A list that contains the smiles of the molecules that should be drawn. Must have same length and same order as list_of_names.
    :param png: Boolean with default = False. Tells the function if files should be .png
    :param plotPath: string. Name of or path to folder in which the pictures should be stored
    """
    if len(list_of_names) != len(list_of_smiles):
        print("list_of_names and list_of_smiles must have same length!!!")
        sys.exit()
    # create 2d pictures of the molecules
    for i, smi in enumerate(list_of_smiles):
        svgImg = build_binary_image_string_of_mol(MolFromSmiles(smi))
        f = open(plotPath + "/" + str(list_of_names[i]) + ".svg", "w")
        f.write(svgImg)
        f.close()
        if png:
            cairosvg.svg2png(
                url=plotPath + "/" + str(list_of_names[i]) + ".svg",
                write_to=plotPath + "/" + str(list_of_names[i]) + ".png",
            )


def build_binary_image_string_of_mol(mol):
    """
    Builds binary string of image of molecule

    :param mol: rdkit molecule
    :return: binary string for writing into file
    """
    AllChem.Compute2DCoords(mol)
    drawer = rdMolDraw2D.MolDraw2DSVG(400, 200)
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    return drawer.GetDrawingText()
