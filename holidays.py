# 0ff7b634-301d-4225-b9af-b2f2d6dc8776

# Required Parameters
# keyyour API key
# countryISO 3166-2 format
# yearISO 8601 format

# {
#   "status": 200,
#   "holidays": [{
#     "name": "Independence Day",
#     "date": "2015-07-04"
#     "observed": "2015-07-03"
#     "public": true,
#   }]
# }

import holidayapi

hapi = holidayapi.v1('0ff7b634-301d-4225-b9af-b2f2d6dc8776')

parameters = {
    'country': 'US',
    'year':    2017,
    'month':    5,
    'day':      25,
}

holidays = hapi.holidays(parameters)

print holidays