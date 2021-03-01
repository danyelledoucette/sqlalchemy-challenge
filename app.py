import numpy as np
import pandas as pandas
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from flask import Flask, jsonify

import datetime as dt

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
base=automap_base()
# reflect the tables
base.prepare(engine)

# View all of the classes that automap found
base.classes.keys()

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Query for start date, end date, and previous year
start_date=session.query(measurement.date).order_by((measurement.date)).limit(1).all()
print(start_date[0][0])

end_date=session.query(measurement.date).order_by((measurement.date).desc()).limit(1).all()
print(end_date[0][0])

previous_year = (dt.datetime.strptime(end_date[0][0], '%Y-%m-%d') - dt.timedelta(days=365)).date()
print(previous_year)

# Flask setup
app=Flask(__name__)


# Flask routes
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Precipitation status: Good")
    query_results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= previous_year)\
    .filter(measurement.station==station.station).all()
    
    total_prcp = []
    for total_prcp in query_results:
        row = {}
        row["date"]=query_results[0]
        row["prcp"]=query_results[1]
        total_prcp.append(row)
        
    return jsonify(total_prcp)

@app.route("/api/v1.0/stations")
def stations():
    print("station status: OK")
    query_stations = session.query(station.name, station.station)
    station_name = read_sql(station.statement, query_stations.session.bind)
    
    return jsonify(station_name.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    print("tobs status: OK")
    temp_results = session.query(measurement.date, measurement.tobs)\
    .filter(measurement.date >= previous_year)\
    .order_by(measurement.date).all()
    tobs_totals = []
    for results in temp_results:
        row = {}
        row["date"]=results[0]
        row["tobs"]=results[1]
        tobs_totals.append(row)
        
    return jsonify(tobs_totals)


@app.route("/api/v1.0/<start>")
def starting_date(start):
    print("start_date status:OK")
    beginning_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    last_date_dd = (dt.datetime.strptime(end_date[0][0], '%Y-%m-%d')).date() 
    first_date_dd = (dt.datetime.strptime(beginning_date[0][0], '%Y-%m-%d')).date()

    if beginning_date > last_date_dd or beginning_date < first_date_dd:
        return(f"Select date range between {beginning_date[0][0]} and {end_date[0][0]}")

    else:
        start_min_max_temp = session.query(func.min(measurement.tobs), func.avg(measurement.tobs),\
                                           func.max(measurement.tobs)).filter(measurement.date >= beginning_date).all()
        start_date_data = list(np.ravel(start_min_max_temp))
        return jsonify(start_date_data)


@app.route("/api/v1.0/<start>/<end>")
def ending_date(start,end):
    print("start and end status:OK")
    beginning_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    ending_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    last_date_dd = (dt.datetime.strptime(end_date[0][0], '%Y-%m-%d')).date() 
    first_date_dd = (dt.datetime.strptime(beginning_date[0][0], '%Y-%m-%d')).date()
    if beginning_date > last_date_dd or beginning_date < first_date_dd or ending_date > last_date_dd or\
    ending_date < first_date_dd:
        return(f"Select date range between {beginning_date[0][0]} and {end_date[0][0]}")
    else:
        start_end_min_max_temp = session.query(func.min(measurement.tobs), func.avg(measurement.tobs),\
                                               func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
        start_end_data = list(np.ravel(start_end_min_max_temp))
        return jsonify(start_end_data)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii weather API!<br/><br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>Returns a JSON representation of precipitation data for dates between {previous_year} and {end_date[0][0]}.<br/><br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of weather stations.<br/><br/>"
        f"/api/v1.0/tobs<br/>Returns a JSON list of the temperature observations (TOBS) for dates between {previous_year} and {end_date[0][0]}.<br/><br/>"
        f"/api/v1.0/yourstartdate(yyyy-mm-dd)<br/>Returns a JSON list of the minimum temperature, average temperature, and max temperature for the dates from the given start-end range. <br/><br/>"
        f"/api/v1.0/start_date(yyyy-mm-dd)/end_date(yyyy-mm-dd)<br/>Returns a JSON list of the minimum temperature, the average temperature, and the max temperature for the dates between the given start date and end date.<br/><br/>"
    )

if __name__=="__main__":
    app.run(debug=True)


