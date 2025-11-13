"""
Agent population generation from configuration
"""

import numpy as np
from typing import Dict, List
import json


class AgentGenerator:
    """Generate voter populations from configuration"""
    
    def __init__(self, config: Dict):
        """
        Initialize generator with configuration
        
        Args:
            config: Full configuration dictionary
        """
        self.config = config
        self.feature_definitions = config.get('feature_definitions', {})
    
    def generate_population(self, scenario_name: str) -> List[Dict[str, float]]:
        """
        Generate population for a specific scenario
        
        Args:
            scenario_name: Name of scenario in config
        
        Returns:
            List of dictionaries, each representing a voter's features
        """
        # Find scenario
        scenario = self._get_scenario(scenario_name)
        if scenario is None:
            raise ValueError(f"Scenario '{scenario_name}' not found in config")
        
        # Get generation rules and context
        rules = scenario['agent_generation_rules']
        context = scenario['global_context']
        pop_size = rules['population_size']
        
        # Generate agents
        agents = []
        for i in range(pop_size):
            agent = self._generate_single_agent(i, rules, context)
            agents.append(agent)
        
        return agents
    
    def _get_scenario(self, scenario_name: str) -> Dict:
        """Find scenario by name"""
        scenarios = self.config.get('simulation_scenarios', [])
        for scenario in scenarios:
            if scenario['scenario_name'] == scenario_name:
                return scenario
        return None
    
    def _generate_single_agent(self, agent_id: int, rules: Dict, 
                               context: Dict) -> Dict[str, float]:
        """
        Generate a single agent's features
        
        Args:
            agent_id: Unique ID
            rules: Agent generation rules
            context: Global context
        
        Returns:
            Dictionary of agent features
        """
        agent = {'voter_id': f"agent_{agent_id}"}
        
        # Generate each feature
        for feature_name, generation_spec in rules.items():
            if feature_name == 'population_size':
                continue
            
            value = self._generate_feature(generation_spec)
            agent[feature_name] = value
        
        # Add global context features
        agent.update(context)
        
        # Generate missing features with defaults if needed
        agent = self._add_default_features(agent)
        
        return agent
    
    def _generate_feature(self, spec: Dict) -> float:
        """
        Generate a single feature value based on specification
        
        Args:
            spec: Feature generation specification
        
        Returns:
            Feature value
        """
        method = spec['method']
        params = spec['parameters']
        
        if method == 'beta_distribution':
            alpha, beta = params
            return np.random.beta(alpha, beta)
        
        elif method == 'beta_distribution_from_proxy':
            proxy_value = params['proxy_value']
            high_params = params['high_skew_params']
            low_params = params['low_skew_params']
            
            # Use proxy value as probability to assign to high group
            if np.random.random() < proxy_value:
                return np.random.beta(*high_params)
            else:
                return np.random.beta(*low_params)
        
        elif method == 'binomial_draw_normalized':
            n = params['num_elections']
            p = params['probability']
            n_votes = np.random.binomial(n, p)
            return n_votes / n  # Normalize to 0-1
        
        elif method == 'probabilistic_distribution':
            # For education based on literacy rate
            literacy_rate = params['literacy_rate']
            # Generate from a Beta distribution shaped by literacy
            alpha = literacy_rate * 10
            beta = (1 - literacy_rate) * 10
            return np.random.beta(max(alpha, 0.5), max(beta, 0.5))
        
        elif method == 'probabilistic_assignment':
            # Binary assignment (e.g., urban/rural)
            prob = params.get('probability_urban', 0.5)
            return 1.0 if np.random.random() < prob else 0.0
        
        else:
            raise ValueError(f"Unknown generation method: {method}")
    
    def _add_default_features(self, agent: Dict) -> Dict:
        """
        Add default values for features not specified in config
        
        Args:
            agent: Partial agent dictionary
        
        Returns:
            Complete agent dictionary
        """
        # Required features with defaults
        defaults = {
            'age': np.random.randint(18, 80),
            'issue_salience': 0.5,
            'partisan_identity_strength': agent.get('partisan_identity_strength', 0.5),
            'perceived_integrity': 0.6,
            'personality_match_candidate': 0.5
        }
        
        for feature, default_value in defaults.items():
            if feature not in agent:
                agent[feature] = default_value
        
        return agent
    
    @staticmethod
    def load_config_from_file(filepath: str) -> Dict:
        """
        Load configuration from JSON file
        
        Args:
            filepath: Path to JSON config file
        
        Returns:
            Configuration dictionary
        """
        with open(filepath, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def save_population_to_file(population: List[Dict], filepath: str):
        """
        Save generated population to file
        
        Args:
            population: List of agent dictionaries
            filepath: Output file path
        """
        import pandas as pd
        df = pd.DataFrame(population)
        df.to_csv(filepath, index=False)
        print(f"Saved {len(population)} agents to {filepath}")