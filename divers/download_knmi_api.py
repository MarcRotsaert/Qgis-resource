import requests
import pandas as pd
from io import StringIO
import pprint as pp

def main():
    startdate = '20220513'
    enddate = '20220513'
    stations = [344,348]
    #variables = ['EV24', 'TG', 'TN', 'DR', 'RH']
    variables = ['DDVEC', 'FHVEC']
    variables = ['DD', 'FH']
    df = get_hourly_data_df(startdate, enddate, stations, variables)
    pp.pprint(df)


def get_hourly_data_df(startdate, enddate, stations, variables):
    """Request and parse data from knmi api.

    Parameters
    ----------
    start : str
        Startdate in string format, eg '20210101'
    end : str
        Enddate in string format, eg '20210101'
    stations : [int], optional
        List of station numbers in int format, by default None
    variables : [str], optional
        List of variables in str format, if None is given, all are returned by the api

    Returns
    -------
    DataFrame
        Containing data returned by knmi api
    """
    r = get_hourly_data_raw(startdate, enddate, stations, variables)
    df = parse_result_to_df(r)
    return df


def get_hourly_data_raw(start, end, stations=None, variables=None):
    """Get raw data from knmi api.
    
    See: https://www.knmi.nl/kennis-en-datacentrum/achtergrond/data-ophalen-vanuit-een-script
    Parameters
    ----------
    start : str
        Startdate in string format, eg '20210101'
    end : str
        Enddate in string format, eg '20210101'
    stations : [int], optional
        List of station numbers in int format, by default None
    variables : [str], optional
        List of variables in str format, if None is given, all are returned by the api

    Returns
    -------
    str
        Containing data returned by knmi api
    """
    #url = 'https://www.daggegevens.knmi.nl/klimatologie/daggegevens'
    url = 'https://www.daggegevens.knmi.nl/klimatologie/uurgegevens'
    params = 'start=' + start
    params = params + '&end=' + end
    params = add_list_items_to_params(params, 'stns', stations)
    params = add_list_items_to_params(params, 'vars', variables)
    r = requests.post(url=url, data=params)
    return r.text


def add_list_items_to_params(params, name, variables):
    """Add every variable in var_list to the parameter string.

    Parameters
    ----------
    params : str
        String containing the request parameters
    name : str
        Name of the variable, specified by knmi api
    variables : list
        Containing items to be added to params

    Returns
    -------
    str
        Appended string of request parameters
    """
    if variables is not None:
        vars_parsed = str(variables[0])
        if len(variables) != 1:
            for var in variables[1:]:
                vars_parsed = vars_parsed + ':' + str(var)
        params = params + '&' + name + '=' + vars_parsed
    return params


def parse_result_to_df(response_text):
    """Parse result of function get_hourly_data_raw

    Parameters
    ----------
    response_text : str
        Containing data returned by knmi api

    Returns
    -------
    DataFrame
        Containing data returned by knmi api
    """
    # Count and drop the # lines, except last containing column names
    count = 0
    for i in range(0, len(response_text)):
        if (response_text[i] == '#'):
            count = count + 1
    r = response_text.split("\n", count-1)[count-1]
    # drop '# '
    r = r[2:]
    df = pd.read_csv(StringIO(r))
    return df


if __name__ == '__main__':
    main()