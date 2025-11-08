#!/usr/bin/env python3

import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelweight': 'bold',
    'axes.titleweight': 'bold',
    'axes.linewidth': 1.2,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'figure.facecolor': 'white'
})

class BESTESTComparison:
    def __init__(self, reference_file='results/OTHER_TOOLS.json', results_file='results/FORMATTED_RESULTS.json'):
        with open(reference_file, 'r') as f:
            self.reference = json.load(f)
        with open(results_file, 'r') as f:
            self.results = json.load(f)
        
        self.colors = {
            'reference': '#5D6D7E',
            'energyplus': '#34495E',
            'range': '#85929E',
            'mean': '#2C3E50',
            'text': '#2C3E50'
        }
    
    def compare_metric(self, metric_name, case='case_600'):
        ref_metric = self.reference['metrics'].get(metric_name)
        if not ref_metric:
            return None
        
        your_value = self.results[case].get(metric_name)
        if isinstance(your_value, dict) and 'value' in your_value:
            your_value = your_value['value']
        
        stats = ref_metric['statistics']
        
        return {
            'metric': metric_name,
            'your_value': your_value,
            'ref_min': stats['min'],
            'ref_max': stats['max'],
            'ref_mean': stats['mean'],
            'within_range': stats['min'] <= your_value <= stats['max'] if your_value else False,
            'unit': ref_metric['unit']
        }
    
    def compare_all_metrics(self):
        results = []
        metrics = [
            'annual_heating_load', 'annual_sensible_cooling_load',
            'peak_heating_load', 'peak_sensible_cooling_load',
            'annual_incident_solar_horizontal', 'annual_incident_solar_north',
            'annual_incident_solar_east', 'annual_incident_solar_south',
            'annual_incident_solar_west', 'annual_transmitted_solar_south',
            'transmissivity_coefficient_south'
        ]
        
        for metric in metrics:
            comp = self.compare_metric(metric, 'case_600')
            if comp:
                results.append(comp)
        
        for metric in ['free_float_mean_temperature', 'free_float_max_temperature', 'free_float_min_temperature']:
            comp = self.compare_metric(metric, 'case_600FF')
            if comp:
                results.append(comp)
        
        return pd.DataFrame(results)
    
    def plot_comparison(self, metric_name, save_path=None):
        ref_metric = self.reference['metrics'].get(metric_name)
        if not ref_metric:
            return
        
        ref_values = ref_metric['reference_values']
        tools = list(ref_values.keys())
        values = []
        for v in ref_values.values():
            if isinstance(v, dict) and 'value' in v:
                values.append(v['value'])
            else:
                values.append(v)
        
        your_value = self.results['case_600'].get(metric_name)
        if isinstance(your_value, dict) and 'value' in your_value:
            your_value = your_value['value']
        
        if your_value:
            tools.append('EnergyPlus 25.1')
            values.append(your_value)
        
        fig, ax = plt.subplots(figsize=(11, 6.5), dpi=100)
        fig.patch.set_facecolor('white')
        
        x_pos = range(len(tools))
        colors = [self.colors['energyplus'] if tool == 'EnergyPlus 25.1' else self.colors['reference'] for tool in tools]
        bars = ax.bar(x_pos, values, color=colors, alpha=0.8, width=0.6, edgecolor='black', linewidth=0.8)
        
        if your_value:
            bars[-1].set_alpha(0.9)
            bars[-1].set_edgecolor(self.colors['energyplus'])
            bars[-1].set_linewidth(2)
        
        stats = ref_metric['statistics']
        ax.axhspan(stats['min'], stats['max'], alpha=0.1, color=self.colors['range'], zorder=0, label='Acceptable Range')
        ax.axhline(y=stats['mean'], color=self.colors['mean'], linestyle='--', linewidth=1.5, alpha=0.7, zorder=1, label='Reference Mean')
        ax.axhline(y=stats['min'], color=self.colors['range'], linestyle=':', linewidth=1.0, alpha=0.5)
        ax.axhline(y=stats['max'], color=self.colors['range'], linestyle=':', linewidth=1.0, alpha=0.5)
        
        all_values = values + [stats['min'], stats['max']]
        data_range = max(all_values) - min(all_values)
        y_margin_bottom = data_range * 0.06
        y_margin_top = data_range * 0.25
        ax.set_ylim(min(all_values) - y_margin_bottom, max(all_values) + y_margin_top)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(tools, rotation=25, ha='right', fontsize=10)
        
        labels = ax.get_xticklabels()
        for i, label in enumerate(labels):
            if label.get_text() == 'EnergyPlus 25.1':
                label.set_weight('600')
                label.set_color(self.colors['energyplus'])
                label.set_fontsize(10.5)
        
        title = metric_name.replace('_', ' ').title()
        ax.set_title(title, fontweight='bold', pad=20)
        ax.set_ylabel(f"{title} ({ref_metric['unit']})", fontweight='bold')
        
        for i, (tool, val) in enumerate(zip(tools, values)):
            if tool == 'EnergyPlus 25.1':
                ax.text(i, val + data_range * 0.015, f'{val:.2f}', ha='center', va='bottom', 
                       fontsize=10, fontweight='600', color=self.colors['energyplus'])
            else:
                ax.text(i, val + data_range * 0.015, f'{val:.2f}', ha='center', va='bottom', 
                       fontsize=9.5, color=self.colors['text'], alpha=0.8, fontweight='400')
        
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=self.colors['reference'], alpha=0.8, label='Reference Tools'),
            Patch(facecolor=self.colors['energyplus'], alpha=0.9, label='EnergyPlus 25.1'),
            Patch(facecolor=self.colors['range'], alpha=0.1, label='Acceptable Range'),
            plt.Line2D([0], [0], color=self.colors['mean'], linewidth=2.5, alpha=0.85, label='Reference Mean')
        ]
        
        legend = ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.98), ncol=2,
                          fontsize=10, frameon=True, fancybox=False)
        legend.get_frame().set_linewidth(0.5)
        legend.get_frame().set_alpha(0.98)
        
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)
        ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', which='major', labelsize=10, width=0.8)
        
        plt.tight_layout(pad=1.5)
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
    
    def plot_all_comparisons(self):
        Path('results_analysis').mkdir(exist_ok=True)
        metrics = ['annual_heating_load', 'annual_sensible_cooling_load', 'peak_heating_load', 
                  'peak_sensible_cooling_load', 'annual_incident_solar_horizontal',
                  'annual_transmitted_solar_south', 'transmissivity_coefficient_south']
        
        for metric in metrics:
            self.plot_comparison(metric, f"results_analysis/{metric}.png")
    
    def plot_monthly_comparison(self, data_type='heating', save_path=None):
        if 'monthly_data' not in self.reference:
            return
        
        ref_key = 'heating_loads' if data_type == 'heating' else 'cooling_loads'
        result_key = f'monthly_{data_type}_loads'
        
        ref_monthly = self.reference['monthly_data'].get(ref_key)
        your_monthly = self.results['case_600'].get(result_key, {})
        
        if not ref_monthly:
            return
        
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                 'july', 'august', 'september', 'october', 'november', 'december']
        
        comparison_data = []
        for month in months:
            if month in ref_monthly.get('months', {}):
                stats = ref_monthly['months'][month]['statistics']
                your_value = your_monthly.get(month, 0)
                within_range = stats['min'] <= your_value <= stats['max']
                comparison_data.append({
                    'month': month.capitalize(),
                    'your_value': your_value,
                    'ref_min': stats['min'],
                    'ref_max': stats['max'],
                    'ref_mean': stats['mean'],
                    'within_range': within_range
                })
        
        if not comparison_data:
            return
            
        df = pd.DataFrame(comparison_data)
        
        fig, ax = plt.subplots(figsize=(12, 6.5), dpi=100)
        fig.patch.set_facecolor('white')
        
        months_short = df['month'].tolist()
        x_pos = range(len(months_short))
        
        ax.fill_between(x_pos, df['ref_min'], df['ref_max'], alpha=0.12, color=self.colors['range'], 
                        label='Acceptable Range', zorder=0)
        
        ax.plot(x_pos, df['ref_mean'], color=self.colors['mean'], linestyle='--', linewidth=1.5, alpha=0.7, 
                label='Reference Mean', marker='o', markersize=4, markerfacecolor='white', 
                markeredgecolor=self.colors['mean'], markeredgewidth=1.5, zorder=2)
        
        colors = [self.colors['energyplus'] if not within else self.colors['reference'] for within in df['within_range']]
        alphas = [0.95 if not within else 0.8 for within in df['within_range']]
        
        for i, (x, y, color, alpha, within) in enumerate(zip(x_pos, df['your_value'], colors, alphas, df['within_range'])):
            edgecolor = self.colors['energyplus'] if not within else self.colors['reference']
            linewidth = 2.0 if not within else 1.2
            ax.scatter(x, y, c=color, s=60, alpha=alpha, zorder=5, edgecolors=edgecolor, linewidth=linewidth)
        
        ax.plot(x_pos, df['your_value'], color=self.colors['energyplus'], alpha=0.8, linewidth=2.5, zorder=1)
        
        for i, val in enumerate(df['your_value']):
            ax.text(i, val + max(df['ref_max']) * 0.02, f'{val:.0f}', ha='center', va='bottom', 
                   fontsize=9.5, fontweight='500')
        
        title = f"Monthly {data_type.title()} Loads Comparison - Case 600"
        ax.set_title(title, fontweight='bold', pad=20)
        ax.set_ylabel(f"Monthly {data_type.title()} Load (kWh)", fontweight='bold')
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels([m[:3] for m in months_short], fontsize=10)
        
        from matplotlib.patches import Patch
        legend_elements = [
            plt.Line2D([0], [0], color=self.colors['mean'], linewidth=1.5, alpha=0.7, linestyle='--', 
                      marker='o', markersize=4, markerfacecolor='white', markeredgecolor=self.colors['mean'], 
                      label='Reference Mean'),
            Patch(facecolor=self.colors['range'], alpha=0.12, label='Acceptable Range'),
            plt.Line2D([0], [0], color=self.colors['energyplus'], marker='o', markersize=6, linewidth=2.5, 
                      markerfacecolor=self.colors['energyplus'], alpha=0.8, label='EnergyPlus 25.1')
        ]
        
        legend = ax.legend(handles=legend_elements, loc='upper right', fontsize=10, frameon=True, fancybox=False)
        legend.get_frame().set_linewidth(0.5)
        legend.get_frame().set_alpha(0.98)
        
        ax.spines['left'].set_linewidth(1.2)
        ax.spines['bottom'].set_linewidth(1.2)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        ax.tick_params(axis='both', which='major', labelsize=10, width=0.8)
        
        plt.tight_layout(pad=1.5)
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()
    
    def generate_comparison_report(self):
        df = self.compare_all_metrics()
        
        Path('results_analysis').mkdir(exist_ok=True)
        with open('results_analysis/results_report.txt', 'w') as f:
            f.write("BESTEST VALIDATION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Tool: {self.results['metadata']['simulation_tool']} v{self.results['metadata']['version']}\n")
            f.write(f"Date: {self.results['metadata']['date_run']}\n\n")
            
            passed = df['within_range'].sum()
            total = len(df)
            f.write(f"Summary: {passed}/{total} metrics within acceptable range\n\n")
            
            # Group by categories
            energy_metrics = df[df['metric'].str.contains('annual|peak')]
            solar_metrics = df[df['metric'].str.contains('solar|transmissivity')]
            temp_metrics = df[df['metric'].str.contains('temperature')]
            
            categories = [
                ("Energy Performance", energy_metrics),
                ("Solar Radiation", solar_metrics), 
                ("Temperature Response", temp_metrics)
            ]
            
            for cat_name, cat_df in categories:
                if not cat_df.empty:
                    cat_passed = cat_df['within_range'].sum()
                    cat_total = len(cat_df)
                    f.write(f"{cat_name} ({cat_passed}/{cat_total})\n")
                    f.write("-" * len(cat_name) + "\n")
                    
                    for _, row in cat_df.iterrows():
                        status = "✓" if row['within_range'] else "✗"
                        metric_name = row['metric'].replace('_', ' ').replace('annual ', '').replace('peak ', '').title()
                        f.write(f"{status} {metric_name}: {row['your_value']:.3f} {row['unit']}")
                        
                        if not row['within_range']:
                            if row['your_value'] < row['ref_min']:
                                f.write(" (below range)")
                            else:
                                f.write(" (above range)")
                        f.write(f" [ref: {row['ref_min']:.3f}-{row['ref_max']:.3f}]\n")
                    f.write("\n")
            
            # Failed metrics if any
            if passed < total:
                failed = df[~df['within_range']]
                f.write("Failed Validation\n")
                f.write("-" * 17 + "\n")
                for _, row in failed.iterrows():
                    metric_name = row['metric'].replace('_', ' ').title()
                    f.write(f"✗ {metric_name}: {row['your_value']:.3f} {row['unit']}")
                    if row['your_value'] < row['ref_min']:
                        f.write(" (below minimum)\n")
                    else:
                        f.write(" (above maximum)\n")
                f.write("\n")
            
            # Performance data
            heating = df[df['metric'] == 'annual_heating_load']['your_value'].iloc[0]
            cooling = df[df['metric'] == 'annual_sensible_cooling_load']['your_value'].iloc[0]
            peak_heat = df[df['metric'] == 'peak_heating_load']['your_value'].iloc[0]
            peak_cool = df[df['metric'] == 'peak_sensible_cooling_load']['your_value'].iloc[0]
            
            f.write("Performance Summary\n")
            f.write("-" * 19 + "\n")
            f.write(f"Annual loads: {heating:.2f} MWh heating, {cooling:.2f} MWh cooling\n")
            f.write(f"Peak loads: {peak_heat:.2f} kW heating, {peak_cool:.2f} kW cooling\n")
            f.write(f"Load factor heating: {(heating*1000)/(peak_heat*8760)*100:.1f}%\n")
            f.write(f"Load factor cooling: {(cooling*1000)/(peak_cool*8760)*100:.1f}%\n")
            
        return df

def main():
    comparison = BESTESTComparison()
    df = comparison.generate_comparison_report()
    
    passed = df['within_range'].sum()
    total = len(df)
    print(f"BESTEST validation: {passed}/{total} passed")
    
    comparison.plot_all_comparisons()
    comparison.plot_monthly_comparison('heating', 'results_analysis/monthly_heating_comparison.png')
    comparison.plot_monthly_comparison('cooling', 'results_analysis/monthly_cooling_comparison.png')

if __name__ == "__main__":
    main()