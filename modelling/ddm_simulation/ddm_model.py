"""
Drift-Diffusion Model for Voter Turnout
Implements sequential evidence accumulation framework
"""

import numpy as np
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import warnings


@dataclass
class DDMParameters:
    """Parameter container for DDM"""
    # Drift rate components
    beta_D: float = 0.15      # Civic duty
    beta_PI: float = 0.12     # Partisan identity (not in minimal config)
    beta_IS: float = 0.10     # Issue salience (not in minimal config)
    beta_S: float = 0.20      # Social pressure
    beta_H: float = 0.18      # Habit
    beta_C: float = -0.14     # Cost (negative)
    beta_EC: float = 0.08     # Electoral competitiveness
    beta_OC: float = 0.05     # Overconfidence
    
    # Base parameters
    drift_rate_base: float = 0.1
    threshold_base: float = 2.0
    sigma_base: float = 0.2
    
    # Threshold modifiers
    gamma_risk: float = 0.4
    gamma_edu: float = 0.3
    gamma_OC: float = 0.2
    
    # Starting point biases
    alpha_H: float = 0.25
    alpha_PI: float = 0.10
    alpha_D: float = 0.10
    
    # Noise modifiers
    nu_edu: float = 0.3
    nu_OC: float = 0.15


class DDMVoter:
    """
    Drift-Diffusion Model voter agent
    
    Attributes:
        voter_id: Unique identifier
        features: Dictionary of voter features
        ddm_params: DDM parameters object
        mu: Computed drift rate
        a: Computed decision threshold
        z: Computed starting point
        sigma: Computed diffusion coefficient
    """
    
    def __init__(self, voter_id: str, features: Dict[str, float], 
                 ddm_params: DDMParameters):
        """
        Initialize DDM voter
        
        Args:
            voter_id: Unique identifier
            features: Dictionary with voter characteristics
            ddm_params: DDM parameters
        """
        self.voter_id = voter_id
        self.features = features
        self.params = ddm_params
        
        # Validate features
        self._validate_features()
        
        # Compute DDM parameters
        self.mu = self._compute_drift_rate()
        self.a = self._compute_threshold()
        self.z = self._compute_starting_point()
        self.sigma = self._compute_diffusion_coefficient()
        
        # Storage for simulation results
        self.last_decision = None
        self.last_decision_time = None
    
    def _validate_features(self):
        """Ensure all required features are present"""
        required = [
            'civic_duty', 'habit_strength', 'social_pressure_sensitivity',
            'risk_aversion', 'education_normalized', 'overconfidence',
            'voting_cost_total', 'electoral_competitiveness'
        ]
        
        missing = [f for f in required if f not in self.features]
        if missing:
            raise ValueError(f"Missing required features: {missing}")
        
        # Check ranges (0-1 for normalized features)
        for feature, value in self.features.items():
            if feature in required and not (0 <= value <= 1):
                warnings.warn(f"Feature {feature}={value} outside [0,1] range")
    
    def _compute_drift_rate(self) -> float:
        """
        Compute drift rate μ from voter features
        
        Returns:
            Drift rate (evidence accumulation rate)
        """
        f = self.features
        p = self.params
        
        # Get partisan identity and issue salience if available, else use defaults
        partisan_id = f.get('partisan_identity_strength', 0.5)
        issue_salience = f.get('issue_salience', 0.5)
        
        mu = (
            p.drift_rate_base +
            p.beta_D * f['civic_duty'] +
            p.beta_PI * partisan_id +
            p.beta_IS * issue_salience +
            p.beta_S * f['social_pressure_sensitivity'] +
            p.beta_H * f['habit_strength'] +
            p.beta_C * f['voting_cost_total'] +  # Note: negative beta
            p.beta_EC * f['electoral_competitiveness'] +
            p.beta_OC * f['overconfidence']
        )
        
        return mu
    
    def _compute_threshold(self) -> float:
        """
        Compute decision threshold a
        Higher threshold = more cautious, requires more evidence
        
        Returns:
            Decision threshold
        """
        f = self.features
        p = self.params
        
        a = p.threshold_base * (
            (1 + p.gamma_risk * f['risk_aversion']) *
            (1 - p.gamma_edu * f['education_normalized']) /
            (1 + p.gamma_OC * f['overconfidence'])
        )
        
        # Ensure positive threshold
        return max(a, 0.5)
    
    def _compute_starting_point(self) -> float:
        """
        Compute starting point z (initial bias)
        
        Returns:
            Starting point between 0 and a
        """
        f = self.features
        p = self.params
        
        # Get partisan identity if available
        partisan_id = f.get('partisan_identity_strength', 0.5)
        
        # Compute bias components
        habit_bias = p.alpha_H * f['habit_strength']
        pi_bias = p.alpha_PI * (partisan_id - 0.5)
        duty_bias = p.alpha_D * (f['civic_duty'] - 0.5)
        
        # Starting point as proportion of threshold
        z_proportion = 0.5 + habit_bias + pi_bias + duty_bias
        z_proportion = np.clip(z_proportion, 0.1, 0.9)  # Keep away from boundaries
        
        return self.a * z_proportion
    
    def _compute_diffusion_coefficient(self) -> float:
        """
        Compute diffusion coefficient σ (decision noise)
        
        Returns:
            Diffusion coefficient
        """
        f = self.features
        p = self.params
        
        sigma = p.sigma_base * (
            (1 + p.nu_edu * (1 - f['education_normalized'])) *
            (1 - p.nu_OC * f['overconfidence'])
        )
        
        return max(sigma, 0.05)  # Minimum noise
    
    def compute_analytical_probability(self) -> float:
        """
        Compute P(Vote) using analytical DDM solution
        
        For constant drift and boundaries at 0 and a:
        P(Vote) = [1 - exp(-2μz/σ²)] / [1 - exp(-2μa/σ²)]
        
        Returns:
            Probability of voting (0-1)
        """
        if abs(self.mu) < 1e-6:
            # No drift case
            return self.z / self.a
        
        numerator = 1 - np.exp(-2 * self.mu * self.z / (self.sigma ** 2))
        denominator = 1 - np.exp(-2 * self.mu * self.a / (self.sigma ** 2))
        
        # Handle numerical issues
        if abs(denominator) < 1e-10:
            # Very strong drift toward voting
            return 1.0 if self.mu > 0 else 0.0
        
        p_vote = numerator / denominator
        return np.clip(p_vote, 0, 1)
    
    def simulate_decision(self, dt: float = 0.01, max_time: float = 10.0,
                         method: str = 'euler') -> Tuple[int, float]:
        """
        Simulate DDM decision process using Euler-Maruyama method
        
        Args:
            dt: Time step size
            max_time: Maximum simulation time
            method: Integration method ('euler' or 'exact')
        
        Returns:
            Tuple of (decision, decision_time)
            decision: 1 = vote, 0 = abstain
            decision_time: time to reach boundary
        """
        X = self.z
        t = 0
        
        trajectory = [X]  # For debugging
        
        while t < max_time:
            if method == 'euler':
                # Euler-Maruyama integration
                dW = np.random.normal(0, np.sqrt(dt))
                dX = self.mu * dt + self.sigma * dW
                X += dX
            elif method == 'exact':
                # Exact simulation (Wiener process)
                X += self.mu * dt + self.sigma * np.random.normal(0, np.sqrt(dt))
            else:
                raise ValueError(f"Unknown method: {method}")
            
            t += dt
            trajectory.append(X)
            
            # Check boundaries
            if X >= self.a:
                self.last_decision = 1
                self.last_decision_time = t
                return 1, t  # Vote
            elif X <= 0:
                self.last_decision = 0
                self.last_decision_time = t
                return 0, t  # Abstain
        
        # Time limit reached - decide based on current position
        decision = int(X > self.a / 2)
        self.last_decision = decision
        self.last_decision_time = max_time
        
        return decision, max_time
    
    def apply_nudge(self, nudge_type: str, nudge_params: Dict):
        """
        Apply nudge by modifying DDM parameters
        
        Args:
            nudge_type: Type of nudge
            nudge_params: Nudge-specific parameters
        """
        if nudge_type == 'monetary':
            # Increases drift rate
            lottery_value = nudge_params.get('lottery_value', 0.3)
            lottery_prob = nudge_params.get('lottery_prob', 0.01)
            civic_duty = self.features['civic_duty']
            
            lottery_boost = lottery_value * lottery_prob * (1 / (1 + civic_duty))
            self.mu += lottery_boost
        
        elif nudge_type == 'social_norm':
            # Increases drift via social pressure component
            revealed = nudge_params.get('revealed_turnout', 0.75)
            prior = nudge_params.get('prior_belief', 0.5)
            
            social_boost = self.params.beta_S * 0.5 * (revealed - prior)
            self.mu += social_boost
            
            # Also reduces noise (information effect)
            self.sigma *= 0.85
        
        elif nudge_type == 'identity':
            # Shifts starting point
            identity_strength = nudge_params.get('identity_strength', 0.7)
            frame_strength = nudge_params.get('frame_strength', 1.0)
            
            identity_shift = 0.15 * identity_strength * frame_strength
            self.z = np.clip(self.z + identity_shift * self.a, 0.05 * self.a, 0.95 * self.a)
        
        elif nudge_type == 'disclosure':
            # Amplifies social pressure in drift
            threat_level = nudge_params.get('threat_level', 1.5)
            social_pressure = self.features['social_pressure_sensitivity']
            
            disclosure_boost = self.params.beta_S * social_pressure * threat_level
            self.mu += disclosure_boost
        
        elif nudge_type == 'implementation':
            # Reduces threshold and shifts starting point
            plan_quality = nudge_params.get('plan_quality', 0.7)
            
            self.a *= (1 - 0.15 * plan_quality)  # Reduce threshold
            self.z += 0.1 * plan_quality * self.a  # Shift starting point
            self.z = np.clip(self.z, 0.05 * self.a, 0.95 * self.a)
        
        elif nudge_type == 'competitiveness':
            # Increases drift via competitiveness component
            comp_info = nudge_params.get('competitiveness_info', 0.8)
            
            # Political efficacy proxy
            efficacy = (0.4 * self.features['education_normalized'] +
                       0.3 * self.features['overconfidence'] +
                       0.3 * self.features.get('partisan_identity_strength', 0.5))
            
            comp_boost = self.params.beta_EC * comp_info * efficacy
            self.mu += comp_boost
            
            # Reduces noise
            self.sigma *= 0.85
        
        else:
            raise ValueError(f"Unknown nudge type: {nudge_type}")
        
        # Recompute probability after nudge
        return self.compute_analytical_probability()
    
    def get_diagnostics(self) -> Dict:
        """
        Get diagnostic information about voter's DDM parameters
        
        Returns:
            Dictionary with diagnostic info
        """
        return {
            'voter_id': self.voter_id,
            'drift_rate': self.mu,
            'threshold': self.a,
            'starting_point': self.z,
            'diffusion_coef': self.sigma,
            'p_vote_analytical': self.compute_analytical_probability(),
            'last_decision': self.last_decision,
            'last_decision_time': self.last_decision_time,
            'drift_to_threshold_ratio': self.mu / self.a if self.a > 0 else 0
        }


