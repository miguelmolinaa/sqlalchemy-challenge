from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import numpy as np

app = Flask(__name__)

DATABASE_URI = "sqlite:///C:/Users/migue/OneDrive/Escritorio/bootcamp/sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Station(Base):
    __tablename__ = 'station'
    id = Column(Integer, primary_key=True)
    station = Column(String)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation = Column(Float)

class Measurement(Base):
    __tablename__ = 'measurement'
    id = Column(Integer, primary_key=True)
    station = Column(String, ForeignKey('station.station'))
    date = Column(String)  
    prcp = Column(Float)
    tobs = Column(Float)

@app.route("/")
def homepage():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session()
    latest_date = session.query(func.max(Measurement.date)).scalar()
    calculated_start_date = (dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")
    
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= calculated_start_date).all()
    session.close()
    
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session()
    stations = session.query(Station.station).all()
    session.close()
    
    stations_list = [station[0] for station in stations]
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session()
    latest_date = session.query(func.max(Measurement.date)).scalar()
    calculated_start_date = (dt.datetime.strptime(latest_date, "%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= calculated_start_date).all()
    session.close()
    
    temps = {date: temp for date, temp in results}
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session()
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Return temperature statistics for all dates greater than or equal to start date
    results = session.query(*sel).filter(Measurement.date >= start).all()
        
    session.close()

    temps = list(np.ravel(results))
    return jsonify({"TMIN": temps[0], "TAVG": temps[1], "TMAX": temps[2]})

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    session = Session()
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    # Return temperature statistics between start and end date
    results = session.query(*sel).filter(Measurement.date.between(start, end)).all()
    
    session.close()

    temps = list(np.ravel(results))
    return jsonify({"TMIN": temps[0], "TAVG": temps[1], "TMAX": temps[2]})

if __name__ == "__main__":
    app.run(debug=True)
