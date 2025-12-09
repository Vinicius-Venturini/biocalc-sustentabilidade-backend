from pydantic import BaseModel
from typing import Optional


class BiomassPropertyResponse(BaseModel):
    id: int
    biomass_name: str
    pci_mj_kg: float
    combustion_emission: Optional[float] = None
    
    class Config:
        from_attributes = True


class VehicleEmissionFactorResponse(BaseModel):
    id: int
    vehicle_type: str
    emission_factor: float
    
    class Config:
        from_attributes = True


class GWPFactorResponse(BaseModel):
    id: int
    gas_name: str
    gwp_value: float
    
    class Config:
        from_attributes = True
