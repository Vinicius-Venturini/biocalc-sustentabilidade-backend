from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProjectBase(BaseModel):
    name: str = Field(..., description="Nome do projeto")
    
    # Company data
    company_name: Optional[str] = None
    cnpj: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    tech_responsible: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    # Biomass data
    biomass_type: Optional[str] = Field(None, description="Tipo de biomassa")
    production_volume: Optional[float] = Field(None, gt=0, description="Volume de produção (t/ano)")
    biomass_consumption_known: Optional[str] = Field(None, pattern="^(Sim|Não)$")
    biomass_consumption_value: Optional[float] = None
    production_state: Optional[str] = None
    wood_residue_stage: Optional[str] = None
    starch_input: Optional[float] = Field(None, ge=0)
    
    # Agricultural transport
    agr_transport_distance: Optional[float] = Field(None, ge=0)
    agr_transport_vehicle: Optional[str] = None
    
    # Industrial data
    biomass_processed: Optional[float] = Field(None, ge=0)
    water_consumption: Optional[float] = Field(None, ge=0)
    
    # Electricity (kWh/ano)
    elec_grid: Optional[float] = Field(0, ge=0)
    elec_solar: Optional[float] = Field(0, ge=0)
    elec_wind: Optional[float] = Field(0, ge=0)
    elec_hydro: Optional[float] = Field(0, ge=0)
    elec_biomass: Optional[float] = Field(0, ge=0)
    elec_other: Optional[float] = Field(0, ge=0)
    
    # Fuels
    fuel_diesel: Optional[float] = Field(0, ge=0)
    fuel_gasoline: Optional[float] = Field(0, ge=0)
    fuel_ethanol: Optional[float] = Field(0, ge=0)
    fuel_biodiesel: Optional[float] = Field(0, ge=0)
    fuel_gnv: Optional[float] = Field(0, ge=0)
    fuel_lpg: Optional[float] = Field(0, ge=0)
    fuel_biomass: Optional[float] = Field(0, ge=0)
    fuel_other: Optional[float] = Field(0, ge=0)
    
    # Other inputs
    input_lubricant: Optional[float] = Field(0, ge=0)
    input_chemical: Optional[float] = Field(0, ge=0)
    input_other: Optional[float] = Field(0, ge=0)
    
    # Domestic transport
    dom_mass: Optional[float] = Field(None, ge=0)
    dom_distance: Optional[float] = Field(None, ge=0)
    dom_modal_road_pct: Optional[float] = Field(100, ge=0, le=100)
    dom_modal_rail_pct: Optional[float] = Field(0, ge=0, le=100)
    dom_vehicle_type: Optional[str] = None
    
    # Export transport
    exp_mass: Optional[float] = Field(None, ge=0)
    exp_factory_port_dist: Optional[float] = Field(None, ge=0)
    exp_modal_road_pct: Optional[float] = Field(100, ge=0, le=100)
    exp_modal_rail_pct: Optional[float] = Field(0, ge=0, le=100)
    exp_modal_water_pct: Optional[float] = Field(0, ge=0, le=100)
    exp_vehicle_port: Optional[str] = None
    exp_port_consumer_dist: Optional[float] = Field(None, ge=0)


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    # All other fields optional for updates
    # (simplified for brevity - in production, include all fields as Optional)


class ProjectResults(BaseModel):
    """Calculated results"""
    carbon_intensity: float = Field(..., description="Intensidade de carbono (kg CO₂eq/MJ)")
    agricultural_emissions: float
    industrial_emissions: float
    transport_emissions: float
    use_emissions: float
    efficiency_note: float = Field(..., description="Nota de eficiência")
    emission_reduction: float = Field(..., description="Redução de emissões (%)")
    cbios: int = Field(..., description="CBIOs gerados")
    cbios_revenue: float = Field(..., description="Remuneração estimada (R$)")


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    status: str
    current_step: int  # Progresso (0-10)
    pci: Optional[float] = None
    
    # Calculated results
    carbon_intensity: Optional[float] = None
    agricultural_emissions: Optional[float] = None
    industrial_emissions: Optional[float] = None
    transport_emissions: Optional[float] = None
    use_emissions: Optional[float] = None
    efficiency_note: Optional[float] = None
    emission_reduction: Optional[float] = None
    cbios: Optional[int] = None
    cbios_revenue: Optional[float] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectListItem(BaseModel):
    """Simplified project for listing"""
    id: int
    name: str
    biomass_type: str
    status: str
    current_step: int  # Progresso (0-10)
    carbon_intensity: Optional[float] = None
    cbios: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
