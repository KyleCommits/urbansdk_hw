from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Float
from database import SessionLocal
from models import Link, SpeedRecord
from schemas import SpatialFilter
from helper import convert_period_string_to_datetimes, day_dict, period_dict
from geoalchemy2.functions import ST_MakeEnvelope, ST_Intersects
from geoalchemy2 import Geometry
import json


app = FastAPI(
    title="UrbanSDK Homework",
    description="API for UrbanSDK Homework",
    version="1.0.0",
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/aggregates/")
def get_aggregates(day:str, period:str, db: Session = Depends(get_db)):
 
    day_id = day_dict.get(day, None)
    if day_id is None:
        raise HTTPException(status_code=400, detail="Invalid day of week")
    
    start_datetime_str, end_datetime_str = convert_period_string_to_datetimes(period)
    if start_datetime_str is None or end_datetime_str is None:
        raise HTTPException(status_code=400, detail="Invalid period")

    # results = db.query(
    #     Link.link_id,
    #     func.avg(SpeedRecord.average_speed).label("average_speed"),
    #     Link.road_name,
    #     func.ST_AsGeoJSON(Link.geometry).label("geometry"),
    #     cast(Link._length, Float).label("length")
    # ).join(
    #     SpeedRecord, SpeedRecord.link_id == Link.link_id
    # ).filter(
    #     SpeedRecord.day_of_week == day_dict.get(day,0),
    #     SpeedRecord.period == period_dict.get(period,0)
    # ).group_by(Link.link_id, Link.road_name, Link.geometry, Link._length).all()

    results = db.query(
        Link.link_id,
        func.avg(SpeedRecord.average_speed).label("average_speed"),
        Link.road_name,
        func.ST_AsGeoJSON(Link.geometry).label("geometry"),
        cast(Link._length, Float).label("length")
    ).join(
        SpeedRecord, SpeedRecord.link_id == Link.link_id
    ).filter(
        SpeedRecord.day_of_week == day_id,
        SpeedRecord.date_time >= start_datetime_str,
        SpeedRecord.date_time <= end_datetime_str
    ).group_by(Link.link_id, Link.road_name, Link.geometry, Link._length).all()


    return_list =[]
    for link_id, average_speed, road_name, geometry, length  in results:
        return_list.append({
            "link_id": link_id,
            "average_speed": average_speed,
            "road_name": road_name,
            "geometry": json.loads(geometry),
            "length": length
        })      
    
    return return_list


@app.get("/aggregates/{link_id}/")
def get_aggregates_link_id(link_id:int, day:str, period:str, db: Session = Depends(get_db)):
     
    # results = db.query(
    #     Link.link_id,
    #     func.avg(SpeedRecord.average_speed).label("average_speed"),
    #     Link.road_name,
    #     cast(Link._length, Float).label("length"),
    #     Link.usdk_speed_category,
    #     Link.speedcat
    # ).join(
    #     SpeedRecord, SpeedRecord.link_id == Link.link_id
    # ).filter(
    #     Link.link_id == link_id,
    #     SpeedRecord.day_of_week == day_dict.get(day,0),
    #     SpeedRecord.period == period_dict.get(period,0),
    # ).group_by(Link.link_id, 
    #            Link.road_name,
    #            Link._length,
    #            Link.usdk_speed_category,
    #            Link.speedcat).all()
    

    day_id = day_dict.get(day, None)
    if day_id is None:
        raise HTTPException(status_code=400, detail="Invalid day of week")
    
    start_datetime_str, end_datetime_str = convert_period_string_to_datetimes(period)
    if start_datetime_str is None or end_datetime_str is None:
        raise HTTPException(status_code=400, detail="Invalid period")


    results = db.query(
        Link.link_id,
        func.avg(SpeedRecord.average_speed).label("average_speed"),
        Link.road_name,
        cast(Link._length, Float).label("length"),
        Link.usdk_speed_category,
        Link.speedcat
    ).join(
        SpeedRecord, SpeedRecord.link_id == Link.link_id
    ).filter(
        Link.link_id == link_id,
        SpeedRecord.day_of_week == day_id,
        SpeedRecord.date_time >= start_datetime_str,
        SpeedRecord.date_time <= end_datetime_str
    ).group_by(Link.link_id, 
               Link.road_name,
               Link._length,
               Link.usdk_speed_category,
               Link.speedcat).all()

    # should ony be 1 item
    return_list =[]

    for link_id, average_speed, road_name, length, usdk_speed_category, speedcat in results:
        return_list.append({
            "link_id": link_id,
            "average_speed": average_speed,
            "road_name": road_name,
            "length": length,
            "usdk_speed_category": usdk_speed_category,
            "speedcat": speedcat
        })
    
    return return_list


@app.get("/patterns/slow_links/")
def get_slow_links(period:str, threshold:int, min_days:int, db: Session = Depends(get_db)):
    

    start_datetime_str, end_datetime_str = convert_period_string_to_datetimes(period)
    if start_datetime_str is None or end_datetime_str is None:
        raise HTTPException(status_code=400, detail="Invalid period")

    # results = db.query(
    #     SpeedRecord.link_id,
    #     func.count(SpeedRecord.day_of_week).label("days_count")
    # ).filter(
    #     SpeedRecord.period == period_dict.get(period,0),
    #     SpeedRecord.average_speed < threshold
    # ).group_by(SpeedRecord.link_id).having(
    #     func.count(SpeedRecord.day_of_week) >= min_days
    # ).all()

    results = db.query(
        SpeedRecord.link_id,
        func.count(SpeedRecord.day_of_week).label("days_count")
    ).filter(
        SpeedRecord.date_time >= start_datetime_str,
        SpeedRecord.date_time <= end_datetime_str,
        SpeedRecord.average_speed < threshold
    ).group_by(SpeedRecord.link_id).having(
        func.count(SpeedRecord.day_of_week) >= min_days
    ).all()
    

    return_list =[]
    for link_id, days in results:
        return_list.append({
            "link_id": link_id,
            "days_count": days
        }) 

    return return_list


@app.post("/aggregates/spatial_filter/")
def post_spatial_filter(json_req: SpatialFilter, db: Session = Depends(get_db)):
    
    start_datetime_str, end_datetime_str = convert_period_string_to_datetimes(json_req.period)
    if start_datetime_str is None or end_datetime_str is None:
        raise HTTPException(status_code=400, detail="Invalid period")

    if json_req.day not in day_dict:
        raise HTTPException(status_code=400, detail="Invalid day of week")
    # if json_req.period not in period_dict:   
    #     raise HTTPException(status_code=400, detail="Invalid period")
    if len(json_req.bbox) != 4:
        raise HTTPException(status_code=400, detail="Bbox must contain 4 values")
        
    # results = db.query(
    #     Link.link_id,
    #     Link.road_name
    #     ).join(
    #         SpeedRecord, SpeedRecord.link_id == Link.link_id
    #     ).filter(
    #         SpeedRecord.day_of_week == day_dict[json_req.day],
    #         SpeedRecord.period == period_dict[json_req.period],
    #         ST_Intersects(
    #             cast(Link.geometry, Geometry(geometry_type="MULTILINESTRING", srid=4326)),  
    #             ST_MakeEnvelope(*json_req.bbox, 4326))
    #     ).group_by(Link.link_id,
    #                Link.road_name 
    #     ).limit(10).all()

    results = db.query(
        Link.link_id,
        Link.road_name
        ).join(
            SpeedRecord, SpeedRecord.link_id == Link.link_id
        ).filter(
            SpeedRecord.day_of_week == day_dict.get(json_req.day, 0),
            SpeedRecord.date_time >= start_datetime_str,
            SpeedRecord.date_time <= end_datetime_str,
            ST_Intersects(
                cast(Link.geometry, Geometry(geometry_type="MULTILINESTRING", srid=4326)),  
                ST_MakeEnvelope(*json_req.bbox, 4326))
        ).group_by(Link.link_id,
                   Link.road_name 
        ).limit(10).all()

    return [{"link_id": link_id, 
            "road_name": road_name} for link_id, road_name, in results]