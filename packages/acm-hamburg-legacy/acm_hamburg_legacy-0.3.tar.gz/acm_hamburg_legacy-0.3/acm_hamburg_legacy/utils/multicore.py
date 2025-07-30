from itertools import islice


def chunk_list_into_n_lists(l, n):
    """
    method to chunk a list for multiprocessing

    :param l: any kind of list
    :param n: number of chunks to chunk the list into
    :return: list (with len(n)) of equally distributed lists
    """
    c = int(len(l) / n)
    if c == 0:
        c = 1
    return [l[x : x + c] for x in range(0, len(l), c)]


def chunk_dict_into_n_dicts(d, n):
    """
    method to chunk a dict for multiprocessing

    :param d: any kind of dict
    :param n: number of chunks to chunk the dict into
    :return: list (with len(n)) of equally distributed dicts
    """
    c = int(len(d) / n)
    if c == 0:
        c = 1
    it = iter(d)
    returner = []
    for i in range(0, len(d), c):
        returner.append({k: d[k] for k in islice(it, c)})
    return returner
