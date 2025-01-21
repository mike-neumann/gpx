import xml.etree.ElementTree as ET

from dateutil import parser
from flask import jsonify, Flask, request, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Sequence, desc

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tracks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"gpx"}

# Enable CORS for all routes
CORS(app)

db = SQLAlchemy(app)


# Database models
class Point(db.Model):
    __tablename__ = "point"
    point_id = db.Column(db.Integer, Sequence("point_id_sequence"), primary_key=True)
    point_track_id = db.Column(db.Integer, nullable=False)
    point_lat = db.Column(db.Float, nullable=False)
    point_lon = db.Column(db.Float, nullable=False)
    point_ele = db.Column(db.Float, nullable=True)
    point_timestamp = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "point_id": self.point_id,
            "point_track_id": self.point_track_id,
            "point_lat": self.point_lat,
            "point_lon": self.point_lon,
            "point_ele": self.point_ele,
            "point_timestamp": self.point_timestamp
        }


class Track(db.Model):
    __tablename__ = "track"
    track_id = db.Column(db.Integer, Sequence("track_id_sequence"), primary_key=True)
    track_file_name = db.Column(db.String(255), nullable=False)
    track_driver_id = db.Column(db.Integer, nullable=False)
    track_vehicle_id = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "track_id": self.track_id,
            "track_file_name": self.track_file_name,
            "track_driver_id": self.track_driver_id,
            "track_vehicle_id": self.track_vehicle_id
        }


class Vehicle(db.Model):
    __tablename__ = "vehicle"
    vehicle_id = db.Column(db.Integer, Sequence("vehicle_id_sequence"), primary_key=True)
    vehicle_license_plate = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "vehicle_id": self.vehicle_id,
            "vehicle_license_plate": self.vehicle_license_plate
        }


class Driver(db.Model):
    __tablename__ = "driver"
    driver_id = db.Column(db.Integer, Sequence("driver_id_sequence"), primary_key=True)
    driver_name = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "driver_id": self.driver_id,
            "driver_name": self.driver_name
        }


@app.route("/driver/<driver_id>")
def get_driver(driver_id):
    driver = Driver.query.filter_by(driver_id=driver_id).first()

    print(f"driver {driver_id} returned {driver}")

    if driver:
        return jsonify(driver.to_dict())
    else:
        return jsonify({})


@app.route("/driver", methods=["GET"])
def get_all_drivers():
    drivers = Driver.query.all()

    return jsonify([driver.to_dict() for driver in drivers])


@app.route("/vehicle/<vehicle_id>")
def get_vehicle(vehicle_id):
    vehicle = Vehicle.query.filter_by(vehicle_id=vehicle_id).first()

    if vehicle:
        return jsonify(vehicle.to_dict())
    else:
        return jsonify({})


@app.route("/vehicle", methods=["GET"])
def get_all_vehicles():
    vehicles = Vehicle.query.all()

    return jsonify([vehicle.to_dict() for vehicle in vehicles])


@app.route("/track", methods=["GET"])
def get_all_tracks():
    tracks = Track.query.all()

    return jsonify([track.to_dict() for track in tracks])


@app.route("/track/<driver_id>/<vehicle_id>", methods=["GET"])
def get_tracks(driver_id, vehicle_id):
    if driver_id == "undefined":
        driver_id = None
    if vehicle_id == "undefined":
        vehicle_id = None

    tracks = (Track.query
              .filter(Track.track_driver_id == driver_id if driver_id is not None else True == True)
              .filter(Track.track_vehicle_id == vehicle_id if vehicle_id is not None else True == True))

    return jsonify([track.to_dict() for track in tracks])


@app.route("/point/<track_id>", methods=["GET"])
def get_points(track_id):
    points = Point.query.filter_by(point_track_id=track_id).order_by(desc(Point.point_timestamp))

    return jsonify([point.to_dict() for point in points])


@app.route("/track", methods=["POST"])
def upload_track():
    request_data = request.get_json()
    file_name = request_data["file_name"]
    file_content = request_data["file_content"]
    gpx_save_message, gpx_save_status = parse_gpx_and_save(file_content, file_name)

    response = make_response()
    response.data = b"""
    {
        "message": "%s"
    }
    """ % gpx_save_message
    response.status_code = gpx_save_status

    return response


@app.route("/track/statistics/<track_id>", methods=["GET"])
def get_track_statistics(track_id):
    track = Track.query.filter_by(track_id=track_id).first()
    points = Point.query.filter_by(point_track_id=track_id)

    # TODO: calculate track statistics, sort by time, then calculate time and length in KM


def parse_gpx_and_save(file_content, file_name) -> tuple[bytes, int]:
    # Parse GPX content from file-like object
    tree = ET.ElementTree(ET.fromstring(file_content))
    root = tree.getroot()
    # we need to define default namespaces, if we dont, XPath cannot query single paths in xml tree
    namespaces = {"default": "http://www.topografix.com/GPX/1/1"}

    # before doing anything else, we need to check, if any tracks are even present in the file, it not, then this file is of no use, cancel operation.
    if len(root.findall(".//default:trk", namespaces)) == 0:
        return b"gpxContainsNoTracks", 400

    # Extract driver and vehicle information from the file_name
    driver_name, vehicle_license_plate = file_name.split("_")[:2]
    driver = Driver.query.filter_by(driver_name=driver_name).first()
    vehicle = Vehicle.query.filter_by(vehicle_license_plate=vehicle_license_plate).first()
    track = Track.query.filter_by(track_file_name=file_name).first()

    if not driver:
        # Save driver to db
        new_driver = Driver()
        new_driver.driver_name = driver_name

        db.session.add(new_driver)
        db.session.commit()
        driver = new_driver
    if not vehicle:
        # Save vehicle to db
        new_vehicle = Vehicle()
        new_vehicle.vehicle_license_plate = vehicle_license_plate

        db.session.add(new_vehicle)
        db.session.commit()
        vehicle = new_vehicle

    if track:
        # Track already exists, dont upload
        return b"uploadTrackAlreadyExists", 400

    # Else we can then save the track into the database after reading its xml contents

    track = Track(track_file_name=file_name, track_driver_id=driver.driver_id, track_vehicle_id=vehicle.vehicle_id)
    db.session.add(track)
    db.session.commit()

    # Parse GPX data and save points
    for trkpt in root.findall(".//default:trkpt", namespaces):
        try:
            lat = float(trkpt.get("lat"))
            lon = float(trkpt.get("lon"))
            ele = trkpt.find("default:ele", namespaces).text if trkpt.find("default:ele",
                                                                           namespaces) is not None else None
            timestamp = trkpt.find("default:time", namespaces).text
            point = Point(
                point_track_id=track.track_id,
                point_lat=lat,
                point_lon=lon,
                point_ele=float(ele) if ele else None,
                point_timestamp=parser.isoparse(timestamp)
            )
            db.session.add(point)
        except Exception as e:
            # we have encountered some error while trying to extract all needed information for a waypoint, continue here and try to extract other information
            continue
    db.session.commit()

    return b"uploadSuccessful", 200


if __name__ == "__main__":
    with app.app_context():
        # Create database tables
        db.create_all()
    app.run(debug=True)
