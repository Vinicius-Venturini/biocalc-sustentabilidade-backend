from pydantic import BaseModel, Field, EmailStr
from typing import Optional


# ============================================================================
# STEP 0: Identificação do Projeto
# ============================================================================

class ProjectStep0(BaseModel):
    """Step 0: Dados de identificação da empresa e projeto"""
    name: str = Field(..., description="Nome do projeto")
    company_name: Optional[str] = None
    cnpj: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    tech_responsible: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


# ============================================================================
# FASE AGRÍCOLA
# ============================================================================

class ProjectStep1(BaseModel):
    """Step 1: Produção de Biomassa"""
    biomass_type: str = Field(..., description="Tipo de biomassa")
    biomass_consumption_known: Optional[str] = Field(None, pattern="^(Sim|Não)$")
    biomass_consumption_value: Optional[float] = Field(None, ge=0, description="kg biomassa/kg biocombustível")
    starch_input: Optional[float] = Field(None, ge=0, description="Entrada de amido de milho (kg/MJ)")


class ProjectStep2(BaseModel):
    """Step 2: Mudança de Uso da Terra (MUT)"""
    production_state: Optional[str] = Field(None, description="Estado da produção da biomassa")
    wood_residue_stage: Optional[str] = Field(None, description="Etapa do ciclo de vida (se resíduo de madeira)")


class ProjectStep3(BaseModel):
    """Step 3: Transporte da Biomassa até a Fábrica"""
    agr_transport_distance: Optional[float] = Field(None, ge=0, description="Distância (km)")
    agr_transport_vehicle: Optional[str] = Field(None, description="Tipo de veículo")


# ============================================================================
# FASE INDUSTRIAL
# ============================================================================

class ProjectStep4(BaseModel):
    """Step 4: Dados do Sistema Industrial"""
    has_cogeneration: Optional[str] = Field(None, pattern="^(Sim|Não)$", description="Existe co-geração?")
    biomass_processed: Optional[float] = Field(None, ge=0, description="Quantidade processada (kg/ano)")
    biomass_cogeneration: Optional[float] = Field(None, ge=0, description="Biomassa consumida na co-geração (kg/ano)")


class ProjectStep5(BaseModel):
    """Step 5: Consumo de Eletricidade"""
    elec_grid: Optional[float] = Field(0, ge=0, description="Rede elétrica (kWh/ano)")
    elec_solar: Optional[float] = Field(0, ge=0, description="Solar (kWh/ano)")
    elec_wind: Optional[float] = Field(0, ge=0, description="Eólica (kWh/ano)")
    elec_hydro: Optional[float] = Field(0, ge=0, description="Hidrelétrica (kWh/ano)")
    elec_biomass: Optional[float] = Field(0, ge=0, description="Biomassa (kWh/ano)")
    elec_other: Optional[float] = Field(0, ge=0, description="Outras (kWh/ano)")


class ProjectStep6(BaseModel):
    """Step 6: Consumo de Combustíveis"""
    fuel_diesel: Optional[float] = Field(0, ge=0, description="Diesel (L/ano)")
    fuel_gasoline: Optional[float] = Field(0, ge=0, description="Gasolina (L/ano)")
    fuel_ethanol: Optional[float] = Field(0, ge=0, description="Etanol (L/ano)")
    fuel_biodiesel: Optional[float] = Field(0, ge=0, description="Biodiesel (L/ano)")
    fuel_gnv: Optional[float] = Field(0, ge=0, description="GNV (m³/ano)")
    fuel_lpg: Optional[float] = Field(0, ge=0, description="GLP (kg/ano)")
    fuel_biomass: Optional[float] = Field(0, ge=0, description="Biomassa (kg/ano)")
    fuel_other: Optional[float] = Field(0, ge=0, description="Outros (L/ano)")


class ProjectStep7(BaseModel):
    """Step 7: Outros Insumos Industriais"""
    water_consumption: Optional[float] = Field(None, ge=0, description="Consumo de água (m³/ano)")
    input_lubricant: Optional[float] = Field(0, ge=0, description="Lubrificantes (kg/ano)")
    input_chemical: Optional[float] = Field(0, ge=0, description="Químicos (kg/ano)")
    input_other: Optional[float] = Field(0, ge=0, description="Outros insumos (kg/ano)")


# ============================================================================
# FASE DE DISTRIBUIÇÃO
# ============================================================================

class ProjectStep8(BaseModel):
    """Step 8: Transporte Doméstico"""
    dom_mass: Optional[float] = Field(None, ge=0, description="Massa transportada (kg/ano)")
    dom_distance: Optional[float] = Field(None, ge=0, description="Distância média (km)")
    dom_modal_road_pct: Optional[float] = Field(100, ge=0, le=100, description="% Modal rodoviário")
    dom_modal_rail_pct: Optional[float] = Field(0, ge=0, le=100, description="% Modal ferroviário")
    dom_vehicle_type: Optional[str] = Field(None, description="Tipo de veículo")


class ProjectStep9(BaseModel):
    """Step 9: Transporte Exportação (Opcional)"""
    exp_mass: Optional[float] = Field(None, ge=0, description="Massa exportada (t/ano)")
    exp_factory_port_dist: Optional[float] = Field(None, ge=0, description="Distância fábrica-porto (km)")
    exp_modal_road_pct: Optional[float] = Field(100, ge=0, le=100, description="% Modal rodoviário")
    exp_modal_rail_pct: Optional[float] = Field(0, ge=0, le=100, description="% Modal ferroviário")
    exp_modal_water_pct: Optional[float] = Field(0, ge=0, le=100, description="% Modal hidroviário")
    exp_vehicle_port: Optional[str] = Field(None, description="Tipo de veículo (porto)")
    exp_port_consumer_dist: Optional[float] = Field(None, ge=0, description="Distância marítima (km)")


class ProjectStep10(BaseModel):
    """Step 10: Volume de Produção"""
    production_volume: float = Field(..., gt=0, description="Volume de produção elegível (t/ano)")


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ProjectStepResponse(BaseModel):
    """Response após salvar um step"""
    id: int
    name: str
    status: str
    current_step: int
    message: str = "Step salvo com sucesso"
    
    class Config:
        from_attributes = True


class ProjectProgressResponse(BaseModel):
    """Response com progresso completo do projeto"""
    id: int
    name: str
    status: str
    current_step: int
    total_steps: int = 10
    progress_percentage: float
    can_calculate: bool  # True se todos steps obrigatórios completos
    
    class Config:
        from_attributes = True
