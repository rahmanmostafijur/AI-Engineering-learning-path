from models import Base
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")

engine = create_engine(database_url)

Base.metadata.create_all(engine)

