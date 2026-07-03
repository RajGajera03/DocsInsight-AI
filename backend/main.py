# This file exists simply to allow the command `uvicorn main:app` to work 
# directly from the backend folder without throwing an import error.
from app.main import app
