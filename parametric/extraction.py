import pandas as pd
from pathlib import Path

def extract_eso_metrics(eso_file_path):
    if not Path(eso_file_path).exists():
        return {}
    
    try:
        with open(eso_file_path, 'r') as f:
            lines = f.readlines()
        
        var_dict = {}
        data_lines = []
        in_data = False
        
        for line in lines:
            line = line.strip()
            if line == "End of Data Dictionary":
                in_data = True
                continue
            
            if not in_data and line and line[0].isdigit() and ',' in line:
                parts = line.split(',')
                if len(parts) >= 4:
                    var_id = parts[0]
                    var_name = parts[3].split('[')[0].strip()
                    var_dict[var_id] = var_name
            elif in_data and line and ',' in line:
                parts = line.split(',')
                if len(parts) >= 2 and parts[0].isdigit():
                    data_lines.append(parts)
        
        heating_energy = 0
        cooling_energy = 0
        
        for parts in data_lines:
            var_id = parts[0]
            try:
                value = float(parts[1])
            except:
                continue
                
            var_name = var_dict.get(var_id, '').lower()
            
            if 'zone ideal loads supply air total heating energy' in var_name:
                heating_energy += value
            elif 'zone ideal loads supply air sensible cooling energy' in var_name:
                cooling_energy += value
        
        return {
            'annual_heating_load': heating_energy / 3.6e9,
            'annual_sensible_cooling_load': cooling_energy / 3.6e9
        }
        
    except Exception:
        return {}

def extract_all_results(sim_results):
    from .config import STUDY_CASES
    from .utils import get_parameter_group_info
    
    all_results = []
    groups = get_parameter_group_info()
    
    base_eso = Path('Case600_output/eplusout.eso')
    if base_eso.exists():
        base_metrics = extract_eso_metrics(base_eso)
        if base_metrics:
            base_metrics.update({
                'variant': 'base',
                'param_group': 'baseline',
                'param_name': 'Base Case',
                'description': 'Original Case 600 configuration',
                'value': 'default'
            })
            all_results.append(base_metrics)
    
    for result in sim_results:
        if result['status'] == 'success':
            variant = result['variant']
            eso_file = Path(result['output_dir']) / 'eplusout.eso'
            
            if eso_file.exists():
                metrics = extract_eso_metrics(eso_file)
                if metrics:
                    metrics['variant'] = variant
                    
                    # Find parameter info
                    variant_config = STUDY_CASES.get(variant, {})
                    metrics['description'] = variant_config.get('description', '')
                    
                    # Find which parameter group this variant belongs to
                    param_group = param_name = value = ''
                    for group_id, group_info in groups.items():
                        if variant in group_info['variants']:
                            param_group = group_id
                            param_name = group_info['name']
                            variant_idx = group_info['variants'].index(variant)
                            value = group_info['labels'][variant_idx]
                            break
                    
                    metrics['param_group'] = param_group
                    metrics['param_name'] = param_name
                    metrics['value'] = value
                    
                    all_results.append(metrics)
    
    df = pd.DataFrame(all_results)
    if not df.empty:
        # Reorder columns for better readability
        column_order = ['variant', 'param_group', 'param_name', 'value', 'description', 
                       'annual_heating_load', 'annual_sensible_cooling_load']
        df = df[column_order]
        
        csv_file = Path.cwd() / "parametric" / "results" / "results.csv"
        df.to_csv(csv_file, index=False)
        print(f"Extracted {len(df)} results")
        return df
    
    return pd.DataFrame()