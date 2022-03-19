from matplotlib.pyplot import close
import numpy as np
import re
import datetime as dt
import pandas as pd 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists  

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii2.sqlite")

Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
Base.prepare

Measurement = Base.classes.measurement
Station = Base.classes.station

Ankita_session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"

    )

@app.route("/api/v1.0/precipitation") 
def precipitation():
    
    session = Session(engine)

    # Query Measurement
    results = (session.query(Measurement.date, Measurement.tobs)
                      .order_by(Measurement.date))
    
    # Create a dictionary
    precipitation_date_tobs = []
    for each_row in results:
        dt_dict = {}
        dt_dict["date"] = each_row.date
        dt_dict["tobs"] = each_row.tobs
        precipitation_date_tobs.append(dt_dict)
    session.close 
    return jsonify(precipitation_date_tobs)

@app.route("/api/v1.0/stations") #Return a JSON list of stations from the dataset
def stations():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Query Stations
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    station_details = list(np.ravel(results))

    return jsonify(station_details)

@app.route("/api/v1.0/tobs") # Query the dates and temperature observations of the most active station for the last year of data
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query Measurements for latest date and calculate query_start_date
    latest_date = (session.query(Measurement.date)
                          .order_by(Measurement.date
                          .desc())
                          .first())
    
    latest_date_str = str(latest_date)
    latest_date_str = re.sub("'|,", "",latest_date_str)
    latest_date_obj = dt.datetime.strptime(latest_date_str, '(%Y-%m-%d)')
    query_start_date = dt.date(latest_date_obj.year, latest_date_obj.month, latest_date_obj.day) - dt.timedelta(days=366)
     
    # Query station names and their observation counts sorted descending and select most active station
    q_station_list = (session.query(Measurement.station, func.count(Measurement.station))
                             .group_by(Measurement.station)
                             .order_by(func.count(Measurement.station).desc())
                             .all())
    
    station_hno = q_station_list[0][0]
    print(station_hno)

@app.route("/api/v1.0/<start>") # Calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
def start_only(start):

    # Create session (link) from Python to the DB
    session = Session(engine)

    # Date Range (only for help to user in case date gets entered wrong)
    date_range_max = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    date_range_max_str = str(date_range_max)
    date_range_max_str = re.sub("'|,", "",date_range_max_str)
    print (date_range_max_str)

    date_range_min = session.query(Measurement.date).first()
    date_range_min_str = str(date_range_min)
    date_range_min_str = re.sub("'|,", "",date_range_min_str)
    print (date_range_min_str)
    valid_entry = session.query(exists().where(Measurement.date == start)).scalar()

    if valid_entry:
        results = (session.query(func.min(Measurement.tobs)
                            ,func.avg(Measurement.tobs)
                            ,func.max(Measurement.tobs))
                                    .filter(Measurement.date >= start).all())

        tmin =results[0][0]
        tavg ='{0:.4}'.format(results[0][1])
        tmax =results[0][2]

        result_printout =(['Entered Start Date: ' + start,
                        'The lowest Temperature was: '  + str(tmin) + ' F',
                        'The average Temperature was: ' + str(tavg) + ' F',
                        'The highest Temperature was: ' + str(tmax) + ' F'])
        return jsonify(result_printout)
    
if __name__ == "__main__":
    app.run(debug=True)



