"""
Main entry point for DDM voter turnout simulation
"""

import json
import argparse
from pathlib import Path
from ddm_model import DDMParameters
from agent_generator import AgentGenerator
from simulation import DDMSimulation
from calibration import DDMCalibrator
from visualization import DDMVisualizer


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)


def save_parameters(params: DDMParameters, filepath: str):
    """Save calibrated parameters to JSON"""
    params_dict = {
        'drift_rate_base': params.drift_rate_base,
        'threshold_base': params.threshold_base,
        'sigma_base': params.sigma_base,
        'drift_components': {
            'beta_D': params.beta_D,
            'beta_PI': params.beta_PI,
            'beta_IS': params.beta_IS,
            'beta_S': params.beta_S,
            'beta_H': params.beta_H,
            'beta_C': params.beta_C,
            'beta_EC': params.beta_EC,
            'beta_OC': params.beta_OC
        },
        'threshold_modifiers': {
            'gamma_risk': params.gamma_risk,
            'gamma_edu': params.gamma_edu,
            'gamma_OC': params.gamma_OC
        },
        'starting_point_biases': {
            'alpha_H': params.alpha_H,
            'alpha_PI': params.alpha_PI,
            'alpha_D': params.alpha_D
        }
    }
    
    with open(filepath, 'w') as f:
        json.dump(params_dict, f, indent=2)
    
    print(f"Parameters saved to {filepath}")


def run_baseline_simulation(config_path: str, scenario: str, output_dir: str):
    """Run baseline simulation without nudges"""
    print("\n" + "="*70)
    print("BASELINE SIMULATION")
    print("="*70)
    
    config = load_config(config_path)
    sim = DDMSimulation(config, scenario)
    
    # Run simulation
    results = sim.run_baseline(use_analytical=True)
    
    # Export results
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    sim.export_results(results, str(output_path / f"baseline_{scenario}.json"))
    
    # Visualizations
    viz = DDMVisualizer()
    diagnostics = sim.get_population_diagnostics()
    viz.plot_population_distribution(
        diagnostics, 
        save_path=str(output_path / f"population_dist_{scenario}.png")
    )
    
    return results


def run_calibration(config_path: str, calibration_scenario: str, 
                   validation_scenario: str, output_dir: str):
    """Run parameter calibration"""
    print("\n" + "="*70)
    print("PARAMETER CALIBRATION")
    print("="*70)
    
    config = load_config(config_path)
    calibrator = DDMCalibrator(config, calibration_scenario)
    
    # Calibrate
    optimal_params, info = calibrator.calibrate(method='differential_evolution')
    
    # Save parameters
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    save_parameters(optimal_params, str(output_path / "calibrated_params.json"))
    
    # Validate
    validation_results = calibrator.validate(optimal_params, validation_scenario)
    
    # Save validation results
    calibrator_results = {
        'calibration': info,
        'validation': validation_results,
        'parameters': {
            'drift_rate_base': optimal_params.drift_rate_base,
            'threshold_base': optimal_params.threshold_base,
            'beta_D': optimal_params.beta_D,
            'beta_H': optimal_params.beta_H,
            'beta_S': optimal_params.beta_S,
            'beta_C': optimal_params.beta_C
        }
    }
    
    with open(output_path / "calibration_results.json", 'w') as f:
        json.dump(calibrator_results, f, indent=2)
    
    return optimal_params, validation_results


def run_nudge_experiments(config_path: str, scenario: str, output_dir: str):
    """Run all nudge experiments"""
    print("\n" + "="*70)
    print("NUDGE EXPERIMENTS")
    print("="*70)
    
    config = load_config(config_path)
    sim = DDMSimulation(config, scenario)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    viz = DDMVisualizer()
    
    # Define nudges to test
    nudges = {
        'monetary': {'lottery_value': 0.3, 'lottery_prob': 0.01},
        'social_norm': {'revealed_turnout': 0.75, 'prior_belief': 0.5},
        'identity': {'identity_strength': 0.7, 'frame_strength': 1.0},
        'competitiveness': {'competitiveness_info': 0.8}
    }
    
    all_results = {}
    
    for nudge_type, nudge_params in nudges.items():
        print(f"\n--- Testing {nudge_type.upper()} nudge ---")
        
        results = sim.run_nudge_experiment(
            nudge_type=nudge_type,
            nudge_params=nudge_params,
            treatment_fraction=0.5,
            use_analytical=True
        )
        
        all_results[nudge_type] = results
        
        # Visualize
        viz.plot_nudge_effects(
            results,
            save_path=str(output_path / f"nudge_{nudge_type}.png")
        )
    
    # Export all results
    with open(output_path / "nudge_experiments.json", 'w') as f:
        # Convert for JSON serialization
        import numpy as np
        def convert(obj):
            if isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(x) for x in obj]
            return obj
        
        json.dump(convert(all_results), f, indent=2)
    
    return all_results


