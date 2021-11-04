from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class WeatherForecast(Base):
    """ Weather Forecast """

    __tablename__ = "weather_forecast"

    id = Column(Integer, primary_key=True)
    location_id = Column(String(250), nullable=False)
    location_name = Column(String(250), nullable=False)
    weather = Column(String(250), nullable=False)
    temperature = Column(String(250), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, location_id, location_name, weather, temperature, timestamp):
        """ Initializes a weather forecast"""
        self.location_id = location_id
        self.location_name = location_name
        self.weather = weather
        self.temperature = temperature
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a weather forecast """
        dict = {}
        dict['id'] = self.id
        dict['location_id'] = self.location_id
        dict['location_name'] = self.location_name
        dict['weather'] = self.weather
        dict['temperature'] = self.temperature
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict