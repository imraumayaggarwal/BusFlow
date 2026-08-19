from sqlalchemy.orm import session

from app.models.route import Route

def get_all_routes(
    db: session
):
    return db.query(Route).all()