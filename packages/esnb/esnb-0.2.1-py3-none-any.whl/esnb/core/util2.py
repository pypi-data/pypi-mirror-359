import logging

from esnb.core.CaseExperiment2 import CaseExperiment2
from esnb.core.util import is_overlapping, process_time_string

logger = logging.getLogger("__name__")


def case_time_filter(case, date_range):
    """
    Filters the cases in the catalog based on overlap with a given date range.

    Parameters
    ----------
    case : object
        An object containing a catalog with a DataFrame `df` and an associated
        `esmcat` attribute. The DataFrame must have a "time_range" column.
    date_range : list or tuple of str
        A sequence of two date strings representing the start and end of the
        desired time range.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing only the rows whose "time_range" overlaps with
        the specified `date_range`.

    Raises
    ------
    AssertionError
        If `date_range` does not contain exactly two elements.

    Notes
    -----
    This function modifies `case.catalog.esmcat._df` in place to reflect the
    filtered DataFrame.
    """
    assert len(date_range) == 2
    trange = xr_date_range_to_datetime(date_range)
    df = case.catalog.df
    non_matching_times = []
    for index, row in df.iterrows():
        if not is_overlapping(trange, row["time_range"]):
            non_matching_times.append(index)
    df = df.drop(non_matching_times)
    case.catalog.esmcat._df = df
    return df


def flatten_list(nested_list):
    """
    Recursively flattens a nested list into a single list of elements.

    Parameters
    ----------
    nested_list : list
        A list which may contain other lists as elements, at any level of nesting.

    Returns
    -------
    flat_list : list
        A flat list containing all the elements from the nested list, with all
        levels of nesting removed.

    Examples
    --------
    >>> flatten_list([1, [2, [3, 4], 5], 6])
    [1, 2, 3, 4, 5, 6]
    """
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))  # Recursive call
        else:
            flat_list.append(item)
    return flat_list


def initialize_cases_from_source(source):
    """
    Initializes case or experiment groups from a nested source list.

    Parameters
    ----------
    source : list
        A list containing case/experiment definitions. Each element can be
        either a single case/experiment or a list of cases/experiments. Only
        two levels of nesting are supported.

    Returns
    -------
    groups : list
        A list of initialized `CaseExperiment2` objects or lists of
        `CaseExperiment2` objects, corresponding to the structure of the
        input `source`.

    Raises
    ------
    ValueError
        If `source` is not a list.
    NotImplementedError
        If more than two levels of case aggregation are provided.

    Notes
    -----
    Each case/experiment is wrapped in a `CaseExperiment2` instance. If a
    sublist is encountered, each of its elements is also wrapped, and the
    sublist is appended to the result.
    """
    if not isinstance(source, list):
        err = "Sources provided to `initialize_cases_from_source` must be a list"
        logger.error(err)
        raise ValueError(err)

    groups = []
    for x in source:
        if not isinstance(x, list):
            logging.debug(f"Setting up individual case/experiment: {x}")
            groups.append(CaseExperiment2(x))
        else:
            subgroup = []
            for i in x:
                if isinstance(i, list):
                    err = "Only two levels of case aggregation are supported."
                    logging.error(err)
                    raise NotImplementedError(err)
                else:
                    logging.debug(f"Setting up individual case/experiment: {i}")
                    subgroup.append(CaseExperiment2(i))
            groups.append(subgroup)

    return groups


def xr_date_range_to_datetime(date_range):
    """
    Converts a list of date strings into a processed datetime string.

    Each date in the input list is expected to be in the format 'YYYY-MM-DD'.
    The function zero-pads the year, month, and day components, concatenates
    them, joins the resulting strings with a hyphen, and then processes the
    final string using the `process_time_string` function.

    Parameters
    ----------
    date_range : list of str
        List of date strings, each in the format 'YYYY-MM-DD'.

    Returns
    -------
    str
        A processed datetime string obtained after formatting and joining the
        input dates, and applying `process_time_string`.

    Notes
    -----
    The function assumes that `process_time_string` is defined elsewhere in
    the codebase.
    """
    _date_range = []
    for x in date_range:
        x = x.split("-")
        x = str(x[0]).zfill(4) + str(x[1]).zfill(2) + str(x[2].zfill(2))
        _date_range.append(x)
    _date_range = str("-").join(_date_range)
    _date_range = process_time_string(_date_range)
    return _date_range
