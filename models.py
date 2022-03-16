import os
import re
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float, create_engine
from sqlalchemy.sql.expression import cast
from sqlalchemy import func
from sqlalchemy.types import UserDefinedType

db = SQLAlchemy()

'''
setup_db(app):
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    database_path = os.getenv('DATABASE_URL', 'DATABASE_URL_WAS_NOT_SET?!')

    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
    drops the database tables and starts fresh
    can be used to initialize a clean database
'''
def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

    # Initial sample data:
    insert_sample_locations()

def insert_sample_locations():
    loc1 = SampleLocation(
        description='Brandenburger Tor',
        geom=Geometry.point_representation(
            latitude=52.516247, 
            longitude=13.377711
        )
    )
    loc1.insert()

    loc2 = SampleLocation(
        description='Schloss Charlottenburg',
        geom=Geometry.point_representation(
            latitude=52.520608, 
            longitude=13.295581
        )
    )
    loc2.insert()

    loc3 = SampleLocation(
        description='Tempelhofer Feld',
        geom=Geometry.point_representation(
            latitude=52.473580, 
            longitude=13.405252
        )
    )
    loc3.insert()

# This is needed to be able to have properties of type 
# Geometry in your own models when using a MySql DB
# For more reference see https://docs.sqlalchemy.org/en/14/core/custom_types.html
class Geometry(UserDefinedType):
    def get_col_spec(self):
        return 'GEOMETRY' 

    def bind_expression(self, bindvalue):
        return func.ST_GeomFromText(bindvalue, SpatialConstants.SRID, type_=self)

    def column_expression(self, col):
        return func.ST_AsText(col, type_=self)

    @staticmethod
    def point_representation(latitude, longitude):
        return 'POINT(%s %s)' % (longitude, latitude)

    @staticmethod
    def extract_from_point_representation(point_representation):
        # Using a regex here would be better,
        # Using a quick solution of stripping and splitting instead:
        stripped_values = point_representation.replace("POINT(", "").replace(")", "")
        coordinates = stripped_values.split(" ")
        return [float(x) for x in coordinates]


class SpatialConstants:
    SRID = 4326

class SampleLocation(db.Model):
    __tablename__ = 'sample_locations'

    id = Column(Integer, primary_key=True)
    description = Column(String(80))

    # This is how we will represent where is this item located in the map / in earth:
    # as a POINT, that is a special (the simplest) type of Geometry
    # see this for a nice explanation on alternatives: http://mysql.rjweb.org/doc.php/find_nearest_in_mysql
    geom = Column(Geometry, nullable=False)

    @staticmethod
    def get_items_within_radius(lat, lng, radius):
        """Return all sample locations within a given radius (in meters)"""

        #TODO: The arbitrary limit = 100 is just a quick way to make sure 
        # we won't return tons of entries at once, 
        # paging needs to be in place for real usecase
        results = SampleLocation.query.filter(
            func.st_distance_sphere(
                SampleLocation.geom, 
                func.ST_GeomFromText(Geometry.point_representation(lat, lng), SpatialConstants.SRID)
            ) <= radius
        ).limit(100).all() 

        print("results: ")
        print(results)
        return [l.to_dict() for l in results]    

    def get_location_latitude(self):
        point = Geometry.extract_from_point_representation(self.geom)
        return point[1]

    def get_location_longitude(self):
        point = Geometry.extract_from_point_representation(self.geom)
        return point[0]

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'location': {
                'lng': self.get_location_longitude(),
                'lat': self.get_location_latitude()
            }
        }    

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()         