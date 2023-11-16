from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat import ChatCompletion
from typing import Any
from fastapi import APIRouter, HTTPException, Query, Body
from model import Point
from typing import Any, List
from schema import PointInput, PointOutput, LatLng
from model import Point as PointModel
from db import AMZRDS, Mongo
from datetime import date
import json

import openai
import os
openai.api_type = "azure"
openai.azure_endpoint = "https://hkust.azure-api.net"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.environ.get("AZURE_API_KEY")

router = APIRouter(
    prefix="/schedules")

GLOBAL_SCHEDULE_CACHE: list[dict[int, Any]] = [

]
sys_prompt = '''
You are a trip assistant. Here are some places I want to go, please help me generate a trip schedule in JSON file.

## Data Models

**Point** : a place I want to go

- name (str): The name of the place
- address (str): The full address of the place
- latLng (object): An object containing latitude and longitude coordinates

**RouteStep** : a single step in the route between two points

- start (str): The starting point's name of the step
- end (str): The ending point's name of the step
- step (str): The specific traffic route, e.g. 'Metro Line 11, 2 stops', 'Bus 91M, 3 stops', '500 metres on foot'
- duration (int): The time (in seconds) it takes to travel this step
- distance (int): The distance (in meters) between the start and end points

**Route** : a complete route from origin to destination

- origin (str): The starting point's name of the route
- destination (str): The ending point of the route
- steps (list[RouteStep]): An array of RouteStep objects representing each step in the route
- duration (int): The total time in seconds
- distance (int): The total distance in kilometers

**ScheduleBlock** : a block of time in the schedule for a specific activity

- type (str): The type of activity ('point' or 'route')
- point (str): The point where the activity takes place (if applicable)
- route (Route): The route taken to reach the point (if applicable)
- start (datetime): The start time of the activity in HH:mm format
- end (datetime): The end time of the activity in HH:mm format
- activity (str): A description of the activity

**ScheduleDay** : a single day in the trip schedule

- day (date): The date in the schedule (e.g. 2023/07/01)
- blocks (list[ScheduleBlock]): An array of ScheduleBlock objects representing the activities for the day

**Schedule** : the entire trip schedule

- start (date): The start date of the trip in YYYY/MM/DD format
- end (date): The end date of the trip
- days (list[ScheduleDay]): An array of ScheduleDay objects representing each day of the trip

'''
few_shots: list[ChatCompletionMessageParam] = [
    {'role': 'user',
     'content':
     '''
{
  "start": "2023/07/01",
  "end": "2023/07/02",
  "points": [
    {
      "name": "Star Ferry",
      "address": "Star Ferry Pier, Tsim Sha Tsui, Tsim Sha Tsui Promenade, Hong Kong",
      "latLng": {
        "lat": 22.293764,
        "lng": 114.168463
      }
    },
    {
      "name": "Victoria Harbour",
      "address": "Tsim Sha Tsui Promenade, Kowloon, Hong Kong",
      "latLng": {
        "lat": 22.293528,
        "lng": 114.171007
      }
    },
    {
      "name": "Lantau Island",
      "address": "Lantau Island, New Territories, Hong Kong",
      "latLng": {
        "lat": 22.266498,
        "lng": 113.941751
      }
    }
  ]
}
'''}, {
         'role': 'assistant',
         'content':
        '''
{
    "start": "2023/07/01",
    "end": "2023/07/02",
    "days": [
        {
            "day": "2023/07/01",
            "blocks": [
                {
                    "type": "point",
                    "point": "Star Ferry",
                    "start": "10:00",
                    "end": "11:00",
                    "activity": "Take a ride on the Star Ferry and enjoy the view of Victoria Harbour"
                },
                {
                    "type": "route",
                    "route": {
                        "origin": "Star Ferry",
                        "destination": "Victoria Harbour",
                        "steps": [
                            {
                                "start": "Star Ferry",
                                "end": "Victoria Harbour",
                                "step": "350 metres on foot",
                                "distance": 350,
                                "duration": 300
                            }
                        ],
                        "duration": 300,
                        "distance": 350
                    },
                    "start": "11:00",
                    "end": "11:05",
                    "activity": "Walk to Victoria Harbour"
                },
                {
                    "type": "point",
                    "point": "Victoria Harbour",
                    "start": "11:05",
                    "end": "13:00",
                    "activity": "Explore Victoria Harbour and enjoy the skyline view"
                }
            ]
        },
        {
            "day": "2023/07/02",
            "blocks": [
                {
                    "type": "point",
                    "point": "Lantau Island",
                    "start": "10:00",
                    "end": "17:00",
                    "activity": "Spend the day exploring Lantau Island, visit the Big Buddha and Po Lin Monastery"
                }
            ]
        }
    ]
}
'''
    }
]


@router.post("/start")
# TODO: uid放 session 里获取
def start_new_schedule_draft(
    uid: int = 1,
    pids: list[int] = Body(...),
    options: dict[str, Any] = Body({}),
    start: date = Body(...),
    end: date = Body(...)
):
    conn = next(AMZRDS().get_connection())

    # 根据 pid，获取 points
    points: list[Point] = conn.query(Point).filter(Point.id.in_(pids)).all()
    if not points:
        raise HTTPException(status_code=400, detail="Invalid point id")

    slim_points = []
    for point in points:
        slim_points.append({
            "id": point.id,
            "name": point.name,
            "latLng": {
                "lat": float(point.latitude),
                "lng": float(point.longitude)
            },
            "address": point.address})

    input = json.dumps({
        'start': str(start),
        'end': str(end),
        'points': slim_points,
    })

    resp: ChatCompletion = openai.chat.completions.create(
        model='gpt-35-turbo',
        messages=[
            {
                'role': 'system',
                'content': sys_prompt,
            },
            few_shots[0],
            few_shots[1],
            {
                'role': 'user',
                'content': input,
            }
        ],  # type: ignore
        n=1,
        temperature=0,
        top_p=1,
        response_format={'type': 'text'},
    )
    choice = resp.choices[0]
    content: str = choice.message.content or ""

    print(content)
    return json.loads(content)


@router.get("/refine")
def refine():
    return {}


@router.post("/")
def create_schedule(uid: int = 1):

    return {}


@router.delete("/delete")
def delete_schedule_by_id(id: str):
    return {}


@router.put("/update")
def update_schedule_by_id(id: str):
    return {}
