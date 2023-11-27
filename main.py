from fastapi.middleware.cors import CORSMiddleware
from router import schedules, test, points
import model
from db import Mongo, AMZRDS
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()
print("Service Init: Loading .env")


print(
    f'Mongo:{Mongo().uri}\nAMZRDS:{AMZRDS().uri}\n')

app = FastAPI()
app.include_router(test.router)
app.include_router(schedules.router)
app.include_router(points.router)
origins = ["*", "http://localhost:3000"]
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],)


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
