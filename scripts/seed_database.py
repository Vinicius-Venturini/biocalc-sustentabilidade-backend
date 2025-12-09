"""
Script para popular o banco de dados com dados auxiliares da planilha BioCalc
Baseado nos dados extraídos de extracted_data/
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models import (
    BiomassProperty,
    VehicleEmissionFactor,
    GWPFactor,
    BiomassProductionEmission,
    TransportModalFactor,
    IndustrialInputEmission,
    MUTFactor,
    BiomassMUTAllocation,
    StationaryCombustionEmission
)

# Import extracted data
try:
    from scripts.data_source import (
        MUT_FACTORS_DATA,
        BIOMASS_PRODUCTION_DATA,
        INDUSTRIAL_INPUTS_DATA,
        BIOMASS_PROPERTIES_DATA,
        BIOMASS_MUT_ALLOCATION_DATA,
        STATIONARY_COMBUSTION_DATA
    )
except ImportError:
    # Fallback/Debug setup if running from different context
    import sys
    sys.path.append(str(Path(__file__).parent))
    from data_source import (
        MUT_FACTORS_DATA,
        BIOMASS_PRODUCTION_DATA,
        INDUSTRIAL_INPUTS_DATA,
        BIOMASS_PROPERTIES_DATA,
        BIOMASS_MUT_ALLOCATION_DATA,
        STATIONARY_COMBUSTION_DATA
    )


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")


def seed_biomass_properties(db: Session):
    """Seed biomass properties table from EXTRACTED DATA"""
    print("\nSeeding biomass properties (from extracted data)...")
    
    count = 0
    for prop_data in BIOMASS_PROPERTIES_DATA:
        existing = db.query(BiomassProperty).filter(BiomassProperty.biomass_name == prop_data["biomass_name"]).first()
        if not existing:
            prop = BiomassProperty(**prop_data)
            db.add(prop)
            count += 1
        else:
            existing.pci_mj_kg = prop_data["pci_mj_kg"]
            existing.combustion_emission = prop_data["combustion_emission"]
    
    db.commit()
    print(f"✓ Processed {len(BIOMASS_PROPERTIES_DATA)} biomass properties (Added: {count})")
    
def seed_biomass_mut_allocations(db: Session):
    """Seed MUT Allocations from EXTRACTED DATA"""
    print("\nSeeding Biomass MUT Allocations...")
    
    count = 0
    for alloc_data in BIOMASS_MUT_ALLOCATION_DATA:
        # Check uniqueness by Biomass + Stage
        existing = db.query(BiomassMUTAllocation).filter(
            BiomassMUTAllocation.biomass_name == alloc_data["biomass_name"],
            BiomassMUTAllocation.lifecycle_stage == alloc_data["lifecycle_stage"]
        ).first()
        
        if not existing:
            alloc = BiomassMUTAllocation(**alloc_data)
            db.add(alloc)
            count += 1
        else:
            existing.allocation_product = alloc_data["allocation_product"]
            existing.allocation_coproduct = alloc_data["allocation_coproduct"]
            
    db.commit()
    print(f"✓ Processed {len(BIOMASS_MUT_ALLOCATION_DATA)} MUT Allocations (Added: {count})")

def seed_stationary_combustion_emissions(db: Session):
    """Seed Stationary Combustion emissions from EXTRACTED DATA"""
    print("\nSeeding Stationary Combustion emissions...")
    
    count = 0
    for item in STATIONARY_COMBUSTION_DATA:
        existing = db.query(StationaryCombustionEmission).filter(
            StationaryCombustionEmission.fuel_name == item["fuel_name"]
        ).first()
        
        if not existing:
            rec = StationaryCombustionEmission(**item)
            db.add(rec)
            count += 1
        else:
            # Update
            existing.co2_eq_emission = item["co2_eq_emission"]
            existing.co2_fossil = item["co2_fossil"]
            existing.co2_biogenic = item["co2_biogenic"]
            
    db.commit()
    print(f"✓ Processed {len(STATIONARY_COMBUSTION_DATA)} stationary combustion factors (Added: {count})")



def seed_gwp_factors(db: Session):
    """Seed GWP factors table"""
    print("\nSeeding GWP factors...")
    
    gwp_factors = [
        {
            "gas_name": "CO2 - Dióxido de Carbono Fóssil",
            "gwp_value": 1.0
        },
        {
            "gas_name": "CH4 - Metano Fóssil",
            "gwp_value": 29.8
        },
        {
            "gas_name": "CH4 - Metano Biogênico",
            "gwp_value": 27.2
        },
        {
            "gas_name": "N2O - Óxido Nitroso",
            "gwp_value": 273.0
        }
    ]
    
    for gwp_data in gwp_factors:
        existing = db.query(GWPFactor).filter(GWPFactor.gas_name == gwp_data["gas_name"]).first()
        if not existing:
            gwp = GWPFactor(**gwp_data)
            db.add(gwp)
    
    db.commit()
    print(f"✓ Processed {len(gwp_factors)} GWP factors")


def seed_vehicle_emission_factors(db: Session):
    """Seed vehicle emission factors table"""
    print("\nSeeding vehicle emission factors...")
    
    vehicles = [
        {
            "vehicle_type": "Caminhão Toco/Semipesado (16-32t)",
            "emission_factor": 0.062
        },
        {
            "vehicle_type": "Carreta/Pesado (>32t)",
            "emission_factor": 0.062
        },
        {
            "vehicle_type": "VUC (Urbano)",
            "emission_factor": 0.089
        },
        {
            "vehicle_type": "Trem (Ferroviário Padrão)",
            "emission_factor": 0.022
        }
    ]
    
    for vehicle_data in vehicles:
        existing = db.query(VehicleEmissionFactor).filter(VehicleEmissionFactor.vehicle_type == vehicle_data["vehicle_type"]).first()
        if not existing:
            vehicle = VehicleEmissionFactor(**vehicle_data)
            db.add(vehicle)
    
    db.commit()
    print(f"✓ Processed {len(vehicles)} vehicle emission factors")


def seed_transport_modal_factors(db: Session):
    """Seed transport modal factors table"""
    print("\nSeeding transport modal factors...")
    
    modals = [
        {
            "modal_type": "road",
            "emission_factor": 0.062
        },
        {
            "modal_type": "rail",
            "emission_factor": 0.022
        },
        {
            "modal_type": "water",
            "emission_factor": 0.015
        },
        {
            "modal_type": "maritime",
            "emission_factor": 0.0053
        }
    ]
    
    for modal_data in modals:
        existing = db.query(TransportModalFactor).filter(TransportModalFactor.modal_type == modal_data["modal_type"]).first()
        if not existing:
            modal = TransportModalFactor(**modal_data)
            db.add(modal)
    
    db.commit()
    print(f"✓ Processed {len(modals)} transport modal factors")


def seed_industrial_input_emissions(db: Session):
    """Seed industrial input emission factors from EXTRACTED DATA"""
    print("\nSeeding industrial input emissions (from extracted data)...")
    
    count = 0
    for input_data in INDUSTRIAL_INPUTS_DATA:
        # Check uniqueness by input_name
        existing = db.query(IndustrialInputEmission).filter(IndustrialInputEmission.input_name == input_data["input_name"]).first()
        if not existing:
            inp = IndustrialInputEmission(**input_data)
            db.add(inp)
            count += 1
        else:
            # Optional: Update existing
            existing.emission_factor = input_data["emission_factor"]
            existing.unit = input_data["unit"]
            existing.input_type = input_data["input_type"]
    
    db.commit()
    print(f"✓ Processed {len(INDUSTRIAL_INPUTS_DATA)} industrial inputs (Added: {count})")


def seed_biomass_production_emissions(db: Session):
    """Seed biomass production emission factors from EXTRACTED DATA"""
    print("\nSeeding biomass production emissions (from extracted data)...")
    
    count = 0
    for emission_data in BIOMASS_PRODUCTION_DATA:
        existing = db.query(BiomassProductionEmission).filter(BiomassProductionEmission.biomass_name == emission_data["biomass_name"]).first()
        if not existing:
            emission = BiomassProductionEmission(**emission_data)
            db.add(emission)
            count += 1
        else:
            existing.emission_factor = emission_data["emission_factor"]
            existing.allocation_product = emission_data.get("allocation_product", 0.0)
            existing.allocation_coproduct = emission_data.get("allocation_coproduct", 1.0)
            existing.biomass_type = emission_data.get("biomass_type", "")
    
    db.commit()
    print(f"✓ Processed {len(BIOMASS_PRODUCTION_DATA)} biomass production emissions (Added: {count})")


def seed_mut_factors(db: Session):
    """Seed MUT factors from EXTRACTED DATA"""
    print("\nSeeding MUT factors (from extracted data)...")
    
    count = 0
    for mut_data in MUT_FACTORS_DATA:
        # Check uniqueness by State + Culture
        existing = db.query(MUTFactor).filter(
            MUTFactor.state == mut_data["state"],
            MUTFactor.culture == mut_data["culture"]
        ).first()
        
        if not existing:
            mut = MUTFactor(**mut_data)
            db.add(mut)
            count += 1
        else:
            existing.emission_factor = mut_data["emission_factor"]
    
    db.commit()
    print(f"✓ Processed {len(MUT_FACTORS_DATA)} MUT factors (Added: {count})")


def main():
    """Main seeding function"""
    print("=" * 80)
    print("BIOCALC DATABASE SEEDING v2")
    print("=" * 80)
    
    # Create tables
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed all tables
        seed_biomass_properties(db)
        seed_gwp_factors(db)
        seed_vehicle_emission_factors(db)
        seed_transport_modal_factors(db)
        
        # New/Updated from Extraction
        seed_industrial_input_emissions(db)
        seed_biomass_production_emissions(db)
        seed_mut_factors(db)
        seed_biomass_mut_allocations(db)
        seed_stationary_combustion_emissions(db)
        
        print("\n" + "=" * 80)
        print("✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Seeding failed: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
