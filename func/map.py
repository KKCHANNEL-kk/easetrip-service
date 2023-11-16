from dotenv import load_dotenv
load_dotenv()
import os
import googlemaps
from googlemaps.directions import directions
import requests
from datetime import datetime

from ..schema import Point
from ..db import AMZRDS
from ..model import Point as PointModel

conn = next(AMZRDS().get_connection())

GOOGLE_MAP_KEY: str = os.environ.get('GOOGLE_MAP_KEY', '')


def get_client() -> googlemaps.Client:
    if not GOOGLE_MAP_KEY:
        raise Exception("GOOGLE_MAP_KEY not found")

    return googlemaps.Client(key=GOOGLE_MAP_KEY)


def compute_route(origin: PointModel, destination: PointModel):
    gmaps = googlemaps.Client(key=GOOGLE_MAP_KEY)
    o = {
        "lat": origin.latitude,
        "lng": origin.longitude
    }
    d = {
        "lat": destination.latitude,
        "lng": destination.longitude
    }

    res = directions(client=gmaps, origin=o, destination=d,
                     mode="transit", departure_time=datetime.now())  # type: ignore
    if res == []:
        res = directions(client=gmaps, origin=o, destination=d,
                         mode="walking", departure_time=datetime.now())
    return res