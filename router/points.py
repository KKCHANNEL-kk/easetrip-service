from fastapi import APIRouter, Query, Body

router = APIRouter(
    prefix="/points")

@router.get("/")
def search_points():
    return {}

@router.get("/{p_id}")
def get_point_by_id(p_id:int):
    return {}