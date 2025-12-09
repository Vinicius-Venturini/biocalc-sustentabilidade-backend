from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    DRAFT = "Em Rascunho"
    COMPLETED = "Concluído"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Project info
    name = Column(String, nullable=False)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    current_step = Column(Integer, default=0)  # Rastreia progresso (0-10)
    
    # Company data
    company_name = Column(String)
    cnpj = Column(String)
    state = Column(String)
    city = Column(String)
    tech_responsible = Column(String)
    phone = Column(String)
    email = Column(String)
    
    # Biomass data
    biomass_type = Column(String)  # Tipo de biomassa (Required in Step 1)
    pci = Column(Float)  # Poder calorífico inferior (MJ/kg) - auto
    production_volume = Column(Float)  # Volume de produção (t/ano) (Required in Step 10)
    biomass_consumption_known = Column(String)  # "Sim" ou "Não"
    biomass_consumption_value = Column(Float)  # kg biomassa / kg biocombustível
    production_state = Column(String)  # Estado da produção
    wood_residue_stage = Column(String)  # Etapa do ciclo (se resíduo)
    starch_input = Column(Float)  # Entrada de amido de milho (kg/MJ)
    
    # Agricultural transport
    agr_transport_distance = Column(Float)  # Distância (km)
    agr_transport_vehicle = Column(String)  # Tipo de veículo
    
    # Industrial data
    biomass_processed = Column(Float)  # Quantidade processada (kg/ano)
    water_consumption = Column(Float)  # Consumo de água (m³/ano)
    
    # Electricity consumption (kWh/ano)
    elec_grid = Column(Float, default=0)
    elec_solar = Column(Float, default=0)
    elec_wind = Column(Float, default=0)
    elec_hydro = Column(Float, default=0)
    elec_biomass = Column(Float, default=0)
    elec_other = Column(Float, default=0)
    
    # Fuel consumption (L/ano or kg/ano)
    fuel_diesel = Column(Float, default=0)
    fuel_gasoline = Column(Float, default=0)
    fuel_ethanol = Column(Float, default=0)
    fuel_biodiesel = Column(Float, default=0)
    fuel_gnv = Column(Float, default=0)
    fuel_lpg = Column(Float, default=0)
    fuel_biomass = Column(Float, default=0)
    fuel_other = Column(Float, default=0)
    
    # Other inputs
    input_lubricant = Column(Float, default=0)
    input_chemical = Column(Float, default=0)
    input_other = Column(Float, default=0)
    
    # Domestic transport
    dom_mass = Column(Float)  # Massa transportada (kg/ano)
    dom_distance = Column(Float)  # Distância média (km)
    dom_modal_road_pct = Column(Float, default=100)  # % Rodoviário
    dom_modal_rail_pct = Column(Float, default=0)  # % Ferroviário
    dom_vehicle_type = Column(String)  # Tipo de veículo
    
    # Export transport
    exp_mass = Column(Float)  # Massa exportada (t/ano)
    exp_factory_port_dist = Column(Float)  # Distância fábrica-porto (km)
    exp_modal_road_pct = Column(Float, default=100)  # % Rodoviário
    exp_modal_rail_pct = Column(Float, default=0)  # % Ferroviário
    exp_modal_water_pct = Column(Float, default=0)  # % Hidroviário
    exp_vehicle_port = Column(String)  # Tipo de veículo (porto)
    exp_port_consumer_dist = Column(Float)  # Distância marítima (km)
    
    # Calculated results
    carbon_intensity = Column(Float)  # Intensidade de carbono (kg CO₂eq/MJ)
    agricultural_emissions = Column(Float)  # Emissões agrícolas
    industrial_emissions = Column(Float)  # Emissões industriais
    transport_emissions = Column(Float)  # Emissões de transporte
    use_emissions = Column(Float)  # Emissões de uso
    efficiency_note = Column(Float)  # Nota de eficiência
    emission_reduction = Column(Float)  # Redução de emissões (%)
    cbios = Column(Integer)  # CBIOs gerados
    cbios_revenue = Column(Float)  # Remuneração estimada (R$)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="projects")
