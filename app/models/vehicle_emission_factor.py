from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base


class VehicleEmissionFactor(Base):
    __tablename__ = "vehicle_emission_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String, unique=True, index=True, nullable=False)
    emission_factor = Column(Float, nullable=False)  # kg CO2 eq/t.km
