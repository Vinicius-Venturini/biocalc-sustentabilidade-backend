import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
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

def check_table(db, model, name):
    try:
        count = db.query(model).count()
        print(f"{name}: {count} records")
        return count
    except Exception as e:
        print(f"{name}: Error ({str(e)})")
        return 0

def main():
    db = SessionLocal()
    print("--- Database Verification Report ---")
    try:
        check_table(db, BiomassProperty, "Biomass Properties")
        check_table(db, GWPFactor, "GWP Factors")
        check_table(db, VehicleEmissionFactor, "Vehicle Factors")
        check_table(db, TransportModalFactor, "Transport Modals")
        check_table(db, MUTFactor, "MUT Factors")
        check_table(db, IndustrialInputEmission, "Industrial Inputs")
        check_table(db, BiomassProductionEmission, "Biomass Production Emissions")
        check_table(db, BiomassMUTAllocation, "Biomass MUT Allocations")
        check_table(db, StationaryCombustionEmission, "Stationary Combustion Emissions")
        print("------------------------------------")
    except Exception as e:
        print(f"Error checking database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
