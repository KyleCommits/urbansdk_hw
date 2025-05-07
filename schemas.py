from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# class SpeedRecordBase(BaseModel):
#     link_id: int
#     date_time: datetime
#     freeflow: Optional[float]
#     count: Optional[int]
#     std_dev: Optional[float]
#     min: Optional[float]
#     max: Optional[float]
#     confidence: Optional[int]
#     average_speed: Optional[float]
#     average_pct_85: Optional[float]
#     average_pct_95: Optional[float]
#     day_of_week: Optional[int]
#     period: Optional[int]

#     class Config:
#         from_attributes = True


# class LinkBase(BaseModel):
#     link_id: int
#     _length: Optional[float]
#     road_name: Optional[str]
#     usdk_speed_category: Optional[int]
#     funclass_id: Optional[int]
#     speedcat: Optional[int]
#     volume_value: int
#     volume_bin_id: int
#     volume_year: int
#     volumes_bin_description: Optional[str]
#     geo_json: Optional[dict]
#     speed_records: Optional[List[SpeedRecordBase]] = []
#     geometry_wkt: Optional[str] = None

#     class Config:
#         from_attributes = True


class SpatialFilter(BaseModel):
    day: str
    period: str
    bbox: List[float] = Field(..., min_items=4, max_items=4)
