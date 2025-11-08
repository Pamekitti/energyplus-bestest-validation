import subprocess
import concurrent.futures
from pathlib import Path
import shutil

from .config import STUDY_CASES, CONFIG

def create_variant_idf(base_content, variant_id, variant_config):
    variant_content = base_content
    
    for object_type, mod_config in variant_config['modifications'].items():
        fields = mod_config['fields']
        values = mod_config['values']
        
        if object_type == 'TIMESTEP':
            variant_content = variant_content.replace('Timestep,4;', f'Timestep,{values[0]};')
        
        elif object_type == 'SHADOWCALCULATION':
            lines = variant_content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('ShadowCalculation,'):
                    shadow_lines = []
                    for j in range(0, 10):
                        shadow_lines.append(lines[i+j])
                        if lines[i+j].strip().endswith(';'):
                            break
                    
                    if fields[0] == 0:
                        shadow_lines[1] = f'    {values[0]},          !- Shading Calculation Method'
                    elif fields[0] == 1:
                        shadow_lines[2] = f'    {values[0]},          !- Shading Calculation Update Frequency Method'
                    elif fields[0] == 2:
                        shadow_lines[3] = f'    {values[0]},          !- Shading Calculation Update Frequency'
                    
                    for k, new_line in enumerate(shadow_lines):
                        lines[i+k] = new_line
                    variant_content = '\n'.join(lines)
                    break
        
        elif object_type == 'BUILDING':
            lines = variant_content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith('Building,'):
                    for j in range(1, 15):
                        if lines[i+j].strip().endswith(';'):
                            building_lines = lines[i:i+j+1]
                            break
                    
                    if fields[0] == 2:
                        building_lines[3] = f'    {values[0]},          !- Terrain'
                    elif fields[0] == 3:
                        building_lines[4] = f'    {values[0]},          !- Loads Convergence Tolerance Value'
                    elif fields[0] == 4:
                        building_lines[5] = f'    {values[0]},          !- Temperature Convergence Tolerance Value'
                    elif fields[0] == 5:
                        building_lines[6] = f'    {values[0]},    !- Solar Distribution'
                    elif fields[0] == 6:
                        building_lines[7] = f'    {values[0]},          !- Maximum Number of Warmup Days'
                    elif fields[0] == 7:
                        building_lines[8] = f'    {values[0]};          !- Minimum Number of Warmup Days'
                    
                    lines[i:i+j+1] = building_lines
                    variant_content = '\n'.join(lines)
                    break
        
        elif object_type == 'HEATBALANCEALGORITHM':
            variant_content = variant_content.replace(
                'HeatBalanceAlgorithm,\n    ConductionTransferFunction,',
                f'HeatBalanceAlgorithm,\n    {values[0]},'
            )
        
        elif object_type == 'SURFACECONVECTIONALGORITHM:INSIDE':
            variant_content = variant_content.replace(
                'SurfaceConvectionAlgorithm:Inside,TARP;',
                f'SurfaceConvectionAlgorithm:Inside,{values[0]};'
            )
        
        elif object_type == 'SURFACECONVECTIONALGORITHM:OUTSIDE':
            variant_content = variant_content.replace(
                'SurfaceConvectionAlgorithm:Outside,DOE-2;',
                f'SurfaceConvectionAlgorithm:Outside,{values[0]};'
            )
        
    
    return variant_content

def run_single_simulation(variant_id, variant_config, base_content):
    try:
        parametric_dir = Path.cwd() / "parametric"
        variant_dir = parametric_dir / "idf_variants" / f"Case600_{variant_id}"
        variant_dir.mkdir(exist_ok=True, parents=True)
        variant_file = variant_dir / f"Case600_{variant_id}.idf"
        
        variant_content = create_variant_idf(base_content, variant_id, variant_config)
        with open(variant_file, 'w') as f:
            f.write(variant_content)
        
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
            
    except Exception as e:
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
    
    with open(base_idf_path, 'r') as f:
        base_content = f.read()
    
    print(f"Running {len(STUDY_CASES)} simulations...")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONFIG['max_parallel']) as executor:
        future_to_variant = {
            executor.submit(run_single_simulation, variant_id, config, base_content): variant_id 
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