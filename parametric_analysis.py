#!/usr/bin/env python3

import sys
import argparse
import shutil
from pathlib import Path

from parametric import run_simulations, extract_all_results, analyze_results, CONFIG

def clean():
    parametric_dir = Path("parametric")
    if parametric_dir.exists():
        for item in parametric_dir.iterdir():
            if item.name not in ['__init__.py', 'config.py', 'simulation.py', 'extraction.py', 'plotting.py', 'analysis.py', 'utils.py']:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        print("Cleaned")
    return True

def run():
    sim_results = run_simulations()
    if not sim_results:
        return False
    df = extract_all_results(sim_results)
    return not df.empty

def main():
    parser = argparse.ArgumentParser(description='BESTEST Parametric Analysis')
    parser.add_argument('command', choices=['clean', 'run', 'analyze', 'run_full'])
    parser.add_argument('--parallel', type=int, default=4, help='Max parallel simulations')
    
    args = parser.parse_args()
    CONFIG['max_parallel'] = args.parallel
    
    if args.command == 'clean':
        return clean()
    elif args.command == 'run':
        return run()
    elif args.command == 'analyze':
        csv_file = Path("parametric/results/results.csv")
        if csv_file.exists():
            import pandas as pd
            df = pd.read_csv(csv_file)
            return analyze_results(df)
        else:
            print("No results.csv found. Run simulations first.")
            return False
    elif args.command == 'run_full':
        clean()
        sim_results = run_simulations()
        if sim_results:
            df = extract_all_results(sim_results)
            if not df.empty and analyze_results(df):
                print("Complete")
                return True
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)