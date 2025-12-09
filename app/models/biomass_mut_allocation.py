from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class BiomassMUTAllocation(Base):
    """
    Allocation rules specifically for Land Use Change (MUT) calculations.
    Distinct from IndustrialInputEmission allocations.
    Source: 'Dados auxiliares' sheet, blue table (~Row 80)
    """
    __tablename__ = "biomass_mut_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    biomass_name = Column(String, index=True, nullable=False) # e.g. "Resíduo de Pinus"
    lifecycle_stage = Column(String) # e.g. "Resíduos de galhos e folhas", "Resíduos de Casca"
    product_name = Column(String) # e.g. "Tora de madeira"
    allocation_product = Column(Float, default=0.0) # % (0-100 or 0-1)
    coproduct_name = Column(String) # e.g. "Resíduos de galhos e folhas"
    allocation_coproduct = Column(Float, default=0.0) # %
