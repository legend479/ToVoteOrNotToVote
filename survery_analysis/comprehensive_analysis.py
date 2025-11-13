"""
Voter Motivation Survey - Comprehensive Analysis (ROBUST VERSION)
==================================================================
Fixed version that handles missing data properly
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

class VoterSurveyAnalysis:
    """Comprehensive analysis class for voter motivation survey."""
    
    def __init__(self, filepath):
        """Load and prepare data."""
        self.df = pd.read_csv(filepath)
        
        # Ensure numeric columns are numeric
        numeric_cols = [f'q{i}_' for i in range(1, 14)]
        for col in self.df.columns:
            if any(col.startswith(prefix) for prefix in numeric_cols) and col != 'q14_open_response':
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        self.question_labels = {
            'q1_emotion': 'Emotional Connection',
            'q2_frequency': 'Voting History',
            'q3_effort_tradeoff': 'Effort Trade-off',
            'q4_perceived_impact': 'Perceived Impact',
            'q5_civic_duty': 'Civic Duty',
            'q6_emotional_reward': 'Emotional Reward',
            'q7_trust': 'Trust in System',
            'q8_social_influence': 'Social Influence',
            'q9_information_load': 'Information Load',
            'q10_disillusionment': 'Disillusionment',
            'q11_online_voting': 'Online Voting Interest',
            'q12_competitiveness': 'Electoral Competitiveness',
            'q13_incentive': 'Incentive Preference'
        }
        
    def create_composite_scores(self):
        """Create composite scores for theoretical constructs."""
        print("\n" + "="*60)
        print("CREATING COMPOSITE SCORES FOR MODEL VARIABLES")
        print("="*60)
        
        # Civic Duty score (direct)
        self.df['civic_duty_score'] = 6 - self.df['q5_civic_duty']  # Reverse so higher = more duty
        
        # Social Pressure score (reverse - higher = more susceptible)
        self.df['social_pressure_score'] = 6 - self.df['q8_social_influence']
        
        # Habit strength (reverse coded - higher = stronger habit)
        self.df['habit_score'] = 6 - self.df['q2_frequency']
        
        # Perceived Cost (higher = more costly, reverse coded)
        cost_cols = ['q3_effort_tradeoff', 'q9_information_load']
        self.df['cost_score'] = self.df[cost_cols].mean(axis=1)
        
        # Perceived Benefit (reverse coded - higher = more benefit)
        self.df['benefit_score'] = ((6 - self.df['q4_perceived_impact']) + 
                                     (6 - self.df['q12_competitiveness'])) / 2
        
        # System Trust (reverse coded - higher = more trust)
        trust_cols = ['q7_trust', 'q10_disillusionment']
        self.df['trust_score'] = 6 - self.df[trust_cols].mean(axis=1)
        
        # Overall Engagement Score
        engagement_components = ['civic_duty_score', 'habit_score', 'benefit_score', 'trust_score']
        self.df['engagement_score'] = self.df[engagement_components].mean(axis=1)
        
        # Voting Likelihood (theoretical utility proxy)
        self.df['voting_utility'] = (
            self.df['benefit_score'] * 0.2 +
            -self.df['cost_score'] * 0.15 +
            self.df['civic_duty_score'] * 0.25 +
            self.df['social_pressure_score'] * 0.15 +
            self.df['habit_score'] * 0.25
        )
        
        print("\nComposite Scores Created:")
        composite_scores = ['civic_duty_score', 'social_pressure_score', 'habit_score', 
                          'cost_score', 'benefit_score', 'trust_score', 
                          'engagement_score', 'voting_utility']
        
        for score in composite_scores:
            valid_n = self.df[score].count()
            mean_val = self.df[score].mean()
            std_val = self.df[score].std()
            print(f"  {score}: N={valid_n}, Mean={mean_val:.2f}, SD={std_val:.2f}")
        
    def plot_individual_distributions(self, save_path='plots'):
        """Create distribution plots for all survey questions."""
        import os
        os.makedirs(save_path, exist_ok=True)
        
        print("\n" + "="*60)
        print("GENERATING INDIVIDUAL QUESTION DISTRIBUTIONS")
        print("="*60)
        
        # Only numeric questions
        question_cols = [f'q{i}_{name}' for i, name in [
            (1, 'emotion'), (2, 'frequency'), (3, 'effort_tradeoff'),
            (4, 'perceived_impact'), (5, 'civic_duty'), (6, 'emotional_reward'),
            (7, 'trust'), (8, 'social_influence'), (9, 'information_load'),
            (10, 'disillusionment'), (11, 'online_voting'), (12, 'competitiveness'),
            (13, 'incentive')
        ]]
        
        question_cols = [col for col in question_cols if col in self.df.columns]
        
        fig, axes = plt.subplots(5, 3, figsize=(18, 20))
        axes = axes.flatten()
        
        for idx, col in enumerate(question_cols):
            if idx >= len(axes):
                break
                
            data = self.df[col].dropna()
            
            if len(data) == 0:
                continue
            
            axes[idx].hist(data, bins=5, alpha=0.6, color='skyblue', edgecolor='black')
            axes[idx].axvline(data.mean(), color='red', linestyle='--', linewidth=2, 
                             label=f'Mean: {data.mean():.2f}')
            axes[idx].axvline(data.median(), color='green', linestyle='--', linewidth=2, 
                             label=f'Median: {data.median():.1f}')
            
            axes[idx].set_title(f'{self.question_labels.get(col, col)}\n(N={len(data)})', 
                               fontsize=11, fontweight='bold')
            axes[idx].set_xlabel('Score', fontsize=9)
            axes[idx].set_ylabel('Frequency', fontsize=9)
            axes[idx].legend(fontsize=8)
            axes[idx].grid(alpha=0.3)
        
        for idx in range(len(question_cols), len(axes)):
            fig.delaxes(axes[idx])
        
        plt.tight_layout()
        plt.savefig(f'{save_path}/individual_distributions.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {save_path}/individual_distributions.png")
        plt.close()
        
    def correlation_analysis(self, save_path='plots'):
        """Comprehensive correlation analysis."""
        import os
        os.makedirs(save_path, exist_ok=True)
        
        print("\n" + "="*60)
        print("CORRELATION ANALYSIS")
        print("="*60)
        
        numeric_cols = [col for col in self.df.columns 
                       if col.startswith('q') and col[1].isdigit() and col != 'q14_open_response']
        
        corr_matrix = self.df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(14, 12))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8},
                   xticklabels=[self.question_labels.get(col, col) for col in numeric_cols],
                   yticklabels=[self.question_labels.get(col, col) for col in numeric_cols])
        plt.title('Correlation Matrix - Survey Questions', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'{save_path}/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {save_path}/correlation_heatmap.png")
        plt.close()
        
        print("\n🔍 Strong Correlations (|r| > 0.4):")
        strong_corrs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.4:
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    strong_corrs.append((col1, col2, corr_val))
                    print(f"  {self.question_labels.get(col1, col1)} ↔ {self.question_labels.get(col2, col2)}: r={corr_val:.3f}")
        
        if not strong_corrs:
            print("  No correlations above 0.4 threshold")
            
        return corr_matrix
    
    def model_component_correlations(self, save_path='plots'):
        """Analyze correlations between theoretical model components."""
        import os
        os.makedirs(save_path, exist_ok=True)
        
        print("\n" + "="*60)
        print("MODEL COMPONENT CORRELATIONS")
        print("="*60)
        print("Based on Extended Rational Choice Model: U(vote) = pB - C + D + S + H")
        
        model_components = ['civic_duty_score', 'social_pressure_score', 'habit_score', 
                          'cost_score', 'benefit_score', 'trust_score']
        
        component_data = self.df[model_components].dropna()
        
        if len(component_data) < 10:
            print("⚠ Not enough complete data for model correlations")
            return None
        
        corr_model = component_data.corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_model, annot=True, fmt='.3f', cmap='RdYlGn', center=0,
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   vmin=-1, vmax=1)
        plt.title('Correlations Between Theoretical Model Components', 
                 fontsize=14, fontweight='bold', pad=15)
        plt.tight_layout()
        plt.savefig(f'{save_path}/model_components_correlation.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {save_path}/model_components_correlation.png")
        plt.close()
        
        print("\n📊 Key Model Relationships:")
        
        # Use pairwise complete observations
        def safe_corr(col1, col2):
            data = self.df[[col1, col2]].dropna()
            if len(data) > 10:
                r, p = stats.pearsonr(data[col1], data[col2])
                return r, p, len(data)
            return None, None, 0
        
        # Test relationships
        relationships = [
            ('civic_duty_score', 'voting_utility', 'Civic Duty → Voting Utility'),
            ('habit_score', 'voting_utility', 'Habit → Voting Utility'),
            ('cost_score', 'voting_utility', 'Cost → Voting Utility'),
            ('benefit_score', 'voting_utility', 'Benefit → Voting Utility'),
        ]
        
        for col1, col2, label in relationships:
            r, p, n = safe_corr(col1, col2)
            if r is not None:
                print(f"  {label}: r={r:.3f}, p={p:.4f} (N={n})")
        
        return corr_model
    
    def create_summary_plots(self, save_path='plots'):
        """Create key summary visualizations."""
        import os
        os.makedirs(save_path, exist_ok=True)
        
        print("\n" + "="*60)
        print("CREATING SUMMARY VISUALIZATIONS")
        print("="*60)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Composite Score Distributions
        composite_scores = ['civic_duty_score', 'social_pressure_score', 'habit_score', 
                          'engagement_score']
        score_data = [self.df[score].dropna() for score in composite_scores]
        
        axes[0, 0].boxplot(score_data, labels=['Civic\nDuty', 'Social\nPressure', 'Habit', 'Engagement'])
        axes[0, 0].set_title('Composite Score Distributions', fontweight='bold')
        axes[0, 0].set_ylabel('Score')
        axes[0, 0].grid(alpha=0.3)
        
        # 2. Age Distribution
        if 'age_range' in self.df.columns:
            age_counts = self.df['age_range'].value_counts()
            axes[0, 1].bar(range(len(age_counts)), age_counts.values, color='coral', alpha=0.7)
            axes[0, 1].set_xticks(range(len(age_counts)))
            axes[0, 1].set_xticklabels(age_counts.index, rotation=45, ha='right')
            axes[0, 1].set_title('Sample Distribution by Age', fontweight='bold')
            axes[0, 1].set_ylabel('Count')
            axes[0, 1].grid(alpha=0.3, axis='y')
        
        # 3. Engagement by Age
        if 'age_range' in self.df.columns:
            age_eng = self.df.groupby('age_range')['engagement_score'].mean().sort_values()
            axes[1, 0].barh(range(len(age_eng)), age_eng.values, color='steelblue', alpha=0.7)
            axes[1, 0].set_yticks(range(len(age_eng)))
            axes[1, 0].set_yticklabels(age_eng.index)
            axes[1, 0].set_title('Average Engagement by Age', fontweight='bold')
            axes[1, 0].set_xlabel('Engagement Score')
            axes[1, 0].grid(alpha=0.3, axis='x')
        
        # 4. Voting Utility Distribution
        util_data = self.df['voting_utility'].dropna()
        axes[1, 1].hist(util_data, bins=15, color='seagreen', alpha=0.7, edgecolor='black')
        axes[1, 1].axvline(util_data.mean(), color='red', linestyle='--', linewidth=2, 
                          label=f'Mean: {util_data.mean():.2f}')
        axes[1, 1].set_title('Voting Utility Distribution', fontweight='bold')
        axes[1, 1].set_xlabel('Voting Utility Score')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].legend()
        axes[1, 1].grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{save_path}/summary_visualizations.png', dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {save_path}/summary_visualizations.png")
        plt.close()
    
    def generate_full_report(self, save_path='plots'):
        """Run all analyses and generate comprehensive report."""
        print("\n" + "🎯" * 30)
        print("COMPREHENSIVE VOTER SURVEY ANALYSIS")
        print("🎯" * 30)
        print(f"\nDataset: {len(self.df)} responses")
        print(f"Analysis output directory: {save_path}")
        
        # Create composite scores
        self.create_composite_scores()
        
        # Individual distributions
        self.plot_individual_distributions(save_path)
        
        # Correlation analysis
        self.correlation_analysis(save_path)
        
        # Model component correlations
        self.model_component_correlations(save_path)
        
        # Summary plots
        self.create_summary_plots(save_path)
        
        print("\n" + "✅" * 30)
        print("ANALYSIS COMPLETE!")
        print("✅" * 30)
        print(f"\nAll plots saved to: {save_path}/")
        print("\nGenerated visualizations:")
        print("  ✓ individual_distributions.png")
        print("  ✓ correlation_heatmap.png")
        print("  ✓ model_components_correlation.png")
        print("  ✓ summary_visualizations.png")
        print("\n📊 Ready for model calibration!")


if __name__ == "__main__":
    print("Voter Motivation Survey - Comprehensive Analysis")
    print("=" * 60)
    
    filepath = input("\nEnter path to your numeric CSV file: ").strip()
    if not filepath:
        filepath = 'survey_responses_numeric_fixed.csv'
        print(f"Using default: {filepath}")
    
    try:
        analyzer = VoterSurveyAnalysis(filepath)
        analyzer.generate_full_report(save_path='voter_analysis_plots')
        
        print("\n🎉 Success! Check voter_analysis_plots/ folder for results")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Try running: python fix_survey_data.py first")
        print("   Then use the _fixed.csv file")