def run_hypothesis_tests(config_path: str, scenario: str, output_dir: str):
    """Run hypothesis tests"""
    print("\n" + "="*70)
    print("HYPOTHESIS TESTING")
    print("="*70)
    
    config = load_config(config_path)
    sim = DDMSimulation(config, scenario)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    viz = DDMVisualizer()
    
    hypotheses = ['HN1', 'HN2', 'HN3', 'HN6']
    all_results = {}
    
    for h_name in hypotheses:
        print(f"\n{'='*60}")
        print(f"Testing {h_name}")
        print(f"{'='*60}")
        
        try:
            results = sim.run_hypothesis_test(h_name)
            all_results[h_name] = results
            
            # Visualize if stratified
            if isinstance(results, dict) and 'Low' in results:
                viz.plot_stratified_effects(
                    results,
                    h_name,
                    save_path=str(output_path / f"hypothesis_{h_name}.png")
                )
        except Exception as e:
            print(f"Error testing {h_name}: {e}")
            all_results[h_name] = {'error': str(e)}
    
    # Export results
    with open(output_path / "hypothesis_tests.json", 'w') as f:
        import numpy as np
        def convert(obj):
            if isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(x) for x in obj]
            return obj
        
        json.dump(convert(all_results), f, indent=2)
    
    return all_results


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='DDM Voter Turnout Simulation')
    parser.add_argument('--config', type=str, required=True,
                       help='Path to configuration JSON file')
    parser.add_argument('--mode', type=str, required=True,
                       choices=['baseline', 'calibrate', 'nudges', 'hypotheses', 'all'],
                       help='Simulation mode')
    parser.add_argument('--scenario', type=str, default='Thiruvananthapuram, Kerala (2019)',
                       help='Scenario to simulate')
    parser.add_argument('--calibration-scenario', type=str, 
                       default='Thiruvananthapuram, Kerala (2019)',
                       help='Scenario for calibration')
    parser.add_argument('--validation-scenario', type=str,
                       default='Shravasti, Uttar Pradesh (2019)',
                       help='Scenario for validation')
    parser.add_argument('--output-dir', type=str, default='./results',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("DDM VOTER TURNOUT SIMULATION")
    print("="*70)
    print(f"Config: {args.config}")
    print(f"Mode: {args.mode}")
    print(f"Output: {args.output_dir}")
    print("="*70)
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    if args.mode == 'baseline':
        run_baseline_simulation(args.config, args.scenario, args.output_dir)
    
    elif args.mode == 'calibrate':
        run_calibration(args.config, args.calibration_scenario, 
                       args.validation_scenario, args.output_dir)
    
    elif args.mode == 'nudges':
        run_nudge_experiments(args.config, args.scenario, args.output_dir)
    
    elif args.mode == 'hypotheses':
        run_hypothesis_tests(args.config, args.scenario, args.output_dir)
    
    elif args.mode == 'all':
        # Run complete workflow
        print("\n" + "="*70)
        print("RUNNING COMPLETE WORKFLOW")
        print("="*70)
        
        # 1. Calibration
        optimal_params, val_results = run_calibration(
            args.config, args.calibration_scenario, 
            args.validation_scenario, args.output_dir
        )
        
        # 2. Baseline with calibrated parameters
        # Update config with calibrated parameters
        config = load_config(args.config)
        config['model_calibration_parameters']['drift_diffusion_model'] = {
            'drift_rate_base': optimal_params.drift_rate_base,
            'threshold_base': optimal_params.threshold_base,
            'drift_components': {
                'beta_D': optimal_params.beta_D,
                'beta_H': optimal_params.beta_H,
                'beta_S': optimal_params.beta_S,
                'beta_C': optimal_params.beta_C
            }
        }
        
        # Save updated config
        updated_config_path = Path(args.output_dir) / "calibrated_config.json"
        with open(updated_config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # 3. Run baseline
        run_baseline_simulation(str(updated_config_path), args.scenario, args.output_dir)
        
        # 4. Nudge experiments
        run_nudge_experiments(str(updated_config_path), args.scenario, args.output_dir)
        
        # 5. Hypothesis tests
        run_hypothesis_tests(str(updated_config_path), args.scenario, args.output_dir)
        
        print("\n" + "="*70)
        print("COMPLETE WORKFLOW FINISHED")
        print(f"All results saved to: {args.output_dir}")
        print("="*70)
    
    print("\nSimulation complete!")


if __name__ == "__main__":
    main()