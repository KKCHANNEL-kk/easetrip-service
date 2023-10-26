from fastapi import APIRouter, Query
from db import Mongo, AMZRDS
import model

router = APIRouter(
    prefix="/test",
)

@router.get("/db/{db_type}")
# 测试数据库读
def get_db(db_type: str, id=Query(1)):
    if db_type == 'mongo':
        client = Mongo()
        print(client)
        conn = client.get_connection()
        # 读取 test 集合的指定 id 数据
        data = conn.test.find_one({"_id": id})
    elif db_type == 'mysql':
        client = AMZRDS()
        print(client)
        conn = next(client.get_connection())
        # 读取 test 表的指定 id 数据
        data = conn.query(model.Test).filter(model.Test.id == id).first()

    return {
        "data": data
    }


@router.post("/db/{db_type}")
# 测试数据库写
def set_db(db_type: str, id=Query(1), val=Query("test")):
    if db_type == 'mongo':
        conn = Mongo().get_connection()
        # 写入 test 集合的指定 id 数据
        conn.test.update_one({"_id": id}, {"$set": {"val": val}}, upsert=True)
    elif db_type == 'mysql':
        conn = next(AMZRDS().get_connection())
        # 写入 test 表的指定 id 数据
        obj = conn.query(model.Test).filter(model.Test.id == id).first()
        if obj is not None:
            conn.query(model.Test).filter(
                model.Test.id == id).update({"val": val})
        else:
            obj = model.Test(val)
            conn.add(obj)
        conn.commit()

    return {
        "state": "success"
    }