from model import Point as PointModel
from db import AMZRDS
from schema import Point
from datetime import datetime
import requests
from googlemaps.directions import directions
import googlemaps
import os
from dotenv import load_dotenv
load_dotenv()


conn = next(AMZRDS().get_connection())

GOOGLE_MAP_KEY: str = os.environ.get('GOOGLE_MAP_KEY', '')


def get_client() -> googlemaps.Client:
    if not GOOGLE_MAP_KEY:
        raise Exception("GOOGLE_MAP_KEY not found")

    return googlemaps.Client(key=GOOGLE_MAP_KEY)


def compute_route(origin: Point, destination: Point):
    gmaps = googlemaps.Client(key=GOOGLE_MAP_KEY)
    # o = {
    #     "lat": origin.latitude,
    #     "lng": origin.longitude
    # }
    # d = {
    #     "lat": destination.latitude,
    #     "lng": destination.longitude
    # }
    o = origin.address
    d = destination.address
    print('o', o)
    print('d', d)

    res = directions(client=gmaps, origin=o, destination=d,
                     mode="transit", departure_time=datetime.now())  # type: ignore
    if res == []:
        res = directions(client=gmaps, origin=o, destination=d,
                         mode="walking", departure_time=datetime.now())
    return res


origin = conn.query(PointModel).filter(PointModel.id == 1).first()
destination = conn.query(PointModel).filter(PointModel.id == 2).first()
res = compute_route(origin, destination)

print(res)
