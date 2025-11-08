import pandas as pd
from pathlib import Path

from .plotting import create_academic_plots
from .utils import get_parameter_group_info

def analyze_results(df):
    plots_dir = Path.cwd() / "parametric" / "results"
    plots_dir.mkdir(exist_ok=True)
    
    if df.empty:
        print("No data to analyze")
        return False
    
    print(f"Analyzing {len(df)} results...")
    
    create_academic_plots(df, plots_dir)
    
    base_mask = df['variant'] == 'base'
    if base_mask.any():
        base_row = df[base_mask].iloc[0]
        
        with open(plots_dir / "results.txt", 'w') as f:
            f.write("Parametric Analysis Results\n\n")
            f.write(f"Base case: {base_row['annual_heating_load']:.3f} MWh heating, {base_row['annual_sensible_cooling_load']:.3f} MWh cooling\n\n")
            
            # Write all results grouped by parameter
            groups = get_parameter_group_info()
            for group_id, group_info in groups.items():
                group_variants = [v for v in group_info['variants'] if v in df['variant'].values]
                if group_variants:
                    f.write(f"{group_info['name']}:\n")
                    for i, variant in enumerate(group_variants):
                        variant_data = df[df['variant'] == variant]
                        if not variant_data.empty:
                            heating = variant_data['annual_heating_load'].iloc[0]
                            cooling = variant_data['annual_sensible_cooling_load'].iloc[0]
                            h_diff = ((heating - base_row['annual_heating_load']) / base_row['annual_heating_load']) * 100
                            c_diff = ((cooling - base_row['annual_sensible_cooling_load']) / base_row['annual_sensible_cooling_load']) * 100
                            label = group_info['labels'][i]
                            f.write(f"  {label}: {heating:.3f} MWh ({h_diff:+.1f}%) / {cooling:.3f} MWh ({c_diff:+.1f}%)\n")
                    f.write("\n")
            
            # Summary table
            f.write("Impact summary (max change in each parameter group):\n")
            for group_id, group_info in groups.items():
                group_variants = [v for v in group_info['variants'] if v in df['variant'].values]
                max_h = max_c = 0
                for variant in group_variants:
                    variant_data = df[df['variant'] == variant]
                    if not variant_data.empty:
                        h_diff = abs(((variant_data['annual_heating_load'].iloc[0] - base_row['annual_heating_load']) / base_row['annual_heating_load']) * 100)
                        c_diff = abs(((variant_data['annual_sensible_cooling_load'].iloc[0] - base_row['annual_sensible_cooling_load']) / base_row['annual_sensible_cooling_load']) * 100)
                        max_h = max(max_h, h_diff)
                        max_c = max(max_c, c_diff)
                
                f.write(f"  {group_info['name']}: {max_h:.1f}% heating, {max_c:.1f}% cooling\n")
    
    print("Analysis complete")
    return True