from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class MiscWeather(Base):
    """ Misc Weather """

    __tablename__ = "misc_weather"

    id = Column(Integer, primary_key=True)
    location_id = Column(String(250), nullable=False)
    location_name = Column(String(250), nullable=False)
    precipitation = Column(String(250), nullable=False)
    humidity = Column(String(250), nullable=False)
    wind = Column(String(250), nullable=False)
    air_quality = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, location_id, location_name, precipitation, humidity, wind, air_quality, timestamp):
        """ Initializes a misc weather report """
        self.location_id = location_id
        self.location_name = location_name
        self.precipitation = precipitation
        self.humidity = humidity
        self.wind = wind
        self.air_quality = air_quality
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a misc weather report """
        dict = {}
        dict['id'] = self.id
        dict['location_id'] = self.location_id
        dict['location_name'] = self.location_name
        dict['precipitation'] = self.precipitation
        dict['humidity'] = self.humidity
        dict['wind'] = self.wind
        dict['air_quality'] = self.air_quality
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
