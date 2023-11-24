from fastapi import APIRouter, HTTPException, Query, Body

from typing import Any
from schema import ScheduleRefineAction, Schedule
from model import Point as PointModel
from func.ai import prompts

from db import AMZRDS, Mongo

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


@router.post("/start")
# TODO: uid放 session 里获取
def start_new_schedule_draft(
    uid: int = 1,
    pids: list[int] = Body(...),
    options: dict[str, Any] = Body({}),
    start: date = Body(...),
    end: date = Body(...),
    city: str = Body(default="Beijing"),
) -> Schedule:
    conn = next(AMZRDS().get_connection())

    # 根据 pid，获取 points
    points: list[PointModel] = conn.query(
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
    return res


@router.post("/refine")
def refine_schedule(
    uid: int = 1,
    refine_chat: str = Body(...),
    draft: dict = Body(...),
):
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
                'content': refine_chat + '(reply with only json)\n'+'draft:\n' + json.dumps(draft)
            }
        ],  # type: ignore
        n=1,
        temperature=0,
        top_p=1,
        response_format={'type': 'text'}
    )
    choice = resp.choices[0]
    content: str = choice.message.content or ""
    return content
    res = json.loads(content)
    return res


@router.post("/")
def create_schedule(uid: int = 1):

    return {}


@router.delete("/delete")
def delete_schedule_by_id(id: str):
    return {}


@router.put("/update")
def update_schedule_by_id(id: str):
    return {}
