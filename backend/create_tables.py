
from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine
from app.models.user import User

Base.metadata.create_all(bind=engine)

# with engine.begin() as connection:
#     connection.execute(
#         text(
#             "DROP TABLE IF EXISTS users"
#         )
#     )

print("Database tables and schema updated successfully")