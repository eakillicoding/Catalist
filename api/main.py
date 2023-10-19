from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import accounts
from routers import journals
from authenticator import authenticator
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("CORS_HOST", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# @app.get("/api/launch-details")
# def launch_details():
#     return {
#         "launch_details": {
#             "module": 3,
#             "week": 17,
#             "day": 5,
#             "hour": 19,
#             "min": "00",
#         }
#     }


app.include_router(journals.router, prefix="/api/journals")
app.include_router(accounts.router)
app.include_router(authenticator.router)