class DDMPopulation:
    """Container for a population of DDM voters"""
    
    def __init__(self, voters: list[DDMVoter]):
        """
        Initialize population
        
        Args:
            voters: List of DDMVoter objects
        """
        self.voters = voters
        self.n_voters = len(voters)
    
    def simulate_election(self, n_simulations: int = 1000, 
                         use_analytical: bool = False) -> Dict:
        """
        Simulate election for all voters
        
        Args:
            n_simulations: Number of Monte Carlo simulations per voter
            use_analytical: If True, use analytical probabilities
        
        Returns:
            Dictionary with simulation results
        """
        if use_analytical:
            # Use analytical probabilities
            probabilities = [v.compute_analytical_probability() for v in self.voters]
            decisions = np.random.binomial(1, probabilities)
            turnout = np.mean(decisions)
            
            return {
                'turnout_rate': turnout,
                'method': 'analytical',
                'n_simulations': 1,
                'individual_probabilities': probabilities
            }
        else:
            # Monte Carlo simulation
            all_decisions = []
            all_times = []
            
            for voter in self.voters:
                voter_decisions = []
                voter_times = []
                
                for _ in range(n_simulations):
                    decision, time = voter.simulate_decision()
                    voter_decisions.append(decision)
                    voter_times.append(time)
                
                all_decisions.append(np.mean(voter_decisions))
                all_times.append(np.mean(voter_times))
            
            return {
                'turnout_rate': np.mean(all_decisions),
                'method': 'monte_carlo',
                'n_simulations': n_simulations,
                'individual_probabilities': all_decisions,
                'mean_decision_time': np.mean(all_times),
                'decision_times': all_times
            }
    
    def apply_nudges(self, nudge_assignment: Dict[str, Dict]):
        """
        Apply nudges to specific voters
        
        Args:
            nudge_assignment: Dict mapping voter_id to nudge spec
                             {'voter_1': {'type': 'monetary', 'params': {...}}}
        """
        for voter in self.voters:
            if voter.voter_id in nudge_assignment:
                nudge_spec = nudge_assignment[voter.voter_id]
                voter.apply_nudge(nudge_spec['type'], nudge_spec['params'])
    
    def get_population_statistics(self) -> Dict:
        """
        Get aggregate statistics for population
        
        Returns:
            Dictionary with population-level statistics
        """
        diagnostics = [v.get_diagnostics() for v in self.voters]
        
        return {
            'n_voters': self.n_voters,
            'mean_drift': np.mean([d['drift_rate'] for d in diagnostics]),
            'mean_threshold': np.mean([d['threshold'] for d in diagnostics]),
            'mean_p_vote': np.mean([d['p_vote_analytical'] for d in diagnostics]),
            'std_drift': np.std([d['drift_rate'] for d in diagnostics]),
            'std_threshold': np.std([d['threshold'] for d in diagnostics]),
            'std_p_vote': np.std([d['p_vote_analytical'] for d in diagnostics])
        }


def load_ddm_parameters_from_config(config: Dict) -> DDMParameters:
    """
    Load DDM parameters from configuration dictionary
    
    Args:
        config: Configuration dict with model_calibration_parameters
    
    Returns:
        DDMParameters object
    """
    ddm_config = config.get('model_calibration_parameters', {}).get('drift_diffusion_model', {})
    
    params = DDMParameters()
    
    # Load drift components
    drift_components = ddm_config.get('drift_components', {})
    params.beta_D = drift_components.get('beta_D', params.beta_D)
    params.beta_H = drift_components.get('beta_H', params.beta_H)
    params.beta_S = drift_components.get('beta_S', params.beta_S)
    params.beta_C = drift_components.get('beta_C', params.beta_C)
    
    # Load base parameters
    params.drift_rate_base = ddm_config.get('drift_rate_base', params.drift_rate_base)
    params.threshold_base = ddm_config.get('threshold_base', params.threshold_base)
    
    return params