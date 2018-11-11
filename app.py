import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from sqlalchemy.pool import StaticPool
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",
        connect_args={'check_same_thread':False},
                    poolclass=StaticPool)
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"<br/>"  
        f"/api/v1.0/precipitation - "
        f"Dates and Precipation for last year available<br/>"
        f"<br/>"  
        f"/api/v1.0/stations - "
        f"List of Hawaiian Weather Stations<br/>"
        f"<br/>"  
        f"/api/v1.0/tobs - "
        f"List of Temperature Observations for last year available<br/>"
        f"<br/>"  
        f"/api/v1.0/start - "
        f"Minimum, Average and Maximum Temperatues over time for a Start Date<br/>"
        f"Date should be entered as YYYY-MM-DD<br/>"   
        f"<br/>"     
        f"/api/v1.0/start/end - "
        f"Minimum, Average and Maximum Temperatues over time for a Start Date and End Date Range<br/>"
        f"Date Range should be entered as YYYY-MM-DD/YYYY-MM-DD"
    )

# /api/v1.0/precipitation
# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    ##sel = Measurement.date, func.sum(Measurement.prcp)
    date = dt.datetime(2016, 8, 23)

    yr_prcp = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > date).\
    order_by(Measurement.date).all()

    precipitation = []

    for M in yr_prcp:
        precipitation_dict = {}
        precipitation_dict["Date"] = M.date
        precipitation_dict["Precipitation"] = M.prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()

    stations = list(np.ravel(results))

    return jsonify(stations)


# /api/v1.0/tobs
# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():

    date = dt.datetime(2016, 8, 23)

    temp_obs2 = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date > date).all()

    temps = list(np.ravel(temp_obs2))

    return jsonify(temps)



# /api/v1.0/<start> 
@app.route("/api/v1.0/<start_date>")
def calc_temps(start_date):

    start = dt.datetime.strptime(start_date, '%Y-%m-%d')

    start_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all() 

    temps2 = list(np.ravel(start_temp)) 

    return jsonify(temps2)
    
    
 
# /api/v1.0/<start>/<end>
@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps_end(start_date, end_date):

    start = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end = dt.datetime.strptime(end_date, '%Y-%m-%d')    
    
    start_end = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).all()

    temps_end = list(np.ravel(start_end)) 

    return jsonify(temps_end)

     


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.


if __name__ == '__main__':
    app.run(debug=True, port=5002)
