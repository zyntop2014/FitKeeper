# "unirest" is a code snippets use an open-source library.
import unirest

#url: https://transloc-api-1-2.p.mashape.com/agencies.{format}
url = 'https://transloc-api-1-2.p.mashape.com'

######## Get the Columbia University agency ID ########
def get_agency(name):
    agencies_url = url + '/agencies.json'
    agencies_response = unirest.get(agencies_url,headers={"X-Mashape-Key": "VtWMMb78tRmshCCC1AW2Pwe8A5Lwp1XU95bjsnuxefAgtIYh3J","Accept": "application/json"})
    for agency in agencies_response.body['data']:
        if agency['long_name']==name:
            agencyID= agency['agency_id']
    return agencyID


#get_routes(): returns a list of current route, route id

def get_routes():
    agency_id = get_agency('Columbia University')
    routes_url = url + '/routes.json?'
    routes_url += 'agencies=' + agency_id
    routes_response = unirest.get(routes_url,headers={"X-Mashape-Key": "VtWMMb78tRmshCCC1AW2Pwe8A5Lwp1XU95bjsnuxefAgtIYh3J","Accept": "application/json"})
    routes=[]
    routes_id=[]
    for i in routes_response.body['data'][agency_id]:
        routes.append(i['long_name'])
        routes_id.append(i['route_id'])
    return routes,routes_id

routes,routes_id=get_routes()

#get_stops(): Returns a list of current stop, stop id ,locations
def get_stops():
    agency_id = get_agency('Columbia University')
    stops_url = url + '/stops.json?'
    stops_url += 'agencies=' + agency_id
    stops_response = unirest.get(stops_url,headers={"X-Mashape-Key": "VtWMMb78tRmshCCC1AW2Pwe8A5Lwp1XU95bjsnuxefAgtIYh3J","Accept": "application/json"})
    stops=[]
    stops_id=[]
    locations=[]
    for i in stops_response.body['data']:
        stops.append(i['name'])
        stops_id.append(i['stop_id'])
        locations.append(i['location'])
    return stops, stops_id, locations

stops, stops_id, locations=get_stops()

"""
get_estimate(route, stop)
Parameters:
    - route: a route ID
    - stop:  a stop ID
Returns:
    - a list of arrival dictionaries
"""

def get_estimate(route_id, stop_id):
    agency_id = get_agency('Columbia University')
    estimates_url = url + '/arrival-estimates.json?'
    estimates_url += 'agencies=' + agency_id
    estimates_url += '&routes='   + route_id
    estimates_url += '&stops='    + stop_id
    estimates_response = unirest.get(estimates_url,headers={"X-Mashape-Key": "VtWMMb78tRmshCCC1AW2Pwe8A5Lwp1XU95bjsnuxefAgtIYh3J","Accept": "application/json"})
    return estimates_response.body['data'][0]['arrivals'][0]['arrival_at']
    
    
arrival_time=get_estimate(routes_id[2],stops_id[23])

#transloc.arrival_time