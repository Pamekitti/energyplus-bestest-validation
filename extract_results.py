#!/usr/bin/env python3

import pandas as pd
import json
from datetime import datetime

def extract_eso_data(eso_file):
    with open(eso_file, 'r') as f:
        lines = f.readlines()
    
    # Parse data dictionary
    variables = {}
    data_start = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line == "End of Data Dictionary":
            data_start = i + 1
            break
        if line and line[0].isdigit() and ',' in line:
            parts = line.split(',')
            if len(parts) >= 4:
                try:
                    key = int(parts[0])
                    zone = parts[2]
                    var = parts[3].split('[')[0].strip()
                    variables[key] = {'zone': zone, 'variable': var}
                except:
                    pass
    
    # Find variables we need
    keywords = [
        'zone mean air temperature',
        'zone ideal loads supply air total heating energy',
        'zone ideal loads supply air sensible cooling energy', 
        'zone ideal loads supply air total heating rate',
        'zone ideal loads supply air sensible cooling rate',
        'surface outside face incident solar radiation rate per area',
        'surface window transmitted solar radiation rate'
    ]
    
    key_vars = {}
    for key, info in variables.items():
        var_lower = info['variable'].lower()
        if any(keyword in var_lower for keyword in keywords):
            key_vars[key] = info
    
    # Parse data
    current_data = {}
    all_data = []
    
    for line in lines[data_start:]:
        line = line.strip()
        if not line or line == "End of Data":
            break
        
        parts = line.split(',')
        if len(parts) >= 2:
            try:
                var_key = int(parts[0])
                value = float(parts[1]) if parts[1].strip() else 0.0
                
                if var_key == 2:  # Time info
                    if current_data:
                        all_data.append(current_data.copy())
                    current_data = {
                        'Month': int(parts[2]) if len(parts) > 2 else 0,
                        'DayOfMonth': int(parts[3]) if len(parts) > 3 else 0,
                        'Hour': int(parts[5]) if len(parts) > 5 else 0,
                        'Minute': float(parts[6]) if len(parts) > 6 else 0.0
                    }
                elif var_key in key_vars:
                    col_name = f"{key_vars[var_key]['zone']}_{key_vars[var_key]['variable']}".replace(" ", "_").replace(":", "_")
                    current_data[col_name] = value
            except:
                continue
    
    if current_data:
        all_data.append(current_data)
    
    return pd.DataFrame(all_data) if all_data else None

def extract_metrics(df, case_name):
    results = {}
    
    # Zone temperature
    zone_temp_col = None
    for col in df.columns:
        if 'MAIN_ZONE' in col and 'Zone_Mean_Air_Temperature' in col:
            zone_temp_col = col
            break
    
    if zone_temp_col:
        results['mean_temp'] = df[zone_temp_col].mean()
        min_idx = df[zone_temp_col].idxmin()
        max_idx = df[zone_temp_col].idxmax()
        results['min_temp'] = df[zone_temp_col].min()
        results['max_temp'] = df[zone_temp_col].max()
        results['min_time'] = df.loc[min_idx, ['Month', 'DayOfMonth', 'Hour']].to_dict()
        results['max_time'] = df.loc[max_idx, ['Month', 'DayOfMonth', 'Hour']].to_dict()
        
        if case_name == 'Case600FF':
            feb_1 = df[(df['Month'] == 2) & (df['DayOfMonth'] == 1)]
            if len(feb_1) > 0:
                hourly = feb_1.groupby('Hour')[zone_temp_col].first()
                if len(hourly) == 24:
                    results['feb_1_temps'] = hourly.tolist()
    
    # Energy loads
    heating_energy = heating_rate = cooling_energy = cooling_rate = None
    for col in df.columns:
        col_lower = col.lower()
        if 'heating' in col_lower and 'energy' in col_lower and 'supply_air' in col_lower:
            heating_energy = col
        elif 'cooling' in col_lower and 'energy' in col_lower and 'supply_air' in col_lower:
            cooling_energy = col
        elif 'heating' in col_lower and 'rate' in col_lower and 'supply_air' in col_lower:
            heating_rate = col
        elif 'cooling' in col_lower and 'rate' in col_lower and 'supply_air' in col_lower:
            cooling_rate = col
    
    if heating_energy:
        results['annual_heating'] = df[heating_energy].sum() / 3.6e9  # J to MWh
    if cooling_energy:
        results['annual_cooling'] = df[cooling_energy].sum() / 3.6e9
    if heating_rate:
        peak_idx = df[heating_rate].idxmax()
        results['peak_heating'] = df[heating_rate].max() / 1000  # W to kW
        results['peak_heating_time'] = df.loc[peak_idx, ['Month', 'DayOfMonth', 'Hour']].to_dict()
    if cooling_rate:
        peak_idx = df[cooling_rate].idxmax()
        results['peak_cooling'] = df[cooling_rate].max() / 1000
        results['peak_cooling_time'] = df.loc[peak_idx, ['Month', 'DayOfMonth', 'Hour']].to_dict()
    
    # Solar radiation (Case600 only)
    if case_name == 'Case600':
        solar_surfaces = {
            'ROOF': 'horizontal',
            'NORTH_WALL': 'north', 
            'EAST_WALL': 'east',
            'SOUTH_WALL': 'south',
            'WEST_WALL': 'west'
        }
        
        for surface, orientation in solar_surfaces.items():
            for col in df.columns:
                if surface in col and 'Incident_Solar_Radiation_Rate_per_Area' in col:
                    results[f'solar_{orientation}'] = df[col].sum() / 1000
                    break
        
        # Transmitted solar
        transmitted_total = 0
        for col in df.columns:
            if 'SOUTH_WINDOW' in col and 'Transmitted_Solar_Radiation_Rate' in col:
                transmitted_total += df[col].sum() / 1000
        if transmitted_total > 0:
            results['transmitted_south'] = transmitted_total / 12.0  # 12 m² total window area
    
    return results

