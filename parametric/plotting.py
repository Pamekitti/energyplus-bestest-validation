import matplotlib.pyplot as plt

from .utils import get_parameter_group_info, get_base_parameter_value

def create_academic_plots(df, plots_dir):
    import matplotlib
    matplotlib.rcParams.update({
        'font.family': 'serif',
        'font.serif': 'Times New Roman', 
        'font.size': 11,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 16,
        'text.usetex': False,
        'axes.linewidth': 1.2,
        'grid.linewidth': 0.8,
        'lines.linewidth': 1.5
    })
    
    groups = get_parameter_group_info()
    base_heating = df[df['variant'] == 'base']['annual_heating_load'].iloc[0] if 'base' in df['variant'].values else None
    base_cooling = df[df['variant'] == 'base']['annual_sensible_cooling_load'].iloc[0] if 'base' in df['variant'].values else None
    
    for group_id, group_info in groups.items():
        group_variants = [v for v in group_info['variants'] if v in df['variant'].values]
        if not group_variants:
            continue
        
        group_labels = [group_info['labels'][i] for i, v in enumerate(group_info['variants']) if v in group_variants]
        base_param_value = get_base_parameter_value(group_id)
        
        heating_data = []
        cooling_data = []
        all_labels = []
        
        if base_heating is not None and base_cooling is not None:
            heating_data.append(base_heating)
            cooling_data.append(base_cooling)
            base_label = f'Baseline\n({base_param_value})' if base_param_value else 'Baseline'
            all_labels.append(base_label)
        
        for i, variant in enumerate(group_variants):
            variant_data = df[df['variant'] == variant]
            if not variant_data.empty:
                heating_data.append(variant_data['annual_heating_load'].iloc[0])
                cooling_data.append(variant_data['annual_sensible_cooling_load'].iloc[0])
                all_labels.append(group_labels[i])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
        fig.patch.set_facecolor('white')
        
        base_color = '#34495E'
        variant_color = '#5D6D7E'
        colors = [base_color] + [variant_color] * len(group_variants)
        
        x_pos = range(len(heating_data))
        bar_width = 0.6
        
        bars1 = ax1.bar(x_pos, heating_data, width=bar_width, color=colors, 
                       edgecolor='black', linewidth=0.8, alpha=0.8)
        bars2 = ax2.bar(x_pos, cooling_data, width=bar_width, color=colors, 
                       edgecolor='black', linewidth=0.8, alpha=0.8)
        
        bars1[0].set_hatch('///')
        bars2[0].set_hatch('///')
        bars1[0].set_alpha(1.0)
        bars2[0].set_alpha(1.0)
        
        # Fix Y-axis limits and formatting
        h_min, h_max = min(heating_data), max(heating_data)
        c_min, c_max = min(cooling_data), max(cooling_data)
        
        h_range = h_max - h_min if h_max != h_min else h_max * 0.1
        c_range = c_max - c_min if c_max != c_min else c_max * 0.1
        
        # For very small ranges (nearly identical values), use reasonable fixed range
        if h_range < 0.01:  # Less than 0.01 MWh difference
            h_center = (h_min + h_max) / 2
            h_range = max(0.1, h_center * 0.05)  # 5% of center value or 0.1 MWh minimum
            ax1.set_ylim(h_center - h_range, h_center + h_range)
        else:
            ax1.set_ylim(h_min - h_range * 0.1, h_max + h_range * 0.2)
            
        if c_range < 0.01:  # Less than 0.01 MWh difference  
            c_center = (c_min + c_max) / 2
            c_range = max(0.1, c_center * 0.05)  # 5% of center value or 0.1 MWh minimum
            ax2.set_ylim(c_center - c_range, c_center + c_range)
        else:
            ax2.set_ylim(c_min - c_range * 0.1, c_max + c_range * 0.2)
        
        # Force proper number formatting
        ax1.ticklabel_format(style='plain', axis='y', useOffset=False)
        ax2.ticklabel_format(style='plain', axis='y', useOffset=False)
        
        # Add value annotations using default positioning
        for i, val in enumerate(heating_data):
            ax1.annotate(f'{val:.3f}', (i, val), ha='center', va='bottom', 
                        fontsize=10, fontweight='bold')
        
        for i, val in enumerate(cooling_data):
            ax2.annotate(f'{val:.3f}', (i, val), ha='center', va='bottom', 
                        fontsize=10, fontweight='bold')
        
        ax1.set_title('(a) Annual Heating Load', fontweight='bold', loc='left', pad=15)
        ax2.set_title('(b) Annual Sensible Cooling Load', fontweight='bold', loc='left', pad=15)
        
        ax1.set_ylabel('Energy Load (MWh/year)', fontweight='bold')
        ax2.set_ylabel('Energy Load (MWh/year)', fontweight='bold')
        
        for ax in [ax1, ax2]:
            ax.set_xticks(x_pos)
            ax.set_xticklabels(all_labels, rotation=15, ha='right', fontsize=10)
            ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
            ax.set_axisbelow(True)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        safe_name = group_info['name'].replace('/', '_').replace('(', '').replace(')', '').replace(' ', '_')
        filename = f"Parameter_{group_id}_{safe_name}.png"
        save_path = plots_dir / filename
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"  Created: {filename}")