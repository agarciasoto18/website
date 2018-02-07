from datetime import datetime
import numpy as np
from astropy.table import Table

dates = {'': [2018, 7, 30],  # putput unassigned talks on first day to make
                             # sure they are not overlooked
         'TBA': [2018, 7, 30],
         'Sun': [2018, 7, 29],
         'Mon': [2018, 7, 30],
         'Tue': [2018, 7, 31],
         'Wed': [2018, 8, 1],
         'Thu': [2018, 8, 2],
         'Fri': [2018, 8, 3],
         'Sat': [2018, 8, 4]}
'''Mapping between 3-character day code and date'''




def parse_day_time(day, timestr, end=False):
    '''Turn day and time string into a datetime object.

    If time is empty or "TBA", the return time is late in the
    afternoon to that not yet assigned talks get printed last
    in the list of sorted talks. A default for ``day`` can be set
    by adding the appropriate values to the look-up table ``dates``.

    Parameters
    ----------
    day : string
        index for lookup in ``dates`` table
    timestr : string
        string for time in the form "14:30 - 15:15".
    end : bool
        Return end time of event (default is start time)

    Returns
    -------
    datetime : `datetime.datetime`
        Start time of event as `datetime.datetime` object.
    '''
    i = 1 if end else 0
    if timestr in ['', 'TBA']:
        time = ['19', '00']
    else:
        time = timestr.split('-')[i].split(':')
    d = dates[day]
    return datetime(d[0], d[1], d[2], int(time[0].strip()), int(time[1].strip()))

def data():
    # Fast reader does not deal well with some unicode
    abstr = Table.read('../data/abstracts.csv', fast_reader=False)
    abstr = abstr[~abstr['Timestamp'].mask]
    abstr['authorlist'] = [r.split(';') for r in abstr['Authors']]
    abstr['affillist'] = [r.split(';') for r in abstr['Affiliations']]

    ind_talk = (abstr['type'] == 'invited') | (abstr['type'] == 'contributed')
    ind_poster = abstr['type'] == 'poster'

    talks = abstr[ind_talk]
    if ('day' in talks.colnames) and ('time' in talks.colnames):
        talks['binary_time'] = [parse_day_time(r['day'][:3], r['time']) for r in talks]
        talks.sort('binary_time')
    else:
        talks.sort('type')
        talks.reverse()  # 'invited' is after 'contributed' alphabetically

    posters = abstr[ind_poster]
    if 'poster number' not in posters.colnames:
        posters['poster number'] = 'TBA'
    posters.sort(['poster number', 'Authors'])
    # check it's a number otherwise sort will fail because string sorting will
    # give different answers
    if not np.issubdtype(posters['poster number'].dtype, np.integer):
        print('Poster numbers are not integers - they might be sorted randomly.')
    # check that no two posters have the same number
    unique_numbers, unique_counts = np.unique(posters['poster number'],
                                          return_counts=True)
    if (unique_counts > 1).sum() > 0:
        print('The following poster numbers are used more than once:')
        for i in (unique_counts > 1).nonzero()[0]:
            print('{}  is assigned to {} posters'.format(unique_numbers[i],
                                                     unique_counts[1]))


    # List all entries that do not have a valid type
    notype = abstr[~ind_talk & ~ind_poster]
    if len(notype) > 0:
        print('The following entries do not have a valid "type" entry, which would classify them as talk or poster:')
        for r in notype:
            print(r['Timestamp'], r['type'], r['Title'])

    return {'talks': talks, 'posters': posters}