from multiprocessing import Pool
from rdkit import DataStructs
from cheminformatics.utils.multicore import chunk_list_into_n_lists


def __helper_get_highest_tanimoto_similarity_of_neighbors(args):
    """
    Helper funktion to parallel call get_highest_tanimoto_similarity_of_neighbors

    :param args: first 3 arguments of get_highest_tanimoto_similarity_of_neighbors
    """
    X, Y, nn = args
    return get_highest_tanimoto_similarity_of_neighbors(X, Y, nn)


def _get_sorted_list_of_tanimoto_similarity_for_one_fp(fp, fpList):
    """
    Method for the calculation of tanimoto similarities for fingerprint against a list of fingerprints

    :param fp: a fingerprint
    :param fpList: a list of fingerprints
    :return: sorted list of similarities
    """
    return sorted([DataStructs.FingerprintSimilarity(fp, y) for y in fpList])


def get_highest_tanimoto_similarity_of_neighbors(
    dataSet, dataSetToFindNearestNeighbor, NumberNearestNeighbor=1, cores=1
):
    """
    Method to get the Tanimoto similarity of two datasets. For each vaule in 'dataSet' the nearest Neighbor in 'dataSetToFindNearestNeighbor' is searched. The order of the two datasets play an important role.

    :param dataSet: List containing values that are compareable via TanimotoSimilarity
    :param dataSetToFindNearestNeighbor: List containing values that are compareable via TanimotoSimilarity
    :param NumberNearestNeighbor: Number (int) of nearest neighbors to return, must be smaller than length of dataSetToFindNearestNeighbor. Default = 1
    :param cores=1: Number (int) of cores to use.
    :return: List (same lenght and order as dataSet) with the highest Tanimoto similarity score in dataSetToFindNearestNeighbor in case NumberNearestNeighbor=1. Otherwise, len(list) = len(dataSet)*NumberNearestNeighbor
    """
    X, Y, nn = dataSet, dataSetToFindNearestNeighbor, NumberNearestNeighbor
    if nn > len(dataSetToFindNearestNeighbor):
        nn = 1
    if cores <= 1:
        return [
            _get_sorted_list_of_tanimoto_similarity_for_one_fp(x, Y)[-nn] for x in X
        ]
    else:
        chunked = chunk_list_into_n_lists(X, cores)
        gen = ((chunk, Y, nn) for chunk in chunked)
        p = Pool(cores)
        re = p.map(__helper_get_highest_tanimoto_similarity_of_neighbors, gen)
        result = []
        for r in re:
            result += r
        return result


def __helper_get_highest_tanimoto_similarity_of_neighbors_plus_ids(args):
    """
    Helper funktion to parallel call get_highest_tanimoto_similarity_of_neighbors_plus_ids
    :param args: first 3 arguments of get_highest_tanimoto_similarity_of_neighbors_plus_ids
    """
    X, Y, nn = args
    return get_highest_tanimoto_similarity_of_neighbors_plus_ids(X, Y, nn)


def _get_highest_tanimoto_similarity_for_one_fp_plus_id(fpId, fpIdList):
    """
    Method for the calculation of tanimoto similarities for fingerprint against a list of fingerprints
    :param fpId: a list of fingerprint + id ([fp,id])
    :param fpIdList: a list of lists containing fingerprints their ids [[fp0,id0],[fp1,id1],[fp2,id2],...]
    :return: List (same lenght and order as dataSetToFindNearestNeighbor) containing (Id_origin, tanimoto similarity index, Id of neighbor) sorted by Highest Tanimoto index
    """
    return sorted(
        [[fp[1], DataStructs.FingerprintSimilarity(fp[0], y[0]), y[1]] for y in fpList]
    )


def get_highest_tanimoto_similarity_of_neighbors_plus_ids(
    dataSet, dataSetToFindNearestNeighbor, NumberNearestNeighbor=1, cores=1
):
    """
    Method to get the Tanimoto similarity of two datasets. For each vaule in 'dataSet', the nearest Neighbor in 'dataSetToFindNearestNeighbor' is searched and returned with the Ids from both datasets. The order of the two datasets play an important role.
    :param dataSet: List of lists containing values that are compareable via TanimotoSimilarity and their ids. Example: [['GRML1234',[0,1,1,1,1]],['GRML2345',[1,1,0,0,1]],['GRML3456',[0,0,1,0,1]]]
    :param dataSetToFindNearestNeighbor: List of lists containing values that are compareable via TanimotoSimilarity and their ids. Example: [['ZINC123423534',[0,1,1,0,0]],['ZINC2346565',[1,0,1,1,1]],['ZINC2563456',[0,0,0,1,1]],['ZINC443567',[0,1,0,1,1]]]
    :param NumberNearestNeighbor: Number (int) of nearest neighbors to return, must be smaller than length of dataSetToFindNearestNeighbor. Default = 1
    :param cores=1: Number (int) of cores to use.
    :return: List (same lenght and order as dataSet) of lists with the highest Tanimoto similarity score in dataSetToFindNearestNeighbor and the ids from both datasets. Example: (('GRML1234',0.8,'ZINC123423534'),('GRML2345',0.5,'ZINC2346565'),('GRML3456',0.6,('ZINC123423534')) in case NumberNearestNeighbor=1, otherwise: len(list) = len(dataSet) * NumberNearestNeighbor.
    """
    X, Y, nn = dataSet, dataSetToFindNearestNeighbor, NumberNearestNeighbor
    if nn > len(dataSetToFindNearestNeighbor):
        nn = 1
    if cores <= 1:
        return [
            _get_highest_tanimoto_similarity_for_one_fp_plus_id(x, Y)[-nn] for x in X
        ]
    else:
        chunked = chunk_list_into_n_lists(X, cores)
        gen = ((chunk, Y, nn) for chunk in chunked)
        p = Pool(cores)
        re = p.map(__helper_get_highest_tanimoto_similarity_of_neighbors_plus_ids, gen)
        result = []
        for r in re:
            result += r
        return result
