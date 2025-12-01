from pydantic import BaseModel

class Bbox(BaseModel):
    """Bounding box for grounding tasks"""
    x1: int
    y1: int
    x2: int
    y2: int
    
    class Config:
        extra="forbid"