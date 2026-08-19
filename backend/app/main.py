from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.route_response import router as route_router
from app.routers.student import router as student_router
from app.routers.manager import router as manager_router
from app.routers.bus import router as bus_router


app = FastAPI(
    title="BusFlow API",
    description="University Bus Management System",
    version="1.0.0"
)


app.include_router(auth_router)
app.include_router(route_router)
app.include_router(student_router)
app.include_router(manager_router)
app.include_router(bus_router)


@app.get("/")
def root():
    return {
        "message": "BusFlow API is running"
    }