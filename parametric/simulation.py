import subprocess
import concurrent.futures
from pathlib import Path
import shutil
from eppy.modeleditor import IDF

from .config import STUDY_CASES, CONFIG

# Set EnergyPlus IDD file
IDF.setiddname("/Applications/EnergyPlus-25-1-0/Energy+.idd")

def create_variant_idf(base_idf_path, variant_id, variant_config):
    # Load IDF using eppy
    idf = IDF(str(base_idf_path))
    
    for object_type, mod_config in variant_config['modifications'].items():
        fields = mod_config['fields']
        values = mod_config['values']
        
        if object_type == 'TIMESTEP':
            timesteps = idf.idfobjects['TIMESTEP']
            if timesteps:
                timesteps[0].Number_of_Timesteps_per_Hour = values[0]
        
        elif object_type == 'SHADOWCALCULATION':
            shadows = idf.idfobjects['SHADOWCALCULATION']
            if shadows:
                shadow = shadows[0]
                if fields[0] == 0:  # method
                    shadow.Shading_Calculation_Method = values[0]
                elif fields[0] == 1:  # frequency method
                    shadow.Shading_Calculation_Update_Frequency_Method = values[0]
                elif fields[0] == 2:  # frequency
                    shadow.Shading_Calculation_Update_Frequency = values[0]
        
        elif object_type == 'BUILDING':
            buildings = idf.idfobjects['BUILDING']
            if buildings:
                building = buildings[0]
                for idx, field_idx in enumerate(fields):
                    if field_idx == 2:  # Terrain
                        building.Terrain = values[idx]
                    elif field_idx == 3:  # Loads tolerance
                        building.Loads_Convergence_Tolerance_Value = values[idx]
                    elif field_idx == 4:  # Temperature tolerance
                        building.Temperature_Convergence_Tolerance_Value = values[idx]
                    elif field_idx == 5:  # Solar Distribution
                        building.Solar_Distribution = values[idx]
                    elif field_idx == 6:  # Max warmup days
                        building.Maximum_Number_of_Warmup_Days = values[idx]
                    elif field_idx == 7:  # Min warmup days
                        building.Minimum_Number_of_Warmup_Days = values[idx]
        
        elif object_type == 'HEATBALANCEALGORITHM':
            algorithms = idf.idfobjects['HEATBALANCEALGORITHM']
            if algorithms:
                algorithms[0].Algorithm = values[0]
        
        elif object_type == 'SURFACECONVECTIONALGORITHM:INSIDE':
            inside_algs = idf.idfobjects['SURFACECONVECTIONALGORITHM:INSIDE']
            if inside_algs:
                inside_algs[0].Algorithm = values[0]
        
        elif object_type == 'SURFACECONVECTIONALGORITHM:OUTSIDE':
            outside_algs = idf.idfobjects['SURFACECONVECTIONALGORITHM:OUTSIDE']
            if outside_algs:
                outside_algs[0].Algorithm = values[0]
    
    return idf

def run_single_simulation(variant_id, variant_config, base_idf_path):
    try:
        parametric_dir = Path.cwd() / "parametric"
        variant_dir = parametric_dir / "idf_variants" / f"Case600_{variant_id}"
        variant_dir.mkdir(exist_ok=True, parents=True)
        variant_file = variant_dir / f"Case600_{variant_id}.idf"
        
        variant_idf = create_variant_idf(base_idf_path, variant_id, variant_config)
        variant_idf.save(str(variant_file))
        
        output_dir = parametric_dir / "outputs" / f"Case600_{variant_id}"
        output_dir.mkdir(exist_ok=True, parents=True)
        
        cmd = [
            CONFIG['energyplus_exe'],
            '-w', CONFIG['weather_file'],
            '-d', str(output_dir),
            str(variant_file)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            return {'variant': variant_id, 'status': 'success', 'output_dir': str(output_dir)}
        else:
            return {'variant': variant_id, 'status': 'failed'}
            
    except Exception:
        return {'variant': variant_id, 'status': 'failed'}

def run_simulations():
    base_dir = Path.cwd()
    parametric_dir = base_dir / "parametric"
    
    parametric_dir.mkdir(exist_ok=True)
    (parametric_dir / "idf_variants").mkdir(exist_ok=True)
    (parametric_dir / "outputs").mkdir(exist_ok=True)
    (parametric_dir / "results").mkdir(exist_ok=True)
    
    base_idf_path = base_dir / CONFIG['base_case']
    if not base_idf_path.exists():
        print(f"Error: Base IDF not found at {base_idf_path}")
        return []
    
    print(f"Running {len(STUDY_CASES)} simulations...")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG['max_parallel']) as executor:
        future_to_variant = {
            executor.submit(run_single_simulation, variant_id, config, base_idf_path): variant_id 
            for variant_id, config in STUDY_CASES.items()
        }
        
        for future in concurrent.futures.as_completed(future_to_variant):
            result = future.result()
            results.append(result)
            status = "✓" if result['status'] == 'success' else "✗"
            print(f"{status} {result['variant']}")
    
    successful = len([r for r in results if r['status'] == 'success'])
    print(f"Completed {successful}/{len(results)} simulations")
    
    return results