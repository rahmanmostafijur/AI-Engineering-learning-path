from models import Base
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

name = os.getenv()

