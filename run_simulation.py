#!/usr/bin/env python3

import subprocess
import os
import sys

def run_simulation(idf_file, output_dir):
    energyplus = "/Applications/EnergyPlus-25-1-0/energyplus"
    weather = "weather_files/BESTEST.epw"
    
    if not os.path.exists(idf_file):
        print(f"Missing: {idf_file}")
        return False
    if not os.path.exists(weather):
        print(f"Missing: {weather}")
        return False
    if not os.path.exists(energyplus):
        print(f"Missing: {energyplus}")
        return False
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        cmd = [energyplus, "-w", weather, "-d", output_dir, idf_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Done: {output_dir}")
            return True
        else:
            print(f"Failed: {result.returncode}")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    cases = [
        ("idf_files/Case600_EnergyPlus-25-1-0.idf", "Case600_output"),
        ("idf_files/Case600FF_EnergyPlus-25-1-0.idf", "Case600FF_output")
    ]
    
    success = 0
    for idf, output in cases:
        if run_simulation(idf, output):
            success += 1
    
    print(f"Completed {success}/{len(cases)} simulations")
    return success == len(cases)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)