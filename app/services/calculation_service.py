from sqlalchemy.orm import Session
from app.models import (
    Project, 
    BiomassProperty, 
    VehicleEmissionFactor,
    MUTFactor,
    BiomassMUTAllocation,
    BiomassProductionEmission,
    IndustrialInputEmission,
    StationaryCombustionEmission,
    TransportModalFactor
)
from app.core.config import settings
from typing import Dict, Any

class CalculationService:
    """Service for calculating emissions and results"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_project_results(self, project: Project) -> Dict[str, Any]:
        """
        Orchestrates all project calculations
        Returns dictionary with all calculated results
        """
        # Get biomass PCI
        biomass = self.db.query(BiomassProperty).filter(
            BiomassProperty.biomass_name == project.biomass_type
        ).first()
        
        if not biomass:
            raise ValueError(f"Biomass '{project.biomass_type}' not found in database")
        
        # Spreadsheet C37: PCI (kg/MJ/biomass ? No, usually MJ/kg of biomass)
        # We need to know how much BIOMASS is needed per MJ of energy produced/analyzed.
        # If PCI is 18.8 MJ/kg -> 1 kg = 18.8 MJ -> 1 MJ needs 1/18.8 kg = 0.053 kg.
        # Most formulas use "Emissions per MJ" = (Emission per kg / PCI_MJ_per_kg)
        # Let's calculate the conversion factor: kg of biomass per MJ.
        biomass_kg_per_mj = 1.0 / biomass.pci_mj_kg if biomass.pci_mj_kg and biomass.pci_mj_kg > 0 else 0.0
        
        # Calculate emissions by phase
        agr_emissions = self._calculate_agricultural_emissions(project, biomass_kg_per_mj, biomass)
        ind_emissions = self._calculate_industrial_emissions(project, biomass_kg_per_mj)
        trans_emissions = self._calculate_transport_emissions(project, biomass_kg_per_mj)
        
        # Use Phase Emissions (Step 10)
        # C26 in spreadsheet. Usually biogenic CO2 is neutral, but CH4/N2O might exist.
        use_emissions = biomass.combustion_emission if biomass.combustion_emission else 0.0
        
        # Carbon intensity (C21 = SUM(C23:C26))
        carbon_intensity = agr_emissions + ind_emissions + trans_emissions + use_emissions
        
        # Efficiency note (C27 = J20 - C21)
        efficiency_note = settings.FOSSIL_REFERENCE_WEIGHTED - carbon_intensity
        
        # Emission reduction (C29 = (J20 - C21) / J20)
        emission_reduction = (settings.FOSSIL_REFERENCE_WEIGHTED - carbon_intensity) / settings.FOSSIL_REFERENCE_WEIGHTED
        emission_reduction_pct = emission_reduction * 100
        
        # CBIOs (H24)
        cbios = self._calculate_cbios(project, biomass, efficiency_note)
        
        # Revenue
        cbio_price = 78.07  # Reference value
        cbios_revenue = cbios * cbio_price
        
        return {
            "pci": biomass.pci_mj_kg,
            "carbon_intensity": carbon_intensity,
            "agricultural_emissions": agr_emissions,
            "industrial_emissions": ind_emissions,
            "transport_emissions": trans_emissions,
            "use_emissions": use_emissions,
            "efficiency_note": efficiency_note,
            "emission_reduction": emission_reduction_pct,
            "cbios": cbios,
            "cbios_revenue": cbios_revenue
        }
    
    def _calculate_agricultural_emissions(self, project: Project, kg_per_mj: float, biomass: BiomassProperty) -> float:
        """
        Calculates Agricultural Emissions (C23)
        Sum of: Production Impact + MUT Impact + Transport Impact
        """
        production_impact = self._calc_biomass_production_impact(project, kg_per_mj, biomass)
        mut_impact = self._calc_mut_impact(project, kg_per_mj, biomass)
        transport_impact = self._calc_biomass_transport_impact(project, kg_per_mj)
        
        return production_impact + mut_impact + transport_impact
    
    def _calc_biomass_production_impact(self, project: Project, kg_per_mj: float, biomass: BiomassProperty) -> float:
        """
        E40 Calculation
        Uses BiomassProductionEmission factors from DB.
        """
        # Lookup emission factor
        prod_emission = self.db.query(BiomassProductionEmission).filter(
            BiomassProductionEmission.biomass_name == biomass.biomass_name
        ).first()

        factor = prod_emission.emission_factor if prod_emission else 0.0251
        
        # Starch impact (Optional)
        starch_impact = 0.0
        if project.starch_input:
             starch_rec = self.db.query(IndustrialInputEmission).filter(
                 IndustrialInputEmission.input_name.ilike("%Amido%")
             ).first()
             starch_factor = starch_rec.emission_factor if starch_rec else 0.5
             starch_impact = project.starch_input * starch_factor
        
        # Calculation
        # If consumption known, we use it. Otherwise derived from PCI.
        # Standard formula: kg_biomass/MJ * Factor(kgCO2/kg_biomass)
        impact = (kg_per_mj * factor) + starch_impact
        
        return impact

    def _calc_mut_impact(self, project: Project, kg_per_mj: float, biomass: BiomassProperty) -> float:
        """
        E47 Calculation: Land Use Change
        """
        if not project.state: 
            return 0.0

        # Map biomass to culture
        culture = "Pinus" # Default fallback
        b_lower = biomass.biomass_name.lower()
        if "eucali" in b_lower: culture = "Eucalipto"
        elif "amendo" in b_lower: culture = "Amendoim"
        
        mut_rec = self.db.query(MUTFactor).filter(
            MUTFactor.state == project.state,
            MUTFactor.culture == culture
        ).first()
        
        if not mut_rec:
            return 0.0
            
        emission_val = mut_rec.emission_factor
        
        # Allocation check (BiomassMUTAllocation)
        alloc_rec = self.db.query(BiomassMUTAllocation).filter(
            BiomassMUTAllocation.biomass_name == biomass.biomass_name
        ).first()
        
        alloc_percent = alloc_rec.allocation_product if alloc_rec else 1.0
        if alloc_percent > 1.0: alloc_percent /= 100.0
        
        # Formula: kg/MJ * EmissionFactor * Allocation
        return kg_per_mj * emission_val * alloc_percent

    def _calc_biomass_transport_impact(self, project: Project, kg_per_mj: float) -> float:
        if not project.agr_transport_distance or not project.agr_transport_vehicle:
            return 0.0
            
        vehicle = self.db.query(VehicleEmissionFactor).filter(
            VehicleEmissionFactor.vehicle_type == project.agr_transport_vehicle
        ).first()
        
        factor = vehicle.emission_factor if vehicle else 0.062
        
        # distance (km) * (kg_biomass/MJ / 1000 => ton_biomass/MJ) * factor (kgCO2/t.km)
        return project.agr_transport_distance * (kg_per_mj / 1000.0) * factor

    def _calculate_industrial_emissions(self, project: Project, kg_per_mj: float) -> float:
        """
        Industrial Emissions (C24)
        """
        elec = self._calc_electricity_emissions(project, kg_per_mj)
        fuel = self._calc_fuel_emissions(project, kg_per_mj)
        other = self._calc_other_inputs_emissions(project, kg_per_mj)
        
        return elec + fuel + other

    def _calc_electricity_emissions(self, project: Project, kg_per_mj: float) -> float:
        if not project.biomass_processed or project.biomass_processed == 0:
            return 0.0
            
        # Helper to get factor
        def get_factor(name_part):
            rec = self.db.query(IndustrialInputEmission).filter(
                IndustrialInputEmission.input_name.ilike(f"%{name_part}%"),
                IndustrialInputEmission.input_type == "electricity"
            ).first()
            return rec.emission_factor if rec else 0.0

        grid_factor = get_factor("Rede")
        
        total_kwh_emissions = (
            (project.elec_grid or 0) * grid_factor +
            (project.elec_solar or 0) * 0.0 + 
            (project.elec_other or 0) * grid_factor # Fallback
        )
        
        # Normalization: Emissions / Biomass processed (kg) * Biomass required (kg) / MJ
        return total_kwh_emissions * (1.0 / project.biomass_processed) * kg_per_mj

    def _calc_fuel_emissions(self, project: Project, kg_per_mj: float) -> float:
        """
        Calculate Fuel Emissions (Scope 1 Combustion + Scope 3 Production)
        """
        if not project.biomass_processed or project.biomass_processed == 0:
            return 0.0
        
        total_emission = 0.0
        
        # List: (qty, search_term, type)
        fuels = [
            (project.fuel_diesel, "Diesel", "fuel"),
            (project.fuel_gasoline, "Gasolina", "fuel"),
            (project.fuel_ethanol, "Etanol", "fuel"),
            (project.fuel_biodiesel, "Biodiesel", "fuel"),
            (project.fuel_gnv, "Gás Natural", "fuel"),
            (project.fuel_lpg, "GLP", "fuel"),
            (project.fuel_biomass, "Lenha", "fuel"),
            (project.fuel_other, "Óleo combustível", "fuel")
        ]
        
        for qty, name_search, ftype in fuels:
            if qty and qty > 0:
                # 1. Production Emission (Scope 3)
                prod_rec = self.db.query(IndustrialInputEmission).filter(
                    IndustrialInputEmission.input_name.ilike(f"%{name_search}%"),
                    IndustrialInputEmission.input_type == ftype
                ).first()
                prod_factor = prod_rec.emission_factor if prod_rec else 0.0
                
                # 2. Combustion Emission (Scope 1)
                comb_rec = self.db.query(StationaryCombustionEmission).filter(
                    StationaryCombustionEmission.fuel_name.ilike(f"%{name_search}%")
                ).first()
                
                comb_factor = comb_rec.co2_eq_emission if comb_rec else 0.0
                
                total_factor = prod_factor + comb_factor
                total_emission += qty * total_factor

        return total_emission * (1.0 / project.biomass_processed) * kg_per_mj

    def _calc_other_inputs_emissions(self, project: Project, kg_per_mj: float) -> float:
        if not project.biomass_processed or project.biomass_processed == 0:
            return 0.0
            
        total = 0.0
        if project.water_consumption:
            w_rec = self.db.query(IndustrialInputEmission).filter(IndustrialInputEmission.input_type=="water").first()
            w_factor = w_rec.emission_factor if w_rec else 0.196
            total += project.water_consumption * w_factor
            
        if project.input_lubricant:
             l_rec = self.db.query(IndustrialInputEmission).filter(IndustrialInputEmission.input_name.ilike("%lubrificante%")).first()
             total += project.input_lubricant * (l_rec.emission_factor if l_rec else 3.5)
             
        if project.input_chemical:
             c_rec = self.db.query(IndustrialInputEmission).filter(IndustrialInputEmission.input_name.ilike("%Genérico%")).first()
             total += project.input_chemical * (c_rec.emission_factor if c_rec else 2.0)
             
        return total * (1.0 / project.biomass_processed) * kg_per_mj
        
    def _calculate_transport_emissions(self, project: Project, kg_per_mj: float) -> float:
        """
        C25 = Sum of Domestic and Export transport
        """
        domestic = self._calc_domestic_transport(project, kg_per_mj)
        export = 0.0 # Placeholder
        return domestic + export

    def _calc_domestic_transport(self, project: Project, kg_per_mj: float) -> float:
        if not project.dom_mass or not project.dom_distance:
            return 0.0
            
        # Modal lookup needs to be precise based on user input
        # Assuming truck for now or using TransportModalFactor if we had a field for mode
        # Using simplified factor for now or looking up standard
        
        modal = self.db.query(TransportModalFactor).filter(TransportModalFactor.modal_type == "road").first()
        factor = modal.emission_factor if modal else 0.062
        
        # Emissions = mass(t) * dist(km) * factor
        # Normalized per MJ
        # Note: logic depends on if dom_mass is TOTAL mass transported or per unit
        # Assuming total project mass logic like others
        
        total_emission = (project.dom_mass * project.dom_distance * factor)
        
        if project.biomass_processed and project.biomass_processed > 0:
             return total_emission * (1.0 / project.biomass_processed) * kg_per_mj
        return 0.0

    def _calculate_cbios(self, project: Project, biomass: BiomassProperty, efficiency_note: float) -> float:
        if not project.production_volume:
            return 0.0
            
        # Project.production_volume is in TONS/Year (Mass)
        # We need Total Energy in MJ.
        # Use Product PCI in MJ/kg.
        # Example: Ethanol Anhydrous approx 28.26 MJ/kg (Source: ANP 894/2022 from Screenshot)
        # We should ideally lookup this value based on product type, but assuming Ethanol for now.
        product_pci_mj_kg = 28.26 
        
        # Tons -> kg
        total_mass_kg = project.production_volume * 1000.0
        total_energy_mj = total_mass_kg * product_pci_mj_kg
        
        # CBIO = (Energy(MJ) * EfficiencyNote(gCO2/MJ)) / 1,000,000 (g->t) ??
        # EfficiencyNote is in gCO2eq/MJ (or kg? Usually C27 is C20-C21. C21 is gCO2eq/MJ).
        # Wait, if data is kgCO2eq/MJ (as per my calc service returning carbon_intensity), 
        # then EfficiencyNote is kgCO2/MJ.
        # CBIO = (MJ * kgCO2/MJ) / 1000 = tCO2 avoided.
        
        # Re-verify units of carbon_intensity.
        # My formulas return kgCO2eq/MJ ( because factors are kgCO2/unit or g/unit/1000 ).
        # Settings.FOSSIL_REFERENCE is likely gCO2eq/MJ (e.g. 73.8).
        # Need to ensure units match.
        # If FOSSIL_REFERENCE is 87.4 gCO2/MJ (Gasoline A) -> 0.0874 kg/MJ.
        # If my calculations return kg/MJ (e.g. 0.02), then efficiency_note is kg/MJ.
        # Total avoided = Energy(MJ) * Avoided(kg/MJ) = Avoided kg.
        # CBIO = Avoided Ton = Avoided kg / 1000.
        
        return (total_energy_mj * efficiency_note) / 1000.0
