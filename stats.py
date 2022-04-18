#!/usr/bin/python3
'''
extract statistics from csv file provided by stats canada

'''
import sys, csv, logging  # pylint: disable=multiple-imports
from datetime import datetime
from matplotlib import pyplot
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

BOM = '\ufeff'
SOURCE_URL = '//jessicar.substack.com/p/what-is-going-on-in-new-brunswick'
DATA_SOURCE = (
    'https://www150.statcan.gc.ca/t1/tbl1/en/tv.action'
    '?pid=1310076801'
    '&pickMembers%5B0%5D=3.1'
    '&cubeTimeFrame.startDaily=2020-01-04'
    '&cubeTimeFrame.endDaily=2022-02-05'
    '&referencePeriods=20200104%2C20220205'
)

def stats(filename='13100768.csv', location='all',
          age='all ages', sex='Both sexes', save_subset=False):
    '''
    plot charts for provinces
    '''
    # pylint: disable=too-many-locals
    logging.debug('processing data for %s', location)
    dateformat = lambda d: datetime.strptime(d, '%Y-%m-%d')
    pathname = '_'.join([
        '-'.join(location.lower().split()),
        '-'.join(age.lower().split()),
        '-'.join(sex.lower().split())
        ])
    with open(filename) as infile:
        marker = infile.read(1)  # check for Byte-Order Marker (BOM)
        logging.debug('marker: %r', marker)
        if marker != BOM:
            infile.seek(0)  # "un-read" it
        else:
            logging.info('skipping byte-order marker (BOM)')
        csvdata = [row for row in csv.reader(infile)]
    headers = csvdata.pop(0)
    logging.debug('headers: %s', headers)
    logging.debug('sample row: %s', csvdata[0])
    filtered = []
    plotted = [[], []]
    if location == 'all':
        done = []
        for row in csvdata:
            rowdict = dict(zip(headers, row))
            area = rowdict['GEO'][:rowdict['GEO'].index(',')]
            if area not in done:
                stats(filename, area, age, sex, save_subset)
                logging.debug('done %s', area)
                done.append(area)
        sys.exit(0)
    for row in csvdata:
        rowdict = dict(zip(headers, row))
        if rowdict['GEO'].startswith(location) and \
                rowdict['Age at time of death'].endswith(age) and \
                rowdict['Sex'] == sex:
            filtered.append(row)
            plotted[0].append(dateformat(rowdict['REF_DATE']))
            plotted[1].append(int(rowdict['VALUE'] or '0'))
    if save_subset:
        logging.debug('storing %d rows as %s', len(filtered), pathname + '.csv')
        with open(pathname + '.csv', 'w') as outfile:
            csvout = csv.writer(outfile)
            csvout.writerow(headers)
            csvout.writerows(filtered)
    pyplot.plot(*plotted)
    pyplot.xlabel('Date')
    pyplot.ylabel('All Cause Deaths in %s' % location)
    pyplot.title(SOURCE_URL)
    logging.debug('saving graph for %s', location)
    pyplot.savefig(pathname + '.png')
    pyplot.show()

if __name__ == '__main__':
    print('If program fails, download data from %s' % DATA_SOURCE)
    stats(*sys.argv[1:])
