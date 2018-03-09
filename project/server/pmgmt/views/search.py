from flask import Blueprint, request, jsonify
from flask_marshmallow import Marshmallow
from pmgmt.models import Hotel, ma
import itertools

class HotelSchema(ma.ModelSchema):
    class Meta:
        model = Hotel

search = Blueprint('search', __name__)

locations = ['chicago il', 'san francisco ca', 'los angeles ca', 'san jose ca','washington dc', 'new york ny', 'miami fl', 'las vegas nv', 'austin tx']

searchable_locations = [place.rsplit(' ', 1) for place in locations]

merged_locations = list(itertools.chain(*searchable_locations))

states = ['illinois', 'california', 'district of columbia', 'new york', 'florida', 'texas', 'nevada', 'washington dc']

merged_locations += states

@search.route('/api/hotels/', methods=['POST'])
def hotel_search():
    """
    Search hotel database by city or state
    """
    # word = request.form['query']
    req = request.get_json()
    word = req['query']
    sort = req['sort']

    name_sort = sort['name']
    price_sort = sort['price']
    rating_sort = sort['rating']

    # figure all sort metriccs
    if price_sort:
        price_order = 'price asc' if price_sort == 1 else 'price desc'
    else:
        price_order = None

    if rating_sort:
        rating_order = 'rating asc' if rating_sort == 1 else 'rating desc'
    else:
        price_order = None

    if name_sort:
        name_order = 'name asc' if name_sort == 1 else 'name desc'
    else:
        name_order = None

    if word not in merged_locations:
        return 'Sorry, we do not currently have any hotels in that area. Check your spelling.'
    else:
    # if word:
        try:
            if price_sort and rating_sort and name_sort:
                query_result = Hotel.query.filter(Hotel.location.like("%"+word+"%"))\
                    .order_by(price_order+', '+rating_order+', '+name_order).all()

            # if price_sort and not rating_sort:
            #     query_result = Hotel.query.filter(Hotel.location.like("%"+word+"%"))\
            #         .order_by(price_sort).order_by(rating_sort).all()
            # serializes search results
            search_schema = HotelSchema(many=True)
            output = search_schema.dump(query_result)

            # return json representation of search results
            return jsonify(output.data)
        except:
            return 'failed query'

@search.route('/api/search_index/', methods=['GET'])
def search_index():

    objects = Hotel.query.with_entities(
            Hotel.name, Hotel.city, Hotel.state).all()

    names, cities, states = set(), set(), set()

    for o in objects:
        names.add(o[0])
        cities.add(o[1])
        states.add(o[2])

    data = {
            'names': list(names),
            'cities': list(cities),
            'states': list(states)
            }

    return jsonify(data)
