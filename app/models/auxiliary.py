from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base


class GWPFactor(Base):
    """Global Warming Potential factors for greenhouse gases"""
    __tablename__ = "gwp_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    gas_name = Column(String, unique=True, index=True, nullable=False)
    gwp_value = Column(Float, nullable=False)  # kg CO2eq/kg


class BiomassProductionEmission(Base):
    """Emission factors for biomass production"""
    __tablename__ = "biomass_production_emissions"
    
    id = Column(Integer, primary_key=True, index=True)
    biomass_name = Column(String, index=True, nullable=False)
    emission_factor = Column(Float, nullable=False)  # kg CO2 eq/kg biomassa
    allocation_product = Column(Float, default=0.0)  # % alocação produto
    allocation_coproduct = Column(Float, default=1.0)  # % alocação co-produto
    biomass_type = Column(String)  # Tipo (Pinus, Eucalipto, Amendoin)


class TransportModalFactor(Base):
    """Emission factors by transport modal"""
    __tablename__ = "transport_modal_factors"
    
    id = Column(Integer, primary_key=True, index=True)
    modal_type = Column(String, index=True, nullable=False)  # road, rail, water, maritime
    emission_factor = Column(Float, nullable=False)  # kg CO2 eq/t.km


class IndustrialInputEmission(Base):
    """Emission factors for industrial inputs"""
    __tablename__ = "industrial_input_emissions"
    
    id = Column(Integer, primary_key=True, index=True)
    input_name = Column(String, index=True, nullable=False)
    input_type = Column(String)  # electricity, fuel, water, chemical, etc
    emission_factor = Column(Float, nullable=False)  # kg CO2 eq/unit
    unit = Column(String)  # kWh, L, m³, kg, etc
