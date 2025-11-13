"""
Neuroeconomics Hypothesis Testing (ROBUST VERSION)
===================================================
Tests specific hypotheses from your voter turnout models
Handles missing data properly
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class HypothesisTester:
    """Test specific hypotheses from neuroeconomics framework."""
    
    def __init__(self, filepath):
        """Initialize with filepath and create composite scores if needed."""
        self.df = pd.read_csv(filepath)
        
        # Ensure numeric
        numeric_cols = [f'q{i}_' for i in range(1, 14)]
        for col in self.df.columns:
            if any(col.startswith(prefix) for prefix in numeric_cols) and col != 'q14_open_response':
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Check if composite scores exist, if not create them
        if 'civic_duty_score' not in self.df.columns:
            print("⚠ Composite scores not found. Creating them...")
            self.create_composite_scores()
        else:
            print("✓ Composite scores found in dataset")
    
    def create_composite_scores(self):
        """Create composite scores if they don't exist."""
        self.df['civic_duty_score'] = 6 - self.df['q5_civic_duty']
        self.df['social_pressure_score'] = 6 - self.df['q8_social_influence']
        self.df['habit_score'] = 6 - self.df['q2_frequency']
        self.df['cost_score'] = self.df[['q3_effort_tradeoff', 'q9_information_load']].mean(axis=1)
        self.df['benefit_score'] = ((6 - self.df['q4_perceived_impact']) + 
                                     (6 - self.df['q12_competitiveness'])) / 2
        self.df['trust_score'] = 6 - self.df[['q7_trust', 'q10_disillusionment']].mean(axis=1)
        self.df['engagement_score'] = self.df[['civic_duty_score', 'habit_score', 
                                                'benefit_score', 'trust_score']].mean(axis=1)
        self.df['voting_utility'] = (
            self.df['benefit_score'] * 0.2 +
            -self.df['cost_score'] * 0.15 +
            self.df['civic_duty_score'] * 0.25 +
            self.df['social_pressure_score'] * 0.15 +
            self.df['habit_score'] * 0.25
        )
    
    def safe_corr(self, col1, col2):
        """Safely compute correlation handling missing data."""
        data = self.df[[col1, col2]].dropna()
        if len(data) >= 10:  # Need at least 10 pairs
            r, p = stats.pearsonr(data[col1], data[col2])
            return r, p, len(data)
        return None, None, 0
    
    def test_civic_duty_hypothesis(self):
        """
        H1: Civic duty should be a strong predictor of voting utility.
        Extended RC Model: D (civic duty) → U(vote)
        """
        print("\n" + "="*60)
        print("HYPOTHESIS 1: CIVIC DUTY AS PREDICTOR")
        print("="*60)
        print("Extended RC Model predicts: D (civic duty) → U(vote)")
        
        r, p, n = self.safe_corr('civic_duty_score', 'voting_utility')
        
        if r is not None:
            print(f"\nCorrelation: r = {r:.3f}, p = {p:.4f} (N = {n})")
            
            if p < 0.05:
                direction = "positively" if r > 0 else "negatively"
                print(f"✓ SIGNIFICANT: Civic duty {direction} predicts voting utility")
            else:
                print("✗ NOT SIGNIFICANT: No clear relationship")
            
            print(f"Effect size (r²): {r**2:.3f} ({r**2*100:.1f}% variance explained)")
            
            # Quartile analysis
            civic_duty = self.df['civic_duty_score'].dropna()
            if len(civic_duty) > 20:
                try:
                    quartiles = pd.qcut(civic_duty, q=4, labels=False, duplicates='drop')
                    # Map to labels based on actual number of bins created
                    unique_quartiles = sorted(quartiles.unique())
                    n_bins = len(unique_quartiles)
                    
                    if n_bins >= 3:
                        quartile_labels = {
                            unique_quartiles[0]: 'Low',
                            unique_quartiles[-1]: 'High'
                        }
                        if n_bins >= 3:
                            quartile_labels[unique_quartiles[len(unique_quartiles)//2]] = 'Medium'
                        
                        self.df.loc[civic_duty.index, 'civic_quartile'] = quartiles
                        
                        print("\nVoting Utility by Civic Duty Level:")
                        for q_val in unique_quartiles:
                            label = quartile_labels.get(q_val, f'Q{q_val}')
                            subset = self.df[self.df['civic_quartile'] == q_val]['voting_utility']
                            if len(subset) > 0:
                                print(f"  {label}: M={subset.mean():.2f}, N={len(subset)}")
                except Exception as e:
                    print(f"\n  ⚠ Could not create quartiles: {e}")
                    print("  (Using correlation only)")
        else:
            print("⚠ Insufficient data for correlation")
            r, p = 0, 1
        
        return {'r': r, 'p': p, 'n': n if n else 0}
    
    def test_habit_formation_hypothesis(self):
        """
        H2: Past voting frequency (habit) should predict current engagement.
        RL Model: Past behavior → Habit strength → Current utility
        """
        print("\n" + "="*60)
        print("HYPOTHESIS 2: HABIT FORMATION (H component)")
        print("="*60)
        print("RL Model: Past behavior → Habit strength → Current utility")
        
        r, p, n = self.safe_corr('habit_score', 'engagement_score')
        
        if r is not None:
            print(f"\nHabit → Engagement: r = {r:.3f}, p = {p:.4f} (N = {n})")
            
            if p < 0.05:
                print(f"✓ SIGNIFICANT: Stronger habits associate with higher engagement")
            else:
                print("✗ NOT SIGNIFICANT")
            
            # Age interaction
            if 'age_range' in self.df.columns:
                print("\nAge Group Analysis:")
                for age_group in self.df['age_range'].dropna().unique():
                    subset = self.df[self.df['age_range'] == age_group]
                    if len(subset) >= 10:
                        r_age, p_age, n_age = self.safe_corr('habit_score', 'engagement_score')
                        if r_age is not None:
                            print(f"  {age_group}: r = {r_age:.3f}, p = {p_age:.4f} (N = {n_age})")
        else:
            print("⚠ Insufficient data")
            r, p = 0, 1
        
        return {'r': r, 'p': p, 'n': n if n else 0}
    
    def test_cost_benefit_tradeoff(self):
        """
        H3: Costs should negatively predict utility.
        H4: Benefits should positively predict utility.
        RC Model: U(vote) = pB - C + ...
        """
        print("\n" + "="*60)
        print("HYPOTHESIS 3 & 4: COST-BENEFIT TRADEOFF")
        print("="*60)
        print("RC Model: U(vote) = pB - C + ...")
        
        r_cost, p_cost, n_cost = self.safe_corr('cost_score', 'voting_utility')
        r_benefit, p_benefit, n_benefit = self.safe_corr('benefit_score', 'voting_utility')
        
        if r_cost is not None:
            print(f"\nCost → Utility: r={r_cost:.3f}, p={p_cost:.4f} (N={n_cost})")
            if r_cost < 0 and p_cost < 0.05:
                print("✓ CONFIRMED: Higher costs → Lower utility (as predicted)")
            elif p_cost >= 0.05:
                print("⚠ NOT SIGNIFICANT: Cost relationship unclear")
            else:
                print("⚠ UNEXPECTED: Positive relationship (theory predicts negative)")
        
        if r_benefit is not None:
            print(f"\nBenefit → Utility: r={r_benefit:.3f}, p={p_benefit:.4f} (N={n_benefit})")
            if r_benefit > 0 and p_benefit < 0.05:
                print("✓ CONFIRMED: Higher benefits → Higher utility (as predicted)")
            elif p_benefit >= 0.05:
                print("⚠ NOT SIGNIFICANT: Benefit relationship unclear")
            else:
                print("⚠ UNEXPECTED: Negative relationship (theory predicts positive)")
        
        return {
            'cost_r': r_cost if r_cost else 0, 
            'cost_p': p_cost if p_cost else 1,
            'benefit_r': r_benefit if r_benefit else 0, 
            'benefit_p': p_benefit if p_benefit else 1
        }
    
    def test_social_influence_hypothesis(self):
        """
        H5: Social pressure should increase voting likelihood.
        Relevant for social nudge mechanisms.
        """
        print("\n" + "="*60)
        print("HYPOTHESIS 5: SOCIAL INFLUENCE (S component)")
        print("="*60)
        print("Tests susceptibility to social nudges")
        
        r, p, n = self.safe_corr('social_pressure_score', 'voting_utility')
        
        if r is not None:
            print(f"\nSocial Pressure → Utility: r = {r:.3f}, p = {p:.4f} (N = {n})")
            
            # High vs Low comparison
            social = self.df['social_pressure_score'].dropna()
            if len(social) > 20:
                median_social = social.median()
                high_social = self.df[self.df['social_pressure_score'] > median_social]['voting_utility'].dropna()
                low_social = self.df[self.df['social_pressure_score'] <= median_social]['voting_utility'].dropna()
                
                if len(high_social) >= 5 and len(low_social) >= 5:
                    t_stat, p_ttest = stats.ttest_ind(high_social, low_social)
                    
                    print(f"\nHigh Social Pressure (M={high_social.mean():.2f}, N={len(high_social)}) vs")
                    print(f"Low Social Pressure (M={low_social.mean():.2f}, N={len(low_social)})")
                    print(f"t-test: t = {t_stat:.2f}, p = {p_ttest:.4f}")
                    
                    if p_ttest < 0.05:
                        print("✓ SIGNIFICANT: Social pressure affects voting utility")
                    else:
                        print("✗ NOT SIGNIFICANT")
                    
                    return {'r': r, 'p': p, 't': t_stat, 'p_ttest': p_ttest}
        
        return {'r': r if r else 0, 'p': p if p else 1, 't': 0, 'p_ttest': 1}
    
    def test_trust_disillusionment_hypothesis(self):
        """
        H6: System trust should moderate other relationships.
        DDM: Trust affects decision threshold
        """
        print("\n" + "="*60)
        print("HYPOTHESIS 6: TRUST AS MODERATOR")
        print("="*60)
        print("DDM: Trust affects decision threshold")
        
        r, p, n = self.safe_corr('trust_score', 'voting_utility')
        
        if r is not None:
            print(f"\nTrust → Utility: r = {r:.3f}, p = {p:.4f} (N = {n})")
            
            # Test moderation
            trust = self.df['trust_score'].dropna()
            if len(trust) > 20:
                median_trust = trust.median()
                
                high_trust = self.df[self.df['trust_score'] > median_trust]
                low_trust = self.df[self.df['trust_score'] <= median_trust]
                
                r_ht, p_ht, n_ht = self.safe_corr('civic_duty_score', 'voting_utility')
                # For subgroups, need to filter first
                ht_data = high_trust[['civic_duty_score', 'voting_utility']].dropna()
                lt_data = low_trust[['civic_duty_score', 'voting_utility']].dropna()
                
                if len(ht_data) >= 10 and len(lt_data) >= 10:
                    r_ht, p_ht = stats.pearsonr(ht_data['civic_duty_score'], ht_data['voting_utility'])
                    r_lt, p_lt = stats.pearsonr(lt_data['civic_duty_score'], lt_data['voting_utility'])
                    
                    print(f"\nCivic Duty → Utility relationship:")
                    print(f"  High Trust: r = {r_ht:.3f}, p = {p_ht:.4f} (N = {len(ht_data)})")
                    print(f"  Low Trust: r = {r_lt:.3f}, p = {p_lt:.4f} (N = {len(lt_data)})")
                    
                    if abs(r_ht) > abs(r_lt) + 0.1:
                        print("  → Trust amplifies civic duty effects")
                    else:
                        print("  → No clear moderation effect")
        
        return {'r': r if r else 0, 'p': p if p else 1}
    
    def test_competitiveness_hypothesis(self):
        """
        H7: Electoral competitiveness should increase voting.
        RC Model: p (probability decisive) in pB term
        """
        print("\n" + "="*60)
        print("HYPOTHESIS 7: ELECTORAL COMPETITIVENESS (p in pB)")
        print("="*60)
        
        r, p, n = self.safe_corr('q12_competitiveness', 'voting_utility')
        
        if r is not None:
            # Note: Lower Q12 score = more competitive = should increase utility
            print(f"\nCompetitiveness → Utility: r={r:.3f}, p={p:.4f} (N={n})")
            print("(Note: Reverse coded - negative r means competitive → higher utility)")
            
            if r < 0 and p < 0.05:
                print("✓ CONFIRMED: More competitive elections → Higher voting utility")
            elif p >= 0.05:
                print("⚠ NOT SIGNIFICANT")
        
        return {'r': r if r else 0, 'p': p if p else 1}
    
    def test_incentive_effectiveness(self):
        """
        H8: Different incentives appeal to different archetypes.
        """
        print("\n" + "="*60)
        print("HYPOTHESIS 8: INCENTIVE PREFERENCES BY ARCHETYPE")
        print("="*60)
        
        # Create engagement groups
        engagement = self.df['engagement_score'].dropna()
        if len(engagement) < 20:
            print("⚠ Insufficient data for incentive analysis")
            return {'chi2': 0, 'p': 1}
        
        try:
            # Try to create 3 bins, but handle if data doesn't support it
            engagement_groups = pd.qcut(engagement, q=3, labels=False, duplicates='drop')
            unique_groups = sorted(engagement_groups.unique())
            
            # Map to labels
            group_labels = {}
            if len(unique_groups) >= 2:
                group_labels[unique_groups[0]] = 'Low'
                group_labels[unique_groups[-1]] = 'High'
                if len(unique_groups) >= 3:
                    group_labels[unique_groups[1]] = 'Medium'
            
            self.df.loc[engagement.index, 'engagement_group_num'] = engagement_groups
            
            # Cross-tabulation
            crosstab = pd.crosstab(
                self.df['engagement_group_num'], 
                self.df['q13_incentive']
            )
            
            print("\nIncentive Distribution by Engagement Level:")
            # Rename rows for display
            crosstab.index = [group_labels.get(idx, f'Group {idx}') for idx in crosstab.index]
            print(crosstab)
            
            # Chi-square test (need at least 2x2)
            if crosstab.shape[0] >= 2 and crosstab.shape[1] >= 2:
                chi2, p, dof, expected = stats.chi2_contingency(crosstab)
                
                print(f"\nχ² test: χ² = {chi2:.2f}, p = {p:.4f}")
                if p < 0.05:
                    print("✓ SIGNIFICANT: Incentive preferences vary by engagement")
                else:
                    print("✗ NOT SIGNIFICANT")
                
                return {'chi2': chi2, 'p': p}
            else:
                print("\n⚠ Insufficient cells for chi-square test")
                return {'chi2': 0, 'p': 1}
                
        except Exception as e:
            print(f"\n⚠ Could not complete incentive analysis: {e}")
            return {'chi2': 0, 'p': 1}
    
    def generate_hypothesis_report(self, save_path='hypothesis_tests'):
        """Run all hypothesis tests and generate report."""
        import os
        os.makedirs(save_path, exist_ok=True)
        
        print("\n" + "🔬" * 30)
        print("NEUROECONOMICS HYPOTHESIS TESTING")
        print("🔬" * 30)
        print(f"\nDataset: {len(self.df)} responses")
        
        results = {}
        
        results['h1_civic_duty'] = self.test_civic_duty_hypothesis()
        results['h2_habit'] = self.test_habit_formation_hypothesis()
        results['h3_h4_cost_benefit'] = self.test_cost_benefit_tradeoff()
        results['h5_social'] = self.test_social_influence_hypothesis()
        results['h6_trust'] = self.test_trust_disillusionment_hypothesis()
        results['h7_competitiveness'] = self.test_competitiveness_hypothesis()
        results['h8_incentives'] = self.test_incentive_effectiveness()
        
        print("\n" + "="*60)
        print("HYPOTHESIS TESTING SUMMARY")
        print("="*60)
        
        # Create summary visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        
        hypotheses = [
            'H1: Civic Duty',
            'H2: Habit Formation',
            'H3: Cost (negative)',
            'H4: Benefit (positive)',
            'H5: Social Influence',
            'H6: Trust Moderation',
            'H7: Competitiveness',
            'H8: Incentive Variance'
        ]
        
        # Extract p-values
        p_values = [
            results['h1_civic_duty'].get('p', 1),
            results['h2_habit'].get('p', 1),
            results['h3_h4_cost_benefit'].get('cost_p', 1),
            results['h3_h4_cost_benefit'].get('benefit_p', 1),
            results['h5_social'].get('p', 1),
            results['h6_trust'].get('p', 1),
            results['h7_competitiveness'].get('p', 1),
            results['h8_incentives'].get('p', 1)
        ]
        
        colors = ['green' if p < 0.05 else 'orange' if p < 0.10 else 'red' for p in p_values]
        
        # Use -log10(p) for visualization
        log_p_values = [-np.log10(p) if p > 0 else 0 for p in p_values]
        
        ax.barh(hypotheses, log_p_values, color=colors, alpha=0.7)
        ax.axvline(-np.log10(0.05), color='black', linestyle='--', linewidth=2, 
                  label='p=0.05 threshold')
        ax.axvline(-np.log10(0.10), color='gray', linestyle=':', linewidth=2, 
                  label='p=0.10 threshold')
        ax.set_xlabel('-log10(p-value)', fontsize=12)
        ax.set_title('Hypothesis Testing Results\n(Green=Significant, Orange=Marginal, Red=Not Significant)', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(f'{save_path}/hypothesis_summary.png', dpi=300, bbox_inches='tight')
        print(f"\n✓ Saved: {save_path}/hypothesis_summary.png")
        plt.close()
        
        print("\n✅ Hypothesis testing complete!")
        print("\n📊 Summary of Results:")
        for i, (hyp, p_val) in enumerate(zip(hypotheses, p_values)):
            sig = "✓ Significant" if p_val < 0.05 else "⚠ Marginal" if p_val < 0.10 else "✗ Not significant"
            print(f"  {hyp}: p={p_val:.4f} {sig}")
        
        print("\n🎯 Next steps:")
        print("  1. Use confirmed relationships for model calibration")
        print("  2. Focus on significant predictors in simulations")
        print("  3. Design nudges targeting validated mechanisms")
        
        return results


if __name__ == "__main__":
    print("Neuroeconomics Hypothesis Testing (Robust Version)")
    print("=" * 60)
    
    filepath = input("\nEnter path to your CSV file: ").strip()
    if not filepath:
        filepath = 'survey_responses_numeric_fixed.csv'
        print(f"Using: {filepath}")
    
    try:
        tester = HypothesisTester(filepath)
        results = tester.generate_hypothesis_report(save_path='hypothesis_tests')
        
        print("\n🎉 Success! Check hypothesis_tests/ folder for results")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()