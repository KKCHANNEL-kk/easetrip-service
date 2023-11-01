from datetime import datetime, date
from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Any, List, Dict, Set, Optional
from model import Point as PointModel

class Test(BaseModel):
    id: int
    val: str


class LatLng(BaseModel):
    latitude: float
    longitude: float

# TODO: HttpUrl转换为 str 入库的问题
class Point(BaseModel):
    id: int
    name: str
    latLng: LatLng
    address: str
    mapid: Optional[str]
    pic: Optional[List[str]] = []
    # TODO: List 转 Set 的问题
    tag: List[str] = []
    city: str
    introduction: str
    options: Dict[Any, Any] = {}


class PointInput(Point):
    id: Optional[int] = None


# TODO: fix 经纬度的类型转换问题，目前暂时忽略报错
class PointOutput(Point):
    @classmethod
    def from_orm(cls, point: PointModel):
        latLng = LatLng(latitude=point.latitude, longitude=point.longitude) # type: ignore
        data = point.__dict__
        data['latLng'] = latLng
        del data['latitude']
        del data['longitude']
        return cls(**data)

    class Config:
        from_attributes = True


class RouteStep(BaseModel):
    start: str
    end: str
    step: str  # 具体路线，如地铁 11 号线乘坐2 站/巴士91M乘坐 3 站/步行500 米
    duration: int  # 单位秒
    distance: int  # 单位米


class Route(BaseModel):
    origin: Point
    destination: Point
    steps: List[RouteStep]
    duration: int  # 单位秒
    distance: int  # 单位米


ScheduleBlockType = ("point", "route")


class ScheduleBlock(BaseModel):
    type: str = Field(..., description="point or route")
    point: Optional[Point]
    route: Optional[Route]
    start_time: datetime
    end_time: datetime
    activity: Optional[str]

    @validator("type")
    def type_validate(cls, v: str) -> str:
        if v not in ScheduleBlockType:
            raise ValueError(
                f"ScheduleBlock type must be in {ScheduleBlockType}")
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
    days: List[ScheduleDay]
    options: Optional[Dict[Any, Any]]
