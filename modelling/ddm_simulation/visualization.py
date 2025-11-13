"""
Visualization tools for DDM simulation results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List


class DDMVisualizer:
    """Visualization tools for DDM results"""
    
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        """Initialize visualizer"""
        plt.style.use(style)
        sns.set_palette("husl")
    
    def plot_population_distribution(self, diagnostics_df: pd.DataFrame, 
                                     save_path: str = None):
        """
        Plot distribution of DDM parameters across population
        
        Args:
            diagnostics_df: DataFrame with voter diagnostics
            save_path: Path to save figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('DDM Parameter Distributions Across Population', fontsize=16)
        
        # Drift rate
        axes[0, 0].hist(diagnostics_df['drift_rate'], bins=50, edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(diagnostics_df['drift_rate'].mean(), color='red', 
                          linestyle='--', label='Mean')
        axes[0, 0].set_xlabel('Drift Rate (μ)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].legend()
        axes[0, 0].set_title('Evidence Accumulation Rate')
        
        # Threshold
        axes[0, 1].hist(diagnostics_df['threshold'], bins=50, edgecolor='black', alpha=0.7)
        axes[0, 1].axvline(diagnostics_df['threshold'].mean(), color='red', 
                          linestyle='--', label='Mean')
        axes[0, 1].set_xlabel('Threshold (a)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].legend()
        axes[0, 1].set_title('Decision Threshold')
        
        # Starting point
        axes[1, 0].hist(diagnostics_df['starting_point'], bins=50, edgecolor='black', alpha=0.7)
        axes[1, 0].axvline(diagnostics_df['starting_point'].mean(), color='red', 
                          linestyle='--', label='Mean')
        axes[1, 0].set_xlabel('Starting Point (z)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].legend()
        axes[1, 0].set_title('Initial Bias')
        
        # P(Vote)
        axes[1, 1].hist(diagnostics_df['p_vote_analytical'], bins=50, 
                       edgecolor='black', alpha=0.7)
        axes[1, 1].axvline(diagnostics_df['p_vote_analytical'].mean(), color='red', 
                          linestyle='--', label=f"Mean = {diagnostics_df['p_vote_analytical'].mean():.3f}")
        axes[1, 1].set_xlabel('P(Vote)')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].legend()
        axes[1, 1].set_title('Voting Probability Distribution')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        
        plt.show()
    
    def plot_nudge_effects(self, nudge_results: Dict, save_path: str = None):
        """
        Plot nudge treatment effects
        
        Args:
            nudge_results: Results from run_nudge_experiment
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        nudge_type = nudge_results['nudge_type']
        control = nudge_results['control_turnout']
        treatment = nudge_results['treatment_turnout']
        effect = nudge_results['average_treatment_effect']
        
        categories = ['Control', 'Treatment']
        values = [control, treatment]
        colors = ['#3498db', '#e74c3c']
        
        bars = ax.bar(categories, values, color=colors, edgecolor='black', alpha=0.7)
        
        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.4f}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        # Add effect arrow
        ax.annotate('', xy=(1, treatment), xytext=(1, control),
                   arrowprops=dict(arrowstyle='<->', color='green', lw=2))
        ax.text(1.15, (control + treatment) / 2, f'ATE = {effect:.4f}',
               fontsize=12, color='green', fontweight='bold')
        
        ax.set_ylabel('Turnout Rate', fontsize=12)
        ax.set_title(f'Nudge Treatment Effect: {nudge_type.upper()}', fontsize=14, fontweight='bold')
        ax.set_ylim([0, max(values) * 1.2])
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        
        plt.show()
    
    def plot_stratified_effects(self, stratified_results: Dict, 
                               hypothesis_name: str, save_path: str = None):
        """
        Plot stratified treatment effects
        
        Args:
            stratified_results: Results from _test_stratified_effect
            hypothesis_name: Name of hypothesis (e.g., 'HN1')
            save_path: Path to save figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle(f'Stratified Treatment Effects: {hypothesis_name}', fontsize=16, fontweight='bold')
        
        strata = list(stratified_results.keys())
        control_vals = [stratified_results[s]['control_turnout'] for s in strata]
        treatment_vals = [stratified_results[s]['treatment_turnout'] for s in strata]
        effects = [stratified_results[s]['effect'] for s in strata]
        
        x = np.arange(len(strata))
        width = 0.35
        
        # Turnout comparison
        bars1 = ax1.bar(x - width/2, control_vals, width, label='Control', 
                       color='#3498db', edgecolor='black', alpha=0.7)
        bars2 = ax1.bar(x + width/2, treatment_vals, width, label='Treatment', 
                       color='#e74c3c', edgecolor='black', alpha=0.7)
        
        ax1.set_xlabel('Stratum', fontsize=12)
        ax1.set_ylabel('Turnout Rate', fontsize=12)
        ax1.set_title('Turnout by Stratum', fontsize=14)
        ax1.set_xticks(x)
        ax1.set_xticklabels(strata)
        ax1.legend()
        ax1.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.3f}',
                        ha='center', va='bottom', fontsize=9)
        
        # Treatment effects
        bars3 = ax2.bar(strata, effects, color='#2ecc71', edgecolor='black', alpha=0.7)
        ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
        ax2.set_xlabel('Stratum', fontsize=12)
        ax2.set_ylabel('Treatment Effect (ATE)', fontsize=12)
        ax2.set_title('Treatment Effect by Stratum', fontsize=14)
        ax2.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, effect in zip(bars3, effects):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{effect:.4f}',
                    ha='center', va='bottom' if effect > 0 else 'top', 
                    fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        
        plt.show()
    
    def plot_calibration_results(self, calibration_df: pd.DataFrame, 
                                save_path: str = None):
        """
        Plot calibration/grid search results
        
        Args:
            calibration_df: DataFrame from grid_search
            save_path: Path to save figure
        """
        # Get parameter columns (exclude turnout and error)
        param_cols = [c for c in calibration_df.columns if c not in ['turnout', 'error']]
        
        n_params = len(param_cols)
        fig, axes = plt.subplots(1, n_params, figsize=(5*n_params, 4))
        
        if n_params == 1:
            axes = [axes]
        
        fig.suptitle('Parameter Sensitivity Analysis', fontsize=16, fontweight='bold')
        
        for ax, param in zip(axes, param_cols):
            # Group by parameter and get mean error
            grouped = calibration_df.groupby(param)['error'].mean()
            
            ax.plot(grouped.index, grouped.values, marker='o', linewidth=2)
            ax.set_xlabel(param, fontsize=12)
            ax.set_ylabel('Mean Absolute Error', fontsize=12)
            ax.set_title(f'Sensitivity to {param}', fontsize=12)
            ax.grid(alpha=0.3)
            
            # Mark minimum
            min_idx = grouped.idxmin()
            min_val = grouped.min()
            ax.axvline(min_idx, color='red', linestyle='--', alpha=0.5)
            ax.text(min_idx, min_val, f'  Min: {min_idx:.3f}', 
                   fontsize=9, color='red')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        
        plt.show()
    
    def plot_decision_trajectory(self, voter, n_simulations: int = 10, 
                                save_path: str = None):
        """
        Plot example DDM decision trajectories
        
        Args:
            voter: DDMVoter object
            n_simulations: Number of trajectories to plot
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for i in range(n_simulations):
            X = voter.z
            t = 0
            dt = 0.01
            max_time = 5.0
            
            trajectory_t = [t]
            trajectory_X = [X]
            
            while t < max_time:
                dW = np.random.normal(0, np.sqrt(dt))
                dX = voter.mu * dt + voter.sigma * dW
                X += dX
                t += dt
                
                trajectory_t.append(t)
                trajectory_X.append(X)
                
                if X >= voter.a or X <= 0:
                    break
            color = 'green' if X >= voter.a else 'red'
            ax.plot(trajectory_t, trajectory_X, alpha=0.6, linewidth=1.5, color=color)
        
        # Plot boundaries
        ax.axhline(y=voter.a, color='green', linestyle='--', linewidth=2, 
                  label=f'Vote Threshold (a={voter.a:.2f})')
        ax.axhline(y=0, color='red', linestyle='--', linewidth=2, 
                  label='Abstain Boundary (0)')
        ax.axhline(y=voter.z, color='blue', linestyle=':', linewidth=2, 
                  label=f'Starting Point (z={voter.z:.2f})')
        
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Evidence (X)', fontsize=12)
        ax.set_title(f'DDM Decision Trajectories (μ={voter.mu:.3f}, σ={voter.sigma:.3f})', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")
        
        plt.show()