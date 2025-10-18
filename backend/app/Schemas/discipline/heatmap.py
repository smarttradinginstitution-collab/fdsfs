from pydantic import BaseModel
import datetime

class HeatmapData(BaseModel):
    date: datetime.date
    score: float # A value between 0.0 and 1.0

    class Config:
        orm_mode = True