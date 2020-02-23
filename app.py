
## Step 2 - Climate App
#Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed.

## Hints
#* You will need to join the station and measurement tables for some of the analysis queries.
#* Use Flask `jsonify` to convert your API data into a valid JSON response object.

#################################################
## Import Dependancies
#################################################

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create the engine and db connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#* Use FLASK to create your routes.
#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# From the homepage "/" list all routes that are available.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"<b>Available Routes:</b><br/>"
        f"<br/>"
        f"<b>Stats:</b><br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperatures for last year: /api/v1.0/tobs<br/>"
        f"<br/>"
        f"<b>Stats for Dates:</b><br/>"
        f"Temperature stats a specific date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stats from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
        f"<br/>"
        f"<b>** Note: </b>First Record Date: 2010-01-01 , Last Record Date: 2017-08-23<br/>" # from jupyter notebook
    )

##* `/api/v1.0/precipitation`
#  * Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
#  * Return the JSON representation of your dictionary.

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precip = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precip.append(prcp_dict)

    return jsonify(precip)

#* `/api/v1.0/stations`
#  * Return a JSON list of stations from the dataset.

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    sel = [Station.station,Station.name]
    queryresult = session.query(*sel).all()
    session.close()

    stations = []
    for station,name in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        stations.append(station_dict)

    return jsonify(stations)

#* `/api/v1.0/tobs`
#  * query for the dates and temperature observations from a year from the last data point.
#  * Return a JSON list of Temperature Observations (tobs) for the previous year.

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    lateststr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    latestdate = dt.datetime.strptime(lateststr, '%Y-%m-%d')
    querydate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    qrysel = [Measurement.date,Measurement.tobs]
    queryresult = session.query(*qrysel).filter(Measurement.date >= querydate).all()
    session.close()

    all_tobs = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

#* `/api/v1.0/<start>`
#  * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
#  * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    all_tobs = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

#* `/api/v1.0/<start>/<end>`
#  * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
#  * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    all_tobs = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

if __name__ == '__main__':
    app.run(debug=True)