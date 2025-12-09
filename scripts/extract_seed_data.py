import json
import logging
from pathlib import Path
import sys
import io

# Force UTF-8 for stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def evaluate_formula(val):
    """Simple formula evaluator for cases like =100/365"""
    if not isinstance(val, str) or not val.startswith('='):
        return val
    
    expr = val[1:]
    try:
        # Very limited safety, but needed for extracted data
        # Support basic ops: /, *, +, -, (, )
        allowed = set("0123456789./*-+()")
        if all(c in allowed for c in expr):
            return eval(expr)
    except:
        pass
    return 0.0

def safe_float(val):
    if val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    
    val_str = str(val).strip()
    if val_str.startswith('='):
        evaluated = evaluate_formula(val_str)
        if isinstance(evaluated, (int, float)):
            return float(evaluated)
            
    try:
        return float(val_str.replace(',', '.').replace('E', 'e'))
    except:
        return 0.0

def main():
    json_path = Path("extracted_data/sheet_Dados auxiliares_data.json")
    if not json_path.exists():
        logging.error(f"File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Load data
    cells_by_row_col = {}
    for item in data:
        r = item.get('row')
        c = item.get('col')
        if r and c:
            cells_by_row_col[(r, c)] = item.get('value')

    # Lists to hold extracted data
    biomass_properties = []
    mut_allocations = []
    mut_factors = []
    biomass_prod = []
    industrial_inputs = [] # Electricity, Fuels, Chemicals
    stationary_combustion = [] # Boilers, Furnaces (Scope 1)

    # -------------------------------------------------------------------------
    # 1. BIOMASS PROPERTIES (PCI/Combustion) - Rows ~7-17
    # -------------------------------------------------------------------------
    print("Extracting Biomass Properties...")
    for row in range(7, 20):
        name = cells_by_row_col.get((row, 2))
        pci = safe_float(cells_by_row_col.get((row, 4)))
        combustion_factor = safe_float(cells_by_row_col.get((row, 5)))
        
        if name and isinstance(name, str) and (pci > 0 or combustion_factor > 0):
            if "Total" in name: continue
            biomass_properties.append({
                'biomass_name': name,
                'pci_mj_kg': pci,
                'combustion_emission': combustion_factor
            })

    # -------------------------------------------------------------------------
    # 2. LIFECYCLE EMISSIONS (Inputs, Biomass Prod, Elec, Fuel) - Rows ~24-70
    # -------------------------------------------------------------------------
    print("Extracting Lifecycle Emissions...")
    current_section = None
    
    for row in range(24, 75):
        val_b = cells_by_row_col.get((row, 2))
        val_b_str = str(val_b).lower() if val_b else ""
        
        if "biomassas (produção)" in val_b_str: current_section = "biomass_prod"; continue
        if "biomassas (combustão)" in val_b_str: current_section = "biomass_comb"; continue
        if "eletricidade" in val_b_str and "mix" not in val_b_str: current_section = "electricity"; continue
        if "combustíveis (produção)" in val_b_str: current_section = "fuel_prod"; continue
        if "combustíveis (combustão)" in val_b_str: current_section = "fuel_comb"; continue
        
        if not val_b or val_b in ["Insumo", "Referência"]: continue
        
        factor = safe_float(cells_by_row_col.get((row, 4)))
        unit = str(cells_by_row_col.get((row, 3)))
        
        if current_section == "biomass_prod":
            # Prod Allocation (Col E), Co-Prod Allocation (Col F)
            aloc_prod = safe_float(cells_by_row_col.get((row, 5)))
            aloc_coprod = safe_float(cells_by_row_col.get((row, 6)))
            biomass_type = str(cells_by_row_col.get((row, 8))) # Col H
            
            if aloc_prod > 1.0: aloc_prod /= 100.0
            if aloc_coprod > 1.0: aloc_coprod /= 100.0
            
            biomass_prod.append({
                'biomass_name': val_b,
                'emission_factor': factor,
                'allocation_product': aloc_prod,
                'allocation_coproduct': aloc_coprod,
                'biomass_type': biomass_type
            })
            
        elif current_section in ["electricity", "fuel_prod", "fuel_comb"]:
            itype = "electricity" if current_section == "electricity" else "fuel"
            industrial_inputs.append({
                'input_name': val_b,
                'input_type': itype,
                'emission_factor': factor,
                'unit': unit
            })

    # -------------------------------------------------------------------------
    # 3. MUT ALLOCATION (Special Table) - Rows ~80-92
    # -------------------------------------------------------------------------
    print("Extracting MUT Allocations...")
    for row in range(80, 95):
        b_name = cells_by_row_col.get((row, 2)) # Col B
        stage = cells_by_row_col.get((row, 3)) # Col C
        if not b_name or not stage or b_name == "Biomassa": continue
        
        prod = cells_by_row_col.get((row, 6)) # Col F
        aloc_p = safe_float(cells_by_row_col.get((row, 7))) # Col G
        coprod = cells_by_row_col.get((row, 8)) # Col H
        aloc_co = safe_float(cells_by_row_col.get((row, 9))) # Col I
        
        if aloc_p > 1.0: aloc_p /= 100.0
        if aloc_co > 1.0: aloc_co /= 100.0
        
        mut_allocations.append({
            'biomass_name': b_name,
            'lifecycle_stage': stage,
            'product_name': prod,
            'allocation_product': aloc_p,
            'coproduct_name': coprod,
            'allocation_coproduct': aloc_co
        })

    # -------------------------------------------------------------------------
    # 4. MUT FACTORS - Rows 97-123
    # -------------------------------------------------------------------------
    print("Extracting MUT Factors...")
    states = [
        "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Distrito Federal", 
        "Espírito Santo", "Goiás", "Maranhão", "Mato Grosso", "Mato Grosso do Sul", 
        "Minas Gerais", "Pará", "Paraíba", "Paraná", "Pernambuco", "Piauí", 
        "Rio de Janeiro", "Rio Grande do Norte", "Rio Grande do Sul", "Rondônia", 
        "Roraima", "Santa Catarina", "São Paulo", "Sergipe", "Tocantins"
    ]
    
    for row in range(97, 130):
        state_name = cells_by_row_col.get((row, 2))
        
        if state_name in states:
            pinus_val = safe_float(cells_by_row_col.get((row, 6)))
            euca_val = safe_float(cells_by_row_col.get((row, 10)))
            peanut_val = safe_float(cells_by_row_col.get((row, 14)))
            
            mut_factors.append({'state': state_name, 'culture': 'Pinus', 'emission_factor': pinus_val})
            mut_factors.append({'state': state_name, 'culture': 'Eucalipto', 'emission_factor': euca_val})
            mut_factors.append({'state': state_name, 'culture': 'Amendoim', 'emission_factor': peanut_val})

    # -------------------------------------------------------------------------
    # 5. REMAINING INDUSTRIAL INPUTS - Rows 174+
    # -------------------------------------------------------------------------
    print("Extracting Other Inputs...")
    for row in range(174, 180): # Only until before Combustion table (~180)
        name = cells_by_row_col.get((row, 2))
        unit = str(cells_by_row_col.get((row, 3)))
        factor = safe_float(cells_by_row_col.get((row, 4)))
        
        if not name or name in ["Insumo", "Referência", "Fonte"]: continue
        if isinstance(name, str) and "Fonte:" in name: continue
        
        industrial_inputs.append({
            'input_name': name,
            'input_type': 'other',
            'emission_factor': factor,
            'unit': unit
        })

    # -------------------------------------------------------------------------
    # 6. STATIONARY COMBUSTION EMISSIONS - Rows ~183-202
    # -------------------------------------------------------------------------
    # Data is in g/unit. Need to convert to kg/unit (divide by 1000).
    print("Extracting Stationary Combustion Emissions...")
    for row in range(183, 205):
        fuel = cells_by_row_col.get((row, 2)) # Col B
        if not fuel or "Combustível" in str(fuel): continue
        
        unit = str(cells_by_row_col.get((row, 3)))
        
        # Col D=CO2 Foss, E=CO2 Bio, F=CH4 Foss, G=CH4 Bio, H=N2O, I=CO2 eq
        co2_foss = safe_float(cells_by_row_col.get((row, 4))) / 1000.0
        co2_bio = safe_float(cells_by_row_col.get((row, 5))) / 1000.0
        ch4_foss = safe_float(cells_by_row_col.get((row, 6))) / 1000.0
        ch4_bio = safe_float(cells_by_row_col.get((row, 7))) / 1000.0
        n2o = safe_float(cells_by_row_col.get((row, 8))) / 1000.0
        co2_eq = safe_float(cells_by_row_col.get((row, 9))) / 1000.0
        
        stationary_combustion.append({
            'fuel_name': fuel,
            'unit': unit,
            'co2_fossil': co2_foss,
            'co2_biogenic': co2_bio,
            'ch4_fossil': ch4_foss,
            'ch4_biogenic': ch4_bio,
            'n2o_emission': n2o,
            'co2_eq_emission': co2_eq
        })

    # Write output
    output_path = Path("scripts/data_source.py")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Auto-generated seed data source\n\n")
        
        f.write("# 1. Biomass Properties\n")
        f.write("BIOMASS_PROPERTIES_DATA = [\n")
        for x in biomass_properties: f.write(f"    {x},\n")
        f.write("]\n\n")
        
        f.write("# 2. MUT Allocations\n")
        f.write("BIOMASS_MUT_ALLOCATION_DATA = [\n")
        for x in mut_allocations: f.write(f"    {x},\n")
        f.write("]\n\n")

        f.write("# 3. MUT Factors\n")
        f.write("MUT_FACTORS_DATA = [\n")
        for x in mut_factors: f.write(f"    {x},\n")
        f.write("]\n\n")
        
        f.write("# 4. Biomass Production Emissions\n")
        f.write("BIOMASS_PRODUCTION_DATA = [\n")
        for x in biomass_prod: f.write(f"    {x},\n")
        f.write("]\n\n")
        
        f.write("# 5. Industrial Inputs (Production Scope 3)\n")
        f.write("INDUSTRIAL_INPUTS_DATA = [\n")
        for x in industrial_inputs: f.write(f"    {x},\n")
        f.write("]\n\n")
        
        f.write("# 6. Stationary Combustion (Scope 1)\n")
        f.write("STATIONARY_COMBUSTION_DATA = [\n")
        for x in stationary_combustion: f.write(f"    {x},\n")
        f.write("]\n\n")

    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    main()
