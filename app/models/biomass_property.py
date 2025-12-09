from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base


class BiomassProperty(Base):
    __tablename__ = "biomass_properties"
    
    id = Column(Integer, primary_key=True, index=True)
    biomass_name = Column(String, unique=True, index=True, nullable=False)
    pci_mj_kg = Column(Float, nullable=False)  # PCI em MJ/kg
    combustion_emission = Column(Float)  # kg CO2 eq/MJ (combustão estacionária)
