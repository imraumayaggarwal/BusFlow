from pydantic import BaseModel

class RouteResponse(BaseModel):
    route_id: str
    start_location: str
    end_location: str

    class config:
        from_attributes = True