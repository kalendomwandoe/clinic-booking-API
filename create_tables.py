from app.database import Base, engine
from app.models import Doctor  # importing registers Doctor with Base

Base.metadata.create_all(bind=engine)
print("Tables created.")