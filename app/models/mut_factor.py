from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class MUTFactor(Base):
    """Emission factors for Land Use Change (MUT) by state and culture"""
    __tablename__ = "mut_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String, index=True, nullable=False)
    culture = Column(String, nullable=False)  # Pinus, Eucalipto, Amendoim
    emission_factor = Column(Float, nullable=False)  # tCO2eq/ha/yr or similar normalized factor
