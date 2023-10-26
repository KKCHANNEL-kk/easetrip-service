from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn
from db import Mongo, AMZRDS
import model
from router import schedules, test,points
load_dotenv()
app = FastAPI()
app.include_router(test.router)
app.include_router(schedules.router)
app.include_router(points.router)

@app.get("/")
def index():
    return {
        "message": "Hello, world!"
    }


def test_script():
    # test = schema.Test(2, 222)

    # test_model = model.Test(test)

    # test_model.create()
    
    pass


if __name__ == "__main__":
    amzrds = AMZRDS()
    model.ModelBase.metadata.create_all(bind=amzrds.engine)
    # test_script()
    uvicorn.run(app="main:app", host='0.0.0.0',
                port=8000, log_level="info", reload=True)
