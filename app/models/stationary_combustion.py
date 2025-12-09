from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class StationaryCombustionEmission(Base):
    """
    Emission factors for stationary combustion (e.g., boilers).
    Represents Scope 1 emissions from burning fuels.
    Source: 'Dados auxiliares' sheet, ~Row 180
    """
    __tablename__ = "stationary_combustion_emissions"
    
    id = Column(Integer, primary_key=True, index=True)
    fuel_name = Column(String, index=True, nullable=False) # e.g. "Gás Natural", "Diesel A"
    unit = Column(String) # e.g. "kg", "m³", "litro"
    
    # Detailed GHG breakdown (g/unit) unless specified otherwise
    co2_fossil = Column(Float, default=0.0)
    co2_biogenic = Column(Float, default=0.0)
    ch4_fossil = Column(Float, default=0.0)
    ch4_biogenic = Column(Float, default=0.0)
    n2o_emission = Column(Float, default=0.0)
    
    # Final aggregated factor (kg CO2 eq/unit)
    # Note: Source table might show g/unit equivalent, carefully check unit conversion
    co2_eq_emission = Column(Float, default=0.0) 
