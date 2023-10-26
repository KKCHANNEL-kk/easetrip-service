from typing import Any
from fastapi import APIRouter, Query, Body
from model import Point

router = APIRouter(
    prefix="/schedules")



GLOBAL_SCHEDULE_CACHE:list[dict[int,Any]] = [
    
]

@router.post("/")
# TODO: uid放 session 里获取
def start(uid:int=1,pids:list[int]=[],options:dict[str,Any]=Body({})):
    # 根据 pid，获取 points
    points:list[Point] = Point.query.filter(Point.id.in_(pids)).all()
    
    
    return {
        "data":{
            "schedule_id":1,
            'uid':uid,
            'pids':pids,
            'options':options
        }
    }
    
    
@router.get("/refine")
def refine():
    return {}

@router.get("/creare")
def create():
    return {}

@router.get("/delete")
def delete():
    return {}

@router.get("/update")
def update():
    return {}

