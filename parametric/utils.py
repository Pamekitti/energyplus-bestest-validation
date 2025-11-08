def get_parameter_group_info():
    return {
        'timestep': {
            'name': 'Timestep (steps/hour)',
            'variants': ['1a', '1b', '1c', '1d'],
            'labels': ['1 step/hr', '6 steps/hr', '10 steps/hr', '20 steps/hr']
        },
        'shadow_freq': {
            'name': 'Shadow Frequency (days)',
            'variants': ['2a', '2b', '2c'],
            'labels': ['7 days', '20 days', '30 days']
        },
        'shadow_calc': {
            'name': 'Shadow Calculation',
            'variants': ['3a', '4a'],
            'labels': ['PixelCounting', 'Timestep Update']
        },
        'solar_dist': {
            'name': 'Solar Distribution',
            'variants': ['5a', '5b', '5c'],
            'labels': ['MinimalShadowing', 'FullExterior', 'FullExt+Reflections']
        },
        'terrain': {
            'name': 'Terrain Type',
            'variants': ['6a', '6b'],
            'labels': ['Suburbs', 'City']
        },
        'convergence': {
            'name': 'Convergence Tolerances',
            'variants': ['7a', '7b', '8a', '8b'],
            'labels': ['Loads: 0.01W', 'Loads: 0.1W', 'Temp: 0.2C', 'Temp: 0.5C']
        },
        'warmup': {
            'name': 'Warmup Days',
            'variants': ['9a', '9b', '10a', '10b'],
            'labels': ['Max: 15', 'Max: 40', 'Min: 3', 'Min: 10']
        },
        'heat_balance': {
            'name': 'Heat Balance Algorithm',
            'variants': ['11a'],
            'labels': ['ConductionFiniteDiff']
        },
        'inside_conv': {
            'name': 'Inside Convection Algorithm',
            'variants': ['12a', '12b', '12c'],
            'labels': ['Simple', 'CeilingDiffuser', 'Adaptive']
        },
        'outside_conv': {
            'name': 'Outside Convection Algorithm',
            'variants': ['13a', '13b', '13c', '13d'],
            'labels': ['SimpleCombined', 'TARP', 'MoWiTT', 'Adaptive']
        },
    }

def get_base_parameter_value(group_id):
    base_values = {
        'timestep': '4 steps/hr',
        'shadow_freq': '1 day',
        'shadow_calc': 'PolygonClipping, Periodic',
        'solar_dist': 'FullInteriorAndExterior',
        'terrain': 'Country',
        'convergence': 'Default (0.04W, 0.4C)',
        'warmup': 'Max: 30, Min: 6',
        'heat_balance': 'ConductionTransferFunction',
        'inside_conv': 'TARP',
        'outside_conv': 'DOE-2',
        'zone_air': 'ThirdOrderBackwardDiff'
    }
    return base_values.get(group_id, 'Default')