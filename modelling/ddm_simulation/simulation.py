"""
Simulation orchestration for DDM voter model
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from ddm_model import DDMVoter, DDMPopulation, DDMParameters, load_ddm_parameters_from_config
from agent_generator import AgentGenerator


class DDMSimulation:
    """Orchestrates DDM simulation for voter turnout"""
    
    def __init__(self, config: Dict, scenario_name: str):
        """
        Initialize simulation
        
        Args:
            config: Configuration dictionary
            scenario_name: Which scenario to simulate
        """
        self.config = config
        self.scenario_name = scenario_name
        
        # Load scenario
        self.scenario = self._find_scenario(scenario_name)
        if self.scenario is None:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        # Load DDM parameters
        self.ddm_params = load_ddm_parameters_from_config(config)
        
        # Generate population
        self.generator = AgentGenerator(config)
        self.agent_features = self.generator.generate_population(scenario_name)
        
        # Create DDM voters
        self.voters = self._create_ddm_voters()
        self.population = DDMPopulation(self.voters)
        
        print(f"Initialized simulation for {scenario_name}")
        print(f"Population size: {len(self.voters)}")
        print(f"Target turnout: {self.scenario['validation_target']['value']:.4f}")
    
    def _find_scenario(self, name: str) -> Optional[Dict]:
        """Find scenario by name"""
        for scenario in self.config.get('simulation_scenarios', []):
            if scenario['scenario_name'] == name:
                return scenario
        return None
    
    def _create_ddm_voters(self) -> List[DDMVoter]:
        """Create DDM voter objects from agent features"""
        voters = []
        for features in self.agent_features:
            voter_id = features['voter_id']
            voter = DDMVoter(voter_id, features, self.ddm_params)
            voters.append(voter)
        return voters
    
    def run_baseline(self, n_simulations: int = 1000, 
                    use_analytical: bool = True) -> Dict:
        """
        Run baseline simulation (no nudges)
        
        Args:
            n_simulations: Number of Monte Carlo runs (if not analytical)
            use_analytical: Use analytical solution vs simulation
        
        Returns:
            Results dictionary
        """
        print(f"\nRunning baseline simulation...")
        print(f"Method: {'Analytical' if use_analytical else f'Monte Carlo ({n_simulations} runs)'}")
        
        results = self.population.simulate_election(
            n_simulations=n_simulations,
            use_analytical=use_analytical
        )
        
        target_turnout = self.scenario['validation_target']['value']
        simulated_turnout = results['turnout_rate']
        error = abs(simulated_turnout - target_turnout)
        
        print(f"\nResults:")
        print(f"  Simulated turnout: {simulated_turnout:.4f}")
        print(f"  Target turnout:    {target_turnout:.4f}")
        print(f"  Absolute error:    {error:.4f}")
        print(f"  Relative error:    {error/target_turnout*100:.2f}%")
        
        results['target_turnout'] = target_turnout
        results['error'] = error
        results['relative_error'] = error / target_turnout
        
        return results
    
    def run_nudge_experiment(self, nudge_type: str, nudge_params: Dict,
                            treatment_fraction: float = 0.5,
                            n_simulations: int = 1000,
                            use_analytical: bool = True) -> Dict:
        """
        Run experiment with nudge treatment
        
        Args:
            nudge_type: Type of nudge
            nudge_params: Nudge parameters
            treatment_fraction: Fraction of population to treat
            n_simulations: Monte Carlo runs
            use_analytical: Use analytical solution
        
        Returns:
            Results dictionary with treatment effects
        """
        print(f"\nRunning nudge experiment: {nudge_type}")
        print(f"Treatment fraction: {treatment_fraction}")
        
        # Baseline (control group)
        n_control = int(len(self.voters) * (1 - treatment_fraction))
        control_voters = self.voters[:n_control]
        control_pop = DDMPopulation(control_voters)
        
        control_results = control_pop.simulate_election(
            n_simulations=n_simulations,
            use_analytical=use_analytical
        )
        
        # Treatment group
        treatment_voters = self.voters[n_control:]
        treatment_pop = DDMPopulation(treatment_voters)
        
        # Apply nudge
        nudge_assignment = {
            v.voter_id: {'type': nudge_type, 'params': nudge_params}
            for v in treatment_voters
        }
        treatment_pop.apply_nudges(nudge_assignment)
        
        treatment_results = treatment_pop.simulate_election(
            n_simulations=n_simulations,
            use_analytical=use_analytical
        )
        
        # Compute treatment effect
        ate = treatment_results['turnout_rate'] - control_results['turnout_rate']
        
        print(f"\nResults:")
        print(f"  Control turnout:    {control_results['turnout_rate']:.4f}")
        print(f"  Treatment turnout:  {treatment_results['turnout_rate']:.4f}")
        print(f"  Treatment effect:   {ate:.4f} ({ate/control_results['turnout_rate']*100:.2f}%)")
        
        return {
            'nudge_type': nudge_type,
            'nudge_params': nudge_params,
            'control_turnout': control_results['turnout_rate'],
            'treatment_turnout': treatment_results['turnout_rate'],
            'average_treatment_effect': ate,
            'relative_effect': ate / control_results['turnout_rate'],
            'control_results': control_results,
            'treatment_results': treatment_results
        }
    
    def run_hypothesis_test(self, hypothesis_name: str) -> Dict:
        """
        Run specific hypothesis test
        
        Args:
            hypothesis_name: e.g., 'HN1', 'HN2', etc.
        
        Returns:
            Test results
        """
        hypothesis_configs = {
            'HN1': {
                'description': 'Monetary lottery more effective for low civic duty',
                'nudge_type': 'monetary',
                'nudge_params': {'lottery_value': 0.3, 'lottery_prob': 0.01},
                                 'nudge_params': {'lottery_value': 0.3, 'lottery_prob': 0.01},
                'test_type': 'stratified'
            },
            'HN2': {
                'description': 'Social norm more effective than informational',
                'nudge_type': 'comparison',
                'nudges': ['social_norm', 'competitiveness'],
                'test_type': 'comparison'
            },
            'HN3': {
                'description': 'Identity framing most effective for moderate civic duty',
                'nudge_type': 'identity',
                'nudge_params': {'identity_strength': 0.7, 'frame_strength': 1.0},
                'test_type': 'stratified'
            },
            'HN6': {
                'description': 'Competitiveness info affects high efficacy voters',
                'nudge_type': 'competitiveness',
                'nudge_params': {'competitiveness_info': 0.8},
                'test_type': 'stratified'
            }
        }
        
        if hypothesis_name not in hypothesis_configs:
            raise ValueError(f"Unknown hypothesis: {hypothesis_name}")
        
        h_config = hypothesis_configs[hypothesis_name]
        print(f"\n{'='*60}")
        print(f"Testing {hypothesis_name}: {h_config['description']}")
        print(f"{'='*60}")
        
        if h_config['test_type'] == 'stratified':
            return self._test_stratified_effect(h_config)
        elif h_config['test_type'] == 'comparison':
            return self._test_nudge_comparison(h_config)
        else:
            raise ValueError(f"Unknown test type: {h_config['test_type']}")
    
    def _test_stratified_effect(self, config: Dict) -> Dict:
        """
        Test nudge effect stratified by feature (e.g., civic duty)
        
        Args:
            config: Hypothesis configuration
        
        Returns:
            Stratified results
        """
        # Determine stratification variable
        if 'HN1' in config['description'] or 'HN3' in config['description']:
            strata_var = 'civic_duty'
            thresholds = [0, 0.33, 0.67, 1.0]
            labels = ['Low', 'Medium', 'High']
        else:
            strata_var = 'education_normalized'
            thresholds = [0, 0.5, 1.0]
            labels = ['Low', 'High']
        
        results = {}
        
        for i in range(len(thresholds) - 1):
            stratum_label = labels[i]
            lower = thresholds[i]
            upper = thresholds[i + 1]
            
            # Filter voters in this stratum
            stratum_voters = [
                v for v in self.voters
                if lower <= v.features[strata_var] < upper
            ]
            
            if len(stratum_voters) == 0:
                continue
            
            print(f"\n--- Stratum: {stratum_label} {strata_var} [{lower:.2f}, {upper:.2f}) ---")
            print(f"    N = {len(stratum_voters)}")
            
            # Control (no nudge)
            n_control = len(stratum_voters) // 2
            control = DDMPopulation(stratum_voters[:n_control])
            control_results = control.simulate_election(use_analytical=True)
            
            # Treatment
            treatment = DDMPopulation(stratum_voters[n_control:])
            nudge_assignment = {
                v.voter_id: {'type': config['nudge_type'], 'params': config['nudge_params']}
                for v in stratum_voters[n_control:]
            }
            treatment.apply_nudges(nudge_assignment)
            treatment_results = treatment.simulate_election(use_analytical=True)
            
            effect = treatment_results['turnout_rate'] - control_results['turnout_rate']
            
            print(f"    Control:   {control_results['turnout_rate']:.4f}")
            print(f"    Treatment: {treatment_results['turnout_rate']:.4f}")
            print(f"    Effect:    {effect:.4f}")
            
            results[stratum_label] = {
                'control_turnout': control_results['turnout_rate'],
                'treatment_turnout': treatment_results['turnout_rate'],
                'effect': effect,
                'n': len(stratum_voters)
            }
        
        return results
    
    def _test_nudge_comparison(self, config: Dict) -> Dict:
        """
        Compare effectiveness of two nudges
        
        Args:
            config: Hypothesis configuration
        
        Returns:
            Comparison results
        """
        nudge_types = config['nudges']
        
        # Define nudge parameters
        nudge_params_map = {
            'social_norm': {'revealed_turnout': 0.75, 'prior_belief': 0.5},
            'competitiveness': {'competitiveness_info': 0.8}
        }
        
        # Split into three groups
        n_per_group = len(self.voters) // 3
        
        # Control
        control_voters = self.voters[:n_per_group]
        control_pop = DDMPopulation(control_voters)
        control_results = control_pop.simulate_election(use_analytical=True)
        
        results = {
            'control': {
                'turnout': control_results['turnout_rate']
            }
        }
        
        # Test each nudge
        for i, nudge_type in enumerate(nudge_types):
            start_idx = n_per_group * (i + 1)
            end_idx = n_per_group * (i + 2) if i == 0 else len(self.voters)
            
            treatment_voters = self.voters[start_idx:end_idx]
            treatment_pop = DDMPopulation(treatment_voters)
            
            nudge_assignment = {
                v.voter_id: {'type': nudge_type, 'params': nudge_params_map[nudge_type]}
                for v in treatment_voters
            }
            treatment_pop.apply_nudges(nudge_assignment)
            
            treatment_results = treatment_pop.simulate_election(use_analytical=True)
            effect = treatment_results['turnout_rate'] - control_results['turnout_rate']
            
            print(f"\n{nudge_type.upper()}:")
            print(f"  Turnout: {treatment_results['turnout_rate']:.4f}")
            print(f"  Effect:  {effect:.4f}")
            
            results[nudge_type] = {
                'turnout': treatment_results['turnout_rate'],
                'effect': effect
            }
        
        # Determine winner
        effects = {k: v['effect'] for k, v in results.items() if k != 'control'}
        winner = max(effects, key=effects.get)
        
        print(f"\n>>> Winner: {winner} (effect = {effects[winner]:.4f})")
        results['winner'] = winner
        
        return results
    
    def export_results(self, results: Dict, filepath: str):
        """
        Export simulation results to file
        
        Args:
            results: Results dictionary
            filepath: Output file path
        """
        import json
        
        # Convert numpy types to Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            else:
                return obj
        
        results_clean = convert_types(results)
        
        with open(filepath, 'w') as f:
            json.dump(results_clean, f, indent=2)
        
        print(f"\nResults exported to {filepath}")
    
    def get_population_diagnostics(self) -> pd.DataFrame:
        """
        Get diagnostic information for all voters
        
        Returns:
            DataFrame with voter diagnostics
        """
        diagnostics = [v.get_diagnostics() for v in self.voters]
        df = pd.DataFrame(diagnostics)
        return df