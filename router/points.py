from fastapi import HTTPException
from fastapi import APIRouter, Query, Body
from typing import Any, List
from typing_extensions import Annotated
import json

from sqlalchemy import text

from schema import PointInput, PointOutput, LatLng
from model import Point as PointModel
from db import AMZRDS, Mongo

router = APIRouter(
    prefix="/points")

conn = next(AMZRDS().get_connection())


ALLOWED_CITIES = ['Shanghai', 'Beijing', 'Guangzhou']
ALLOWED_TAGS = ['seasonal_limited',
                'delicious_food',
                'historical_sites',
                'citywalk',
                'playgrounds',
                'cultural_expriences',
                'events_shows',
                ]
GOOGLEMAPID_CITY = {
    'ChIJuSwU55ZS8DURiqkPryBWYrk': 'Beijing',
    'ChIJMzz1sUBwsjURoWTDI5QSlQI': 'Shanghai',
    'ChIJD5gyo-3iAzQRfMnq27qzivA': 'Hong Kong'
}


@router.get("/",
            summary="Search for points of interest based on city and/or tag.",
            description="Search for points of interest based on city and/or tag.",
            response_description="List of points of interest matching the search criteria.",
            response_model=List[PointOutput]
            )
def search_points(limit: Annotated[int, 'The maximum number of points to return.'] = 10,
                  offset: Annotated[int, 'The number of points to skip.'] = 0,
                  city: str = Query(None),
                  tag: str = Query(None)
                  ) -> List[PointOutput]:
    # 兼容 Google Map ID 传值场景
    if city in GOOGLEMAPID_CITY:
        city = GOOGLEMAPID_CITY[city]

    query = conn.query(PointModel)
    if city:
        query = query.filter(PointModel.city == city)
    if tag:
        # tag_json = json.dumps([tag])  # Convert the tag to a JSON array
        query = query.filter(PointModel.options['tag'].contains(tag))

    points: List[PointModel] = query.limit(limit).offset(offset).all()

    ret: list[PointOutput] = [PointOutput.from_orm(p) for p in points]

    return ret


@router.get("/cart")
def get_points_by_ids(p_ids: List[int] = Query(...)):
    """
    Retrieve a list of points by ID.

    Args:
        p_ids (List[int]): The IDs of the points to retrieve.

    Returns:
        List[PointModel]: The points with the specified IDs.
    """
    points: List[PointModel] = conn.query(PointModel).filter(
        PointModel.id.in_(p_ids)).all()

    return [PointOutput.from_orm(p) for p in points]


@router.get("/{p_id}")
def get_point_by_id(p_id: int):
    """
    Retrieve a point by ID.

    Args:
        p_id (int): The ID of the point to retrieve.

    Returns:
        PointModel: The point with the specified ID.
    """
    point: PointModel = conn.query(PointModel).filter(
        PointModel.id == p_id).first()

    return PointOutput.from_orm(point)


@router.post("/")
def save_points(points: List[PointInput] = Body({})):
    """
    Save a list of points to the database.

    Args:
        points (List[PointInput]): A list of PointInput objects containing information about each point.

    Returns:
        None
    """
    for point in points:
        point.options['pic'] = point.pic
        point.options['tag'] = point.tag

        m_p = PointModel(name=point.name, longitude=point.latLng.longitude, latitude=point.latLng.latitude, address=point.address, mapid=point.mapid,
                         city=point.city, introduction=point.introduction, options=point.options)
        m_p.create()
