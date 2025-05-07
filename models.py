
from sqlalchemy import Column, Integer, Float, String, JSON, DateTime, func, ForeignKey
from database import Base
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship

class Link(Base):
    __tablename__ = "Link"

    link_id = Column(Integer, primary_key=True)
    _length = Column(Float)
    road_name = Column(String, nullable=True)
    usdk_speed_category = Column(Integer, nullable=True)
    funclass_id = Column(Integer, nullable=True)
    speedcat = Column(Integer, nullable=True)
    volume_value = Column(Integer)
    volume_bin_id = Column(Integer)
    volume_year = Column(Integer)
    volumes_bin_description = Column(String, nullable=True)
    geo_json = Column(JSON)
    geometry = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=True)
    speed_records = relationship("SpeedRecord", back_populates="link")



class SpeedRecord(Base):
    __tablename__ = "SpeedRecord"
    
    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("Link.link_id"), nullable=False)
    date_time = Column(DateTime, nullable=False)
    freeflow = Column(Float)
    count = Column(Integer)
    std_dev = Column(Float)
    min = Column(Float)
    max = Column(Float)
    confidence = Column(Integer)
    average_speed = Column(Float)
    average_pct_85 = Column(Float)
    average_pct_95 = Column(Float)
    day_of_week = Column(Integer)
    period = Column(Integer)
    link = relationship("Link", back_populates="speed_records")
  
