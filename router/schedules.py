from fastapi import APIRouter, HTTPException, Query, Body

from typing import Any
from schema import Schedule, ScheduleOutput
from model import Point as PointModel
from func.ai import prompts

from db import AMZRDS, Mongo
from pymongo.database import Database as MongoDatabase

from datetime import date, datetime
import os
import json

import openai
from openai.types.chat.completion_create_params import ResponseFormat
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat import ChatCompletion
openai.api_type = "azure"
openai.azure_endpoint = "https://hkust.azure-api.net"
openai.api_version = "2023-07-01-preview"
openai.api_key = os.environ.get("AZURE_API_KEY")

router = APIRouter(
    prefix="/schedules")

GLOBAL_SCHEDULE_CACHE: list[dict[int, Any]] = [

]


def write_schedule_to_nosql(schedule: dict, uid: int = 1):
    mongo_conn: MongoDatabase = Mongo().get_connection()
    s_id = schedule['id']
    schedule['uid'] = uid
    try:
        mongo_conn['schedules'].update_one(
            {'id': s_id}, {"$set": schedule}, upsert=True)
    except Exception as e:
        print(
            'Unable to update schedule {schedule["id"]}: {e}')


@router.post("/start")
# TODO: uid放 session 里获取
def start_new_schedule_draft(
    uid: int = Body(1),
    pids: list[int] = Body(...),
    options: dict[str, Any] = Body({}),
    start: date = Body(...),
    end: date = Body(...),
    city: str = Body(default="Beijing"),
) -> Schedule:
    mysql_conn = next(AMZRDS().get_connection())

    # 根据 pid，获取 points
    points: list[PointModel] = mysql_conn.query(
        PointModel).filter(PointModel.id.in_(pids)).all()
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
                'content': prompts['start_new_schedule_draft']['system'],
            },
            *prompts['start_new_schedule_draft']['examples'],
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
    res = json.loads(content)
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    res['id'] = f"{uid}-{current_time}"
    res['name'] = f"{city}-{start}-{end}"

    w = write_schedule_to_nosql(res)

    return res


@router.post("/refine")
def refine_schedule(
    uid: int = Body(1),
    refine_chat: str = Body(...),
    draft: dict = Body(...),
):
    s_id = draft['id']
    del draft['id']
    resp: ChatCompletion = openai.chat.completions.create(
        model='gpt-35-turbo',
        messages=[
            {
                'role': 'system',
                'content': prompts['start_new_schedule_draft']['system'],
            },
            *prompts['start_new_schedule_draft']['examples'],
            *prompts['refine_schedule']['examples'],
            {
                'role': 'user',
                'content': refine_chat + "(reply with only json')\n'+'draft:\n" + json.dumps(draft)
            }
        ],  # type: ignore
        n=1,
        temperature=0,
        top_p=1,
        response_format={'type': 'text'}
    )
    choice = resp.choices[0]
    content: str = choice.message.content or '{}'

    def convert_json_in_text_to_dict(text):
        # 去除{之前的多余内容，这条语句同时适用于{之前没有多余内容的情况
        t = text[len(text.split('{')[0]):]
        suffix_length = len(text.split('}')[-1])
        # 去除}之后的多余内容, }之后没有多余内容时，则不用处理
        if suffix_length:
            t = t[:-suffix_length]
        # 转换成字典返回
        return json.loads(t)

    try:
        res = convert_json_in_text_to_dict(content)
        res['id'] = s_id
        write_schedule_to_nosql(res)
        return res
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="OpenAI Result Error")


@router.post("/")
def create_schedule(uid: int = 1, schedule: Schedule = Body(...)):

    return {}


@router.delete("/{id}")
def delete_schedule_by_id(id: str):
    mongo_conn = Mongo().get_connection()
    try:
        mongo_conn['schedules'].delete_one({'id': id})
    except Exception as e:
        print(
            'Unable to delete schedule {id}: {e}')


@router.get("/{id}", response_model=ScheduleOutput,)
def get_schedule_by_id(id: str) -> ScheduleOutput:
    mongo_conn = Mongo().get_connection()
    schedule = mongo_conn['schedules'].find_one({'id': id})
    if schedule is None:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.get('/history/{uid}')
def get_user_schedule_history(uid: int) -> list[ScheduleOutput]:
    mongo_conn = Mongo().get_connection()
    schedules = mongo_conn['schedules'].find({'uid': uid})

    def clean(schedule: dict) -> ScheduleOutput:
        del schedule['_id']
        return ScheduleOutput(**schedule)

    res: list[ScheduleOutput] = [clean(x) for x in schedules]
    return res

# @router.put("/update")
# def update_schedule_by_id(id: str):
#     return {}
