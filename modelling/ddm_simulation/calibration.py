"""
Parameter calibration for DDM using optimization
"""

import numpy as np
from scipy.optimize import minimize, differential_evolution
from typing import Dict, List, Tuple
from ddm_model import DDMParameters, DDMVoter, DDMPopulation
from agent_generator import AgentGenerator
import copy
import pandas as pd

class DDMCalibrator:
    """Calibrate DDM parameters to match target turnout"""
    
    def __init__(self, config: Dict, calibration_scenario: str):
        """
        Initialize calibrator
        
        Args:
            config: Configuration dictionary
            calibration_scenario: Scenario to calibrate on (e.g., 'Thiruvananthapuram')
        """
        self.config = config
        self.scenario_name = calibration_scenario
        
        # Load scenario
        self.scenario = self._find_scenario(calibration_scenario)
        if self.scenario is None:
            raise ValueError(f"Scenario '{calibration_scenario}' not found")
        
        self.target_turnout = self.scenario['validation_target']['value']
        
        # Generate population
        generator = AgentGenerator(config)
        self.agent_features = generator.generate_population(calibration_scenario)
        
        print(f"Calibrator initialized for {calibration_scenario}")
        print(f"Target turnout: {self.target_turnout:.4f}")
        print(f"Population size: {len(self.agent_features)}")
    
    def _find_scenario(self, name: str) -> Dict:
        """Find scenario by name"""
        for scenario in self.config.get('simulation_scenarios', []):
            if scenario['scenario_name'] == name:
                return scenario
        return None
    
    def objective_function(self, params_array: np.ndarray) -> float:
        """
        Objective function: squared error between simulated and target turnout
        
        Args:
            params_array: Array of parameters to optimize
        
        Returns:
            Loss value (lower is better)
        """
        # Unpack parameters
        ddm_params = self._array_to_params(params_array)
        
        # Create voters with these parameters
        voters = [
            DDMVoter(f['voter_id'], f, ddm_params)
            for f in self.agent_features
        ]
        
        population = DDMPopulation(voters)
        
        # Simulate election
        results = population.simulate_election(use_analytical=True)
        simulated_turnout = results['turnout_rate']
        
        # Squared error
        error = (simulated_turnout - self.target_turnout) ** 2
        
        return error
    
    def _array_to_params(self, params_array: np.ndarray) -> DDMParameters:
        """
        Convert parameter array to DDMParameters object
        
        Args:
            params_array: Array of parameters
        
        Returns:
            DDMParameters object
        """
        params = DDMParameters()
        
        # Map array elements to parameters
        # Order: [drift_base, threshold_base, beta_D, beta_H, beta_S, beta_C]
        params.drift_rate_base = params_array[0]
        params.threshold_base = params_array[1]
        params.beta_D = params_array[2]
        params.beta_H = params_array[3]
        params.beta_S = params_array[4]
        params.beta_C = params_array[5]
        
        return params
    
    def _params_to_array(self, params: DDMParameters) -> np.ndarray:
        """
        Convert DDMParameters to array
        
        Args:
            params: DDMParameters object
        
        Returns:
            Parameter array
        """
        return np.array([
            params.drift_rate_base,
            params.threshold_base,
            params.beta_D,
            params.beta_H,
            params.beta_S,
            params.beta_C
        ])
    
    def calibrate(self, method: str = 'nelder-mead', 
                  initial_params: DDMParameters = None) -> Tuple[DDMParameters, Dict]:
        """
        Calibrate parameters using optimization
        
        Args:
            method: Optimization method ('nelder-mead', 'powell', 'differential_evolution')
            initial_params: Initial parameter guess
        
        Returns:
            Tuple of (optimized_params, optimization_info)
        """
        print(f"\nStarting calibration using {method}...")
        
        if initial_params is None:
            initial_params = DDMParameters()
        
        x0 = self._params_to_array(initial_params)
        
        # Parameter bounds
        bounds = [
            (0.01, 0.5),     # drift_base
            (0.5, 4.0),      # threshold_base
            (0.0, 0.5),      # beta_D
            (0.0, 0.5),      # beta_H
            (0.0, 0.5),      # beta_S
            (-0.5, 0.0)      # beta_C (negative)
        ]
        
        if method == 'differential_evolution':
            # Global optimization
            result = differential_evolution(
                self.objective_function,
                bounds=bounds,
                maxiter=100,
                popsize=15,
                seed=42,
                disp=True
            )
        else:
            # Local optimization
            result = minimize(
                self.objective_function,
                x0=x0,
                method=method,
                bounds=bounds,
                options={'maxiter': 200, 'disp': True}
            )
        
        # Convert result back to parameters
        optimal_params = self._array_to_params(result.x)
        
        # Final simulation to verify
        voters = [
            DDMVoter(f['voter_id'], f, optimal_params)
            for f in self.agent_features
        ]
        population = DDMPopulation(voters)
        final_results = population.simulate_election(use_analytical=True)
        
        info = {
            'success': result.success,
            'final_loss': result.fun,
            'iterations': result.nit if hasattr(result, 'nit') else result.nfev,
            'simulated_turnout': final_results['turnout_rate'],
            'target_turnout': self.target_turnout,
            'absolute_error': abs(final_results['turnout_rate'] - self.target_turnout)
        }
        
        print(f"\nCalibration complete!")
        print(f"  Final loss: {info['final_loss']:.6f}")
        print(f"  Simulated turnout: {info['simulated_turnout']:.4f}")
        print(f"  Target turnout: {info['target_turnout']:.4f}")
        print(f"  Absolute error: {info['absolute_error']:.4f}")
        
        return optimal_params, info
    
    def validate(self, params: DDMParameters, validation_scenario: str) -> Dict:
        """
        Validate calibrated parameters on a different scenario
        
        Args:
            params: Calibrated parameters
            validation_scenario: Name of validation scenario
        
        Returns:
            Validation results
        """
        print(f"\n{'='*60}")
        print(f"Validating on {validation_scenario}...")
        print(f"{'='*60}")
        
        # Load validation scenario
        val_scenario = self._find_scenario(validation_scenario)
        if val_scenario is None:
            raise ValueError(f"Validation scenario '{validation_scenario}' not found")
        
        val_target = val_scenario['validation_target']['value']
        
        # Generate validation population
        generator = AgentGenerator(self.config)
        val_features = generator.generate_population(validation_scenario)
        
        # Create voters
        voters = [
            DDMVoter(f['voter_id'], f, params)
            for f in val_features
        ]
        
        population = DDMPopulation(voters)
        results = population.simulate_election(use_analytical=True)
        
        simulated = results['turnout_rate']
        error = abs(simulated - val_target)
        
        print(f"\nValidation Results:")
        print(f"  Simulated turnout: {simulated:.4f}")
        print(f"  Target turnout:    {val_target:.4f}")
        print(f"  Absolute error:    {error:.4f}")
        print(f"  Relative error:    {error/val_target*100:.2f}%")
        
        return {
            'scenario': validation_scenario,
            'simulated_turnout': simulated,
            'target_turnout': val_target,
            'absolute_error': error,
            'relative_error': error / val_target
        }
    
    def grid_search(self, param_ranges: Dict, n_points: int = 5) -> pd.DataFrame:
        """
        Perform grid search over parameter space
        
        Args:
            param_ranges: Dict with parameter names and (min, max) tuples
            n_points: Number of points per parameter
        
        Returns:
            DataFrame with grid search results
        """
        import pandas as pd
        from itertools import product
        
        # Generate grid
        param_names = list(param_ranges.keys())
        param_grids = [
            np.linspace(param_ranges[name][0], param_ranges[name][1], n_points)
            for name in param_names
        ]
        
        results = []
        total_combinations = n_points ** len(param_names)
        
        print(f"Running grid search with {total_combinations} combinations...")
        
        for i, param_values in enumerate(product(*param_grids)):
            # Create parameters
            params = DDMParameters()
            for name, value in zip(param_names, param_values):
                setattr(params, name, value)
            
            # Evaluate
            voters = [
                DDMVoter(f['voter_id'], f, params)
                for f in self.agent_features
            ]
            population = DDMPopulation(voters)
            sim_results = population.simulate_election(use_analytical=True)
            
            turnout = sim_results['turnout_rate']
            error = abs(turnout - self.target_turnout)
            
            result = {name: value for name, value in zip(param_names, param_values)}
            result['turnout'] = turnout
            result['error'] = error
            
            results.append(result)
            
            if (i + 1) % 10 == 0:
                print(f"  Completed {i+1}/{total_combinations}...")
        
        df = pd.DataFrame(results)
        df = df.sort_values('error')
        
        print(f"\nBest parameters:")
        print(df.iloc[0])
        
        return df