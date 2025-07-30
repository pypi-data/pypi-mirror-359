import os
import sys
import uuid
import time
import xmlrpc.client
from multiprocessing import Pool
from cheminformatics.utils.multicore import chunk_list_into_n_lists
from cheminformatics.AcmErrors import MoeLicenceNotFoundError
from cheminformatics.AcmErrors import AcmEnvVarError


def calculateMOE2Descriptors(ListOfSmiles, writeHeader=False, descriptorSet="all"):
    """
    Calculates off moe2d Descriptors for the given SMILES

    :param ListOfSmiles: List of SMILES
    :param writeHeader: Switch which allows to return a header (default False)
    :param descriptorSet: a set (string for special selections) of desriptors e.g. set(a_acc,a_acid)/'pca' (default 'all')
    :return: List of 206 moe2d descriptors
    :return: Header for the 206 moe2d descriptors
    """
    descriptors = _whichDs(descriptorSet)
    descr = []
    header = []
    tmppath = sys.path[0]
    tmpFileName = str(uuid.uuid4())
    for p in sys.path:
        if "cheminformatics" in p:
            splitted = p.split("/")
            reppath = ""
            for pp in splitted[:-1]:
                reppath += pp + "/"
    asc = open(tmppath + "/" + tmpFileName + ".txt", "w")
    for smi in ListOfSmiles:
        asc.write(str(smi) + "\n")
    asc.close()
    osReturn = None
    while not osReturn == 0:
        try:
            osReturn = os.system(
                "$ACM_MOE -exec \"run ['"
                + reppath
                + "externals/calc_2Dmoe_descriptors.svl',['"
                + tmpFileName
                + "','"
                + tmppath
                + "',["
                + descriptors
                + ']]]" -exit'
            )
            if osReturn == 256:
                raise MoeLicenceNotFoundError()
            elif osReturn == 32512:
                raise AcmEnvVarError("$ACM_MOE")
            else:
                print("Error Code:", osReturn)
        except MoeLicenceNotFoundError:
            print(
                "To less MOE licences programm will continue when enough licences are there, next try in 1 minute"
            )
            time.sleep(60)
    try:
        outFile = open(tmppath + "/" + tmpFileName + "_out.txt", "r")
    except FileNotFoundError:
        print("Error in MOE")
        return None
    skipFirstLine = True
    for line in outFile:
        if skipFirstLine:
            skipFirstLine = False
            line = line.strip("\n")
            header = line.split(",")
            header[0] = "smiles"
            continue
        d = []
        splitted = line.split(",")
        d.append(splitted[0])
        for s in splitted[1:]:
            try:
                d.append(float(s))
                warning = None
            except ValueError:
                warning = "WARNING: For a compound no descriptors were calculated. None was added instead!"
                d.append(None)
        if warning:
            print(warning)
        descr.append(d)
    outFile.close()
    os.remove(tmppath + "/" + tmpFileName + "_out.txt")
    if writeHeader == False:
        return descr
    elif writeHeader == True:
        return (descr, header)


def _whichDs(dSet):
    """
    Helper method to build a string of decriptors as input for MOE calculation

    :param dSet: Set of descriptors or string for standard descriptor description ('pca','all')
    :return: Stirng of descriptors for MOE calculation
    """
    allList = [
        "apol",
        "ast_fraglike",
        "ast_fraglike_ext",
        "ast_violation",
        "ast_violation_ext",
        "a_acc",
        "a_acid",
        "a_aro",
        "a_base",
        "a_count",
        "a_don",
        "a_donacc",
        "a_heavy",
        "a_hyd",
        "a_IC",
        "a_ICM",
        "a_nB",
        "a_nBr",
        "a_nC",
        "a_nCl",
        "a_nF",
        "a_nH",
        "a_nI",
        "a_nN",
        "a_nO",
        "a_nP",
        "a_nS",
        "balabanJ",
        "BCUT_PEOE_0",
        "BCUT_PEOE_1",
        "BCUT_PEOE_2",
        "BCUT_PEOE_3",
        "BCUT_SLOGP_0",
        "BCUT_SLOGP_1",
        "BCUT_SLOGP_2",
        "BCUT_SLOGP_3",
        "BCUT_SMR_0",
        "BCUT_SMR_1",
        "BCUT_SMR_2",
        "BCUT_SMR_3",
        "bpol",
        "b_1rotN",
        "b_1rotR",
        "b_ar",
        "b_count",
        "b_double",
        "b_heavy",
        "b_max1len",
        "b_rotN",
        "b_rotR",
        "b_single",
        "b_triple",
        "chi0",
        "chi0v",
        "chi0v_C",
        "chi0_C",
        "chi1",
        "chi1v",
        "chi1v_C",
        "chi1_C",
        "chiral",
        "chiral_u",
        "density",
        "diameter",
        "FCharge",
        "GCUT_PEOE_0",
        "GCUT_PEOE_1",
        "GCUT_PEOE_2",
        "GCUT_PEOE_3",
        "GCUT_SLOGP_0",
        "GCUT_SLOGP_1",
        "GCUT_SLOGP_2",
        "GCUT_SLOGP_3",
        "GCUT_SMR_0",
        "GCUT_SMR_1",
        "GCUT_SMR_2",
        "GCUT_SMR_3",
        "h_ema",
        "h_emd",
        "h_emd_C",
        "h_logD",
        "h_logP",
        "h_logS",
        "h_log_dbo",
        "h_log_pbo",
        "h_mr",
        "h_pavgQ",
        "h_pKa",
        "h_pKb",
        "h_pstates",
        "h_pstrain",
        "Kier1",
        "Kier2",
        "Kier3",
        "KierA1",
        "KierA2",
        "KierA3",
        "KierFlex",
        "lip_acc",
        "lip_don",
        "lip_druglike",
        "lip_violation",
        "logP(o/w)",
        "logS",
        "mr",
        "mutagenic",
        "nmol",
        "opr_brigid",
        "opr_leadlike",
        "opr_nring",
        "opr_nrot",
        "opr_violation",
        "PC+",
        "PC-",
        "PEOE_PC+",
        "PEOE_PC-",
        "PEOE_RPC+",
        "PEOE_RPC-",
        "PEOE_VSA-6",
        "PEOE_VSA-5",
        "PEOE_VSA-4",
        "PEOE_VSA-3",
        "PEOE_VSA-2",
        "PEOE_VSA-1",
        "PEOE_VSA-0",
        "PEOE_VSA+0",
        "PEOE_VSA+1",
        "PEOE_VSA+2",
        "PEOE_VSA+3",
        "PEOE_VSA+4",
        "PEOE_VSA+5",
        "PEOE_VSA+6",
        "PEOE_VSA_FHYD",
        "PEOE_VSA_FNEG",
        "PEOE_VSA_FPNEG",
        "PEOE_VSA_FPOL",
        "PEOE_VSA_FPOS",
        "PEOE_VSA_FPPOS",
        "PEOE_VSA_HYD",
        "PEOE_VSA_NEG",
        "PEOE_VSA_PNEG",
        "PEOE_VSA_POL",
        "PEOE_VSA_POS",
        "PEOE_VSA_PPOS",
        "petitjean",
        "petitjeanSC",
        "Q_PC+",
        "Q_PC-",
        "Q_RPC+",
        "Q_RPC-",
        "Q_VSA_FHYD",
        "Q_VSA_FNEG",
        "Q_VSA_FPNEG",
        "Q_VSA_FPOL",
        "Q_VSA_FPOS",
        "Q_VSA_FPPOS",
        "Q_VSA_HYD",
        "Q_VSA_NEG",
        "Q_VSA_PNEG",
        "Q_VSA_POL",
        "Q_VSA_POS",
        "Q_VSA_PPOS",
        "radius",
        "reactive",
        "rings",
        "RPC+",
        "RPC-",
        "rsynth",
        "SlogP",
        "SlogP_VSA0",
        "SlogP_VSA1",
        "SlogP_VSA2",
        "SlogP_VSA3",
        "SlogP_VSA4",
        "SlogP_VSA5",
        "SlogP_VSA6",
        "SlogP_VSA7",
        "SlogP_VSA8",
        "SlogP_VSA9",
        "SMR",
        "SMR_VSA0",
        "SMR_VSA1",
        "SMR_VSA2",
        "SMR_VSA3",
        "SMR_VSA4",
        "SMR_VSA5",
        "SMR_VSA6",
        "SMR_VSA7",
        "TPSA",
        "VAdjEq",
        "VAdjMa",
        "VDistEq",
        "VDistMa",
        "vdw_area",
        "vdw_vol",
        "vsa_acc",
        "vsa_acid",
        "vsa_base",
        "vsa_don",
        "vsa_hyd",
        "vsa_other",
        "vsa_pol",
        "Weight",
        "weinerPath",
        "weinerPol",
        "zagreb",
    ]
    allSet = set(allList)
    if dSet == "all":
        dList = ""
        for d in allList:
            dList += "'" + d + "',"
        dList = dList[:-1]
    elif dSet == "pca":
        dList = "'a_acc','a_acid','a_aro','a_base','a_don','a_heavy','a_hyd','a_nB','a_nBr','a_nC','a_nCl','a_nF','a_nH','a_nI','a_nN','a_nO','a_nP','a_nS','b_ar','b_count','b_double','b_rotN','b_rotR','b_single','b_triple','chiral','FCharge','logP(o/w)','logS','mr','PC+','PC-','rings','TPSA','vdw_area','vdw_vol','vsa_acc','vsa_acid','vsa_base','vsa_don','vsa_hyd','vsa_other','vsa_pol','Weight'"
    else:
        if not dSet.issubset(allSet):
            print("Error: given undefined descriptors\nterminating...")
            sys.exit()
        else:
            dList = ""
            for d in allList:
                if d in dSet:
                    dList += "'" + d + "',"
            dList = dList[:-1]
    return dList


def get_similarity_of_nearest_aggregator(smilesList, cores=1):
    """
    Method that returns the similarity (based on the similarity used in Aggregator Advisor; ChemAxonPath) to the nearest aggregator found by Aggregator Advisor for a given SMILES

    :param smiles: list of valid smiles for query
    :param cores: cores to use
    :return: float (2 digits) similarity
    """
    p = Pool(cores)
    chunks = chunk_list_into_n_lists(smilesList, cores)
    mapped = p.map(_get_aggregator_advisor_result_for_smiles, chunks)
    returner = []
    for result in mapped:
        for r in result:
            if "aggregators" in r.keys():
                returner.append(round(r["aggregators"][0]["similarity"], 2))
            else:
                returner.append(0)
    return returner


def _get_aggregator_advisor_result_for_smiles(smiles):
    """
    Method to calculate a result of Aggregator Advisor. For further details see: http://advisor.bkslab.org

    :param smiles: a valid list of SMILES string
    :return: dict as the result of Aggregator Advisor result['aggregators'] contains the similarity, smiles, reference and formular of the aggregators that were found, orderd by decreseing similarity
    """
    server_url = "http://advisor.bkslab.org:8080/aggregate_lookup/xml-rpc/"
    server = xmlrpc.client.ServerProxy(server_url)
    result = []
    for smi in smiles:
        try:
            result.append(server.similarity.getSimilars(smi))
        except:
            result.append({"aggregators": [{"similarity": -1}]})
    return result
