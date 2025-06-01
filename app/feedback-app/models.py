from pydantic import BaseModel
from datetime import datetime

class FeedbackCreate(BaseModel):
    rating: str
    message: str