def generate_bestest_json(case600_data, case600ff_data):
    json_data = {
        "metadata": {
            "simulation_tool": "EnergyPlus",
            "version": "25.1.0",
            "date_run": datetime.now().strftime("%Y-%m-%d")
        }
    }
    
    if case600_data:
        transmissivity = None
        if 'solar_south' in case600_data and 'transmitted_south' in case600_data:
            if case600_data['solar_south'] > 0:
                transmissivity = case600_data['transmitted_south'] / case600_data['solar_south']
        
        case_600_data = {
            "annual_heating_load": round(case600_data.get('annual_heating', 0), 3),
            "annual_sensible_cooling_load": round(case600_data.get('annual_cooling', 0), 3),
            "peak_heating_load": round(case600_data.get('peak_heating', 0), 3),
            "peak_sensible_cooling_load": round(case600_data.get('peak_cooling', 0), 3),
            "annual_incident_solar_horizontal": round(case600_data.get('solar_horizontal', 0)),
            "annual_incident_solar_north": round(case600_data.get('solar_north', 0)),
            "annual_incident_solar_east": round(case600_data.get('solar_east', 0)),
            "annual_incident_solar_south": round(case600_data.get('solar_south', 0)),
            "annual_incident_solar_west": round(case600_data.get('solar_west', 0)),
            "annual_transmitted_solar_south": round(case600_data.get('transmitted_south', 0)),
            "transmissivity_coefficient_south": round(transmissivity, 3) if transmissivity else 0
        }
        
        # Add monthly data if available
        if 'monthly_heating_loads' in case600_data:
            case_600_data['monthly_heating_loads'] = case600_data['monthly_heating_loads']
        if 'monthly_cooling_loads' in case600_data:
            case_600_data['monthly_cooling_loads'] = case600_data['monthly_cooling_loads']
        
        json_data["case_600"] = case_600_data
    
    if case600ff_data:
        json_data["case_600FF"] = {
            "free_float_mean_temperature": round(case600ff_data.get('mean_temp', 0), 1),
            "free_float_max_temperature": round(case600ff_data.get('max_temp', 0), 1),
            "free_float_min_temperature": round(case600ff_data.get('min_temp', 0), 1)
        }
    
    with open('results/FORMATTED_RESULTS.json', 'w') as f:
        json.dump(json_data, f, indent=2)

def extract_monthly_data(df, case_name):
    """Extract monthly heating/cooling data"""
    monthly_heating = {}
    monthly_cooling = {}
    
    if case_name != 'Case600':
        return monthly_heating, monthly_cooling
    
    # Find energy columns
    heating_col = cooling_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'heating' in col_lower and 'energy' in col_lower and 'supply_air' in col_lower:
            heating_col = col
        elif 'cooling' in col_lower and 'energy' in col_lower and 'supply_air' in col_lower:
            cooling_col = col
    
    if not heating_col or not cooling_col:
        return monthly_heating, monthly_cooling
    
    month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                   'july', 'august', 'september', 'october', 'november', 'december']
    
    for month_num in range(1, 13):
        month_data = df[df['Month'] == month_num]
        month_name = month_names[month_num - 1]
        
        if len(month_data) > 0:
            heating_total = month_data[heating_col].sum() / 3.6e6  # J to kWh
            cooling_total = month_data[cooling_col].sum() / 3.6e6
            monthly_heating[month_name] = heating_total
            monthly_cooling[month_name] = cooling_total
    
    return monthly_heating, monthly_cooling

def main():
    import os
    
    cases = {
        'Case600': 'Case600_output/eplusout.eso',
        'Case600FF': 'Case600FF_output/eplusout.eso'
    }
    
    os.makedirs('data', exist_ok=True)
    case600_data = case600ff_data = None
    
    for case_name, eso_file in cases.items():
        try:
            df = extract_eso_data(eso_file)
            if df is not None:
                # Save CSV files for bestest_analyze.py
                csv_file = f"results/{case_name}.csv"
                df.to_csv(csv_file, index=False)
                
                metrics = extract_metrics(df, case_name)
                
                # Add monthly data for Case600
                if case_name == 'Case600':
                    monthly_heating, monthly_cooling = extract_monthly_data(df, case_name)
                    metrics['monthly_heating_loads'] = monthly_heating
                    metrics['monthly_cooling_loads'] = monthly_cooling
                
                if case_name == 'Case600':
                    case600_data = metrics
                    print(f"Case 600: {metrics.get('annual_heating', 0):.3f} MWh heating, {metrics.get('annual_cooling', 0):.3f} MWh cooling")
                else:
                    case600ff_data = metrics
                    print(f"Case 600FF: {metrics.get('mean_temp', 0):.1f}°C mean temp")
                
        except FileNotFoundError:
            print(f"File not found: {eso_file}")
        except Exception as e:
            print(f"Error processing {case_name}: {e}")
    
    if case600_data or case600ff_data:
        generate_bestest_json(case600_data, case600ff_data)
        print("Data saved to CSV and JSON files")

if __name__ == "__main__":
    main()