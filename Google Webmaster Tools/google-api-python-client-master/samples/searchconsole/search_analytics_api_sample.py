#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Example for using the Google Search Analytics API (part of Search Console API).

A basic python command-line example that uses the searchAnalytics.query method
of the Google Search Console API. This example demonstrates how to query Google
search results data for your property. Learn more at
https://developers.google.com/webmaster-tools/

To use:
1) Install the Google Python client library, as shown at https://developers.google.com/webmaster-tools/v3/libraries.
2) Sign up for a new project in the Google APIs console at https://code.google.com/apis/console.
3) Register the project to use OAuth2.0 for installed applications.
4) Copy your client ID, client secret, and redirect URL into the client_secrets.json file included in this package.
5) Run the app in the command-line as shown below.

Sample usage:

  $ python search_analytics_api_sample.py 'https://www.example.com/' '2015-05-01' '2015-05-30'

"""

import sys
from googleapiclient import sample_tools


def get(siteUrl, body):
  return SERVICE.searchanalytics().query(siteUrl=siteUrl, body=body).execute()

def print_table(response, title):
  """Prints out a response table.

  Each row contains key(s), clicks, impressions, CTR, and average position.

  Args:
    response: The server response to be printed as a table.
    title: The title of the table.
  """
  print('\n'+title + ':' +str(response))

  if 'rows' not in response:
    print('Empty response')
    return

  rows = response['rows']
  row_format = '{:<20}' + '{:>20}' * 4
  print(row_format.format('Keys', 'Clicks', 'Impressions', 'CTR', 'Position'))
  for row in rows:
    keys = ''
    # Keys are returned only if one or more dimensions are requested.
    if 'keys' in row:
      keys = u','.join(row['keys']).encode('utf-8')
    print(row_format.format(
        keys, row['clicks'], row['impressions'], row['ctr'], row['position']))
SERVICE=None
#if __name__ == '__main__':
flags={'url':"https://www.onlineverdict.com/",'startDate':'2017-01-01', 'endDate':'2017-10-01'}
SERVICE, f = sample_tools.init(
    sys.argv, 'webmasters', 'v3', __doc__, __file__, 
    scope='https://www.googleapis.com/auth/webmasters.readonly')
# First run a query to learn which dates we have data for. You should always
# check which days in a date range have data before running your main query.
# This query shows data for the entire range, grouped and sorted by day,
# descending; any days without data will be missing from the results.
response = get(flags['url'], {
    'startDate': flags['startDate'],
    'endDate': flags['endDate'],
    'dimensions': ['date']})
print_table(response, 'Available dates')

# Get totals for the date range.
response = get(flags['url'], {
    'startDate': flags['startDate'],
    'endDate': flags['endDate'] })
print_table(response, 'Totals')

# Get top 10 queries for the date range, sorted by click count, descending.
response = get(flags['url'], {
    'startDate': flags['startDate'],
    'endDate': flags['endDate'],
    'dimensions': ['query'],
    'rowLimit': 10  })
print_table(response, 'Top Queries')

# Get top 11-20 mobile queries for the date range, sorted by click count, descending.
response = get(flags['url'], {
    'startDate': flags['startDate'],
    'endDate': flags['endDate'],
    'dimensions': ['query'],
    'dimensionFilterGroups': [{
        'filters': [{
            'dimension': 'device',
            'expression': 'mobile'
        }]
    }],
    'rowLimit': 10,
    'startRow': 10  })
print_table(response, 'Top 11-20 Mobile Queries')

# Get top 10 pages for the date range, sorted by click count, descending.
response = get(flags['url'], {
    'startDate': flags['startDate'],
    'endDate': flags['endDate'],
    'dimensions': ['page'],
    'rowLimit': 10  })
print_table(response, 'Top Pages')

# Get the top 10 queries in India, sorted by click count, descending.
response = get(flags['url'], {
    'startDate': flags['startDate'],
    'endDate': flags['endDate'],
    'dimensions': ['query'],
    'dimensionFilterGroups': [{
        'filters': [{
            'dimension': 'country',
            'expression': 'ind'
        }]
    }],
    'rowLimit': 10  })
print_table(response, 'Top queries in India')

# Group by both country and device.
response = get(flags['url'], {
    'startDate': flags['startDate'],
    'endDate': flags['endDate'],
    'dimensions': ['country', 'device'],
    'rowLimit': 10  })
print_table(response, 'Group by country and device')

