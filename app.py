import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base=automap_base()
# reflect the tables
base.prepare(engine, reflect=True)

# View all of the classes that automap found
base.classes.keys()

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

session=Session(engine)

# # Query for start date, end date, and previous year
start_date=session.query(measurement.date).order_by((measurement.date)).limit(1).all()
# print(start_date[0][0])

end_date=session.query(measurement.date).order_by((measurement.date).desc()).limit(1).all()
# print(end_date[0][0])

previous_year = (dt.datetime.strptime(end_date[0][0], '%Y-%m-%d') - dt.timedelta(days=365)).date()
# print(previous_year)

# Flask setup
app=Flask(__name__)

# Flask routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii weather API!<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>Returns a JSON representation of precipitation data for dates between {previous_year} and {end_date[0][0]}.<br/><br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of weather stations.<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns a JSON list of the temperature observations (TOBS) for dates between {previous_year} and {end_date[0][0]}.<br/><br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>Returns a JSON list of the minimum temperature, average temperature, and max temperature for the dates from the given start-end range. <br/><br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between a given start date and end date.<br/><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= previous_year)\
    .filter(measurement.station==station.station).all()
    
    session.close()

    total_prcp = []
    for result in results:
        prcp_dict = {}
        prcp_dict["date"]=result[0]
        prcp_dict["prcp"]=result[1]
        total_prcp.append(prcp_dict)
            
    return jsonify(total_prcp)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_name = session.query(station.station).all()
    # print(query_stations)
    session.close()
    
    return jsonify(list(np.ravel(station_name)))

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    temp_results = session.query(measurement.date, measurement.tobs)\
    .filter(measurement.date >= previous_year)\
    .order_by(measurement.date).all()

    session.close()

    tobs_totals = []
    for results in temp_results:
        row = {}
        row["date"]=results[0]
        row["tobs"]=results[1]
        tobs_totals.append(row)
        
    return jsonify(tobs_totals)


@app.route("/api/v1.0/<start>")
def starting_date(start):
    session = Session(engine)
    result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()

    tobs = []
    for min,avg,max in result:
        temp_dict = {}
        temp_dict["Min"]=min
        temp_dict["Average"]=avg
        temp_dict["Max"]=max
        tobs.append(temp_dict)

    return jsonify(tobs)


@app.route("/api/v1.0/<start>/<stop>")
def start_stop(start,stop):
    session = Session(engine)
    result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= stop).all()
    session.close()

    tobs = []
    for min,avg,max in result:
        temp_dict = {}
        temp_dict["Min"]=min
        temp_dict["Average"]=avg
        temp_dict["Max"]=max
        tobs.append(temp_dict)

    return jsonify(tobs)


if __name__=="__main__":
    app.run(debug=True)