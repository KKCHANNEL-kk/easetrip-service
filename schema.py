from datetime import datetime, date
from pydantic import BaseModel, Field, validator
from typing import Any, List, Dict, Optional

class Test(BaseModel):
    id: int
    val: str

class LatLng(BaseModel):
    lat: float
    lng: float

class Point(BaseModel):
    id: int
    name: str
    location: LatLng
    address: str
    mapid: Optional[str]
    iconurl: Optional[list[str]]
    tag:list[str]
    city: str
    introduction: str
    options: Optional[Dict[Any,Any]]
    
class RouteStep(BaseModel):
    start: str
    end: str
    step: str # 具体路线，如地铁 11 号线乘坐2 站/巴士91M乘坐 3 站/步行500 米
    duration: int # 单位秒
    distance: int # 单位米
    
class Route(BaseModel):
    origin: Point
    destination: Point
    steps: List[RouteStep]
    duration: int # 单位秒
    distance: int # 单位米

ScheduleBlockType = ("point", "route")
    
class ScheduleBlock(BaseModel):
    type: str = Field(..., description="point or route")
    point:Optional[Point]
    route:Optional[Route]
    start_time: datetime
    end_time: datetime
    activity: Optional[str]
    
    @validator("type")
    def type_validate(cls, v:str)->str:
        if v not in ScheduleBlockType:
            raise ValueError(f"ScheduleBlock type must be in {ScheduleBlockType}")
        return v
    
    
    __exclusive__ = ["point", "route"]
    
class ScheduleDay(BaseModel):
    day: date
    blocks: List[ScheduleBlock]
    
class Schedule(BaseModel):  
    id: str
    name: str
    start_date: date
    end_date: date
    days = List[ScheduleDay]
    options = Optional[Dict[Any,Any]]
    