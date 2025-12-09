from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models import BiomassProperty, VehicleEmissionFactor, GWPFactor
from app.schemas.auxiliary import (
    BiomassPropertyResponse,
    VehicleEmissionFactorResponse,
    GWPFactorResponse
)

router = APIRouter(prefix="/auxiliary", tags=["Auxiliary Data"])


@router.get("/biomass-properties", response_model=List[BiomassPropertyResponse])
def get_biomass_properties(db: Session = Depends(get_db)):
    """Get all biomass properties"""
    biomasses = db.query(BiomassProperty).all()
    return biomasses


@router.get("/vehicle-emission-factors", response_model=List[VehicleEmissionFactorResponse])
def get_vehicle_emission_factors(db: Session = Depends(get_db)):
    """Get all vehicle emission factors"""
    vehicles = db.query(VehicleEmissionFactor).all()
    return vehicles


@router.get("/gwp-factors", response_model=List[GWPFactorResponse])
def get_gwp_factors(db: Session = Depends(get_db)):
    """Get all GWP factors"""
    gwp_factors = db.query(GWPFactor).all()
    return gwp_factors
