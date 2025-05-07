import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy import text

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)

print("B4 engine connect")
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS "SpeedRecord"'))
    conn.execute(text('DROP TABLE IF EXISTS "Link"'))
    conn.close()

print("reading parquet files")
speed = pd.read_parquet(r"C:\Users\kylej\Documents\Github\UrbanSDK\duval_jan1_2024.parquet.gz", engine="pyarrow")
link = pd.read_parquet(r"C:\Users\kylej\Documents\Github\UrbanSDK\link_info.parquet.gz", engine="pyarrow")

print("storing data")
speed.to_sql("SpeedRecord", engine, if_exists="append", index=False)
link.to_sql("Link", engine, if_exists="append", index=False)

print("adding geometry data from geojson")
with engine.connect() as conn:
    conn.execute(text("""
        UPDATE "Link"
        SET geometry = ST_SetSRID(ST_GeomFromGeoJSON(geo_json::text), 4326)
        WHERE geo_json IS NOT NULL;
    """))
    conn.commit() 

print("Done")


