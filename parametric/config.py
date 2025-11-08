STUDY_CASES = {
    '1a': {'description': 'Timestep: 1 step/hour', 'modifications': {'TIMESTEP': {'fields': [0], 'values': [1]}}},
    '1b': {'description': 'Timestep: 6 steps/hour', 'modifications': {'TIMESTEP': {'fields': [0], 'values': [6]}}},
    '1c': {'description': 'Timestep: 10 steps/hour', 'modifications': {'TIMESTEP': {'fields': [0], 'values': [10]}}},
    '1d': {'description': 'Timestep: 20 steps/hour', 'modifications': {'TIMESTEP': {'fields': [0], 'values': [20]}}},
    
    '2a': {'description': 'Shadow calc frequency: 7 days', 'modifications': {'SHADOWCALCULATION': {'fields': [2], 'values': [7]}}},
    '2b': {'description': 'Shadow calc frequency: 20 days', 'modifications': {'SHADOWCALCULATION': {'fields': [2], 'values': [20]}}},
    '2c': {'description': 'Shadow calc frequency: 30 days', 'modifications': {'SHADOWCALCULATION': {'fields': [2], 'values': [30]}}},
    
    '3a': {'description': 'Shadow method: PixelCounting', 'modifications': {'SHADOWCALCULATION': {'fields': [0], 'values': ['PixelCounting']}}},
    
    '4a': {'description': 'Shadow update: Timestep', 'modifications': {'SHADOWCALCULATION': {'fields': [1], 'values': ['Timestep']}}},
    
    '5a': {'description': 'Solar: MinimalShadowing', 'modifications': {'BUILDING': {'fields': [5], 'values': ['MinimalShadowing']}}},
    '5b': {'description': 'Solar: FullExterior', 'modifications': {'BUILDING': {'fields': [5], 'values': ['FullExterior']}}},
    '5c': {'description': 'Solar: FullExtWithReflections', 'modifications': {'BUILDING': {'fields': [5], 'values': ['FullExteriorWithReflections']}}},
    
    '6a': {'description': 'Terrain: Suburbs', 'modifications': {'BUILDING': {'fields': [2], 'values': ['Suburbs']}}},
    '6b': {'description': 'Terrain: City', 'modifications': {'BUILDING': {'fields': [2], 'values': ['City']}}},
    
    '7a': {'description': 'Loads tolerance: 0.01W', 'modifications': {'BUILDING': {'fields': [3], 'values': [0.01]}}},
    '7b': {'description': 'Loads tolerance: 0.1W', 'modifications': {'BUILDING': {'fields': [3], 'values': [0.1]}}},
    
    '8a': {'description': 'Temp tolerance: 0.2C', 'modifications': {'BUILDING': {'fields': [4], 'values': [0.2]}}},
    '8b': {'description': 'Temp tolerance: 0.5C', 'modifications': {'BUILDING': {'fields': [4], 'values': [0.5]}}},
    
    '9a': {'description': 'Max warmup: 15 days', 'modifications': {'BUILDING': {'fields': [6], 'values': [15]}}},
    '9b': {'description': 'Max warmup: 40 days', 'modifications': {'BUILDING': {'fields': [6], 'values': [40]}}},
    
    '10a': {'description': 'Min warmup: 3 days', 'modifications': {'BUILDING': {'fields': [7], 'values': [3]}}},
    '10b': {'description': 'Min warmup: 10 days', 'modifications': {'BUILDING': {'fields': [7], 'values': [10]}}},
    
    '11a': {'description': 'Heat balance: ConductionFiniteDifference', 'modifications': {'HEATBALANCEALGORITHM': {'fields': [0], 'values': ['ConductionFiniteDifference']}}},
    
    '12a': {'description': 'Inside convection: Simple', 'modifications': {'SURFACECONVECTIONALGORITHM:INSIDE': {'fields': [0], 'values': ['Simple']}}},
    '12b': {'description': 'Inside convection: CeilingDiffuser', 'modifications': {'SURFACECONVECTIONALGORITHM:INSIDE': {'fields': [0], 'values': ['CeilingDiffuser']}}},
    '12c': {'description': 'Inside convection: AdaptiveConvectionAlgorithm', 'modifications': {'SURFACECONVECTIONALGORITHM:INSIDE': {'fields': [0], 'values': ['AdaptiveConvectionAlgorithm']}}},
    
    '13a': {'description': 'Outside convection: SimpleCombined', 'modifications': {'SURFACECONVECTIONALGORITHM:OUTSIDE': {'fields': [0], 'values': ['SimpleCombined']}}},
    '13b': {'description': 'Outside convection: TARP', 'modifications': {'SURFACECONVECTIONALGORITHM:OUTSIDE': {'fields': [0], 'values': ['TARP']}}},
    '13c': {'description': 'Outside convection: MoWiTT', 'modifications': {'SURFACECONVECTIONALGORITHM:OUTSIDE': {'fields': [0], 'values': ['MoWiTT']}}},
    '13d': {'description': 'Outside convection: AdaptiveConvectionAlgorithm', 'modifications': {'SURFACECONVECTIONALGORITHM:OUTSIDE': {'fields': [0], 'values': ['AdaptiveConvectionAlgorithm']}}},
    
    # Zone air heat balance variants removed - object doesn't exist in Case 600
}

CONFIG = {
    'base_case': 'idf_files/Case600_EnergyPlus-9-4-0.idf',
    'weather_file': 'weather_files/BESTEST.epw',
    'energyplus_exe': '/Applications/EnergyPlus-9-4-0/energyplus',
    'max_parallel': 4
}