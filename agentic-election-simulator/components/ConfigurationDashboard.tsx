
import React, { useState, useEffect } from 'react';
import { FullSimulationConfig, ModelType } from '../types';
import { SCENARIO_TEMPLATES } from '../constants';
import Modal from './ui/Modal';
import Accordion from './ui/Accordion';
import Tooltip from './ui/Tooltip';

interface ConfigurationDashboardProps {
  isOpen: boolean;
  onClose: () => void;
  config: FullSimulationConfig;
  setConfig: React.Dispatch<React.SetStateAction<FullSimulationConfig>>;
  savedProfiles: FullSimulationConfig[];
  setSavedProfiles: React.Dispatch<React.SetStateAction<FullSimulationConfig[]>>;
}

const ConfigurationDashboard: React.FC<ConfigurationDashboardProps> = ({ isOpen, onClose, config, setConfig, savedProfiles, setSavedProfiles }) => {
  const [newProfileName, setNewProfileName] = useState('');
  const [jsonText, setJsonText] = useState('');

  // This effect will run whenever the modal is opened or the underlying config changes.
  useEffect(() => {
    if (isOpen) {
        setJsonText(JSON.stringify(config, null, 2));

        // If the current profile name indicates it's a customization...
        if (config.profileName.endsWith(' (Customized)')) {
            // ...and it hasn't been saved under this exact name yet...
            if (!savedProfiles.some(p => p.profileName === config.profileName)) {
                // ...then suggest this name for saving.
                setNewProfileName(config.profileName);
            } else {
                // Otherwise, the user needs to provide a new, unique name.
                setNewProfileName('');
            }
        } else {
            // If it's not a customized profile, start with a blank slate.
            setNewProfileName('');
        }
    }
  }, [isOpen, config, savedProfiles]);


  const handleSaveProfile = () => {
    const trimmedName = newProfileName.trim();
    if (!trimmedName) {
      alert("Profile name cannot be empty.");
      return;
    }
    if (savedProfiles.some(p => p.profileName === trimmedName)) {
      alert("A profile with this name already exists.");
      return;
    }
    const newProfile = {
      ...config,
      profileName: trimmedName,
    };
    setSavedProfiles(prev => [...prev, newProfile]);
    setNewProfileName('');
    alert(`Profile "${trimmedName}" saved successfully!`);
  };

  const handleDeleteProfile = (profileNameToDelete: string) => {
    if (window.confirm(`Are you sure you want to delete profile "${profileNameToDelete}"?`)) {
        setSavedProfiles(prev => prev.filter(p => p.profileName !== profileNameToDelete));
    }
  };

  const handleLoadProfile = (profile: FullSimulationConfig) => {
    setConfig(profile);
  };

  const handleApplyJson = () => {
      try {
          const parsed = JSON.parse(jsonText);
          // Basic validation: check for top-level keys
          if (!parsed.globalContext || !parsed.agentGeneration || !parsed.modelPhysics) {
              throw new Error("Invalid configuration format. Missing top-level sections.");
          }
          setConfig(parsed);
          alert("Configuration applied successfully!");
      } catch (e) {
          alert(`Error parsing JSON: ${(e as Error).message}`);
      }
  };

  const handleCopyJson = () => {
      navigator.clipboard.writeText(jsonText);
      alert("Configuration copied to clipboard!");
  };

  const createHandler = (path: string) => (field: string, value: string) => {
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      const keys = path.split('.');
      setConfig(prev => {
        const newConfig = JSON.parse(JSON.stringify(prev));
        let current = newConfig;
        for(let i = 0; i < keys.length; i++) {
          if (i === keys.length - 1) {
            current[keys[i]][field] = numValue;
          } else {
            current = current[keys[i]];
          }
        }
        
        // If the profile name doesn't already indicate customization, add the suffix.
        if (!newConfig.profileName.endsWith(' (Customized)')) {
            newConfig.profileName = `${newConfig.profileName} (Customized)`;
        }
        
        return newConfig;
      });
    }
  };

  const globalHandler = createHandler('globalContext');
  const agentHandler = createHandler('agentGeneration');
  const utilityHandler = createHandler('modelPhysics.utility');
  const ddmHandler = createHandler('modelPhysics.ddm');
  const dsHandler = createHandler('modelPhysics.dual_system');

  const ParamSlider: React.FC<{
      label: string, 
      value: number, 
      min: number, 
      max: number, 
      step: number, 
      handler: (field: string, value: string) => void, 
      field: string,
      tooltip: string
  }> = ({label, value, min, max, step, handler, field, tooltip}) => (
    <div className="grid grid-cols-3 items-center gap-4">
      <div className="col-span-1 flex items-center min-w-0">
          <span className="text-sm text-slate-400 mr-2 truncate">{label}</span>
          <Tooltip text={tooltip} />
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => handler(field, e.target.value)}
        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer col-span-1"
      />
      <input type="number" value={value.toFixed(3)}
        onChange={(e) => handler(field, e.target.value)}
        className="bg-slate-800 border border-slate-600 rounded-md py-1 px-2 text-slate-200 text-sm w-24"
      />
    </div>
  );
  
  const isTemplate = (profileName: string) => Object.values(SCENARIO_TEMPLATES).some(t => t.profileName === profileName);
  const modalTitle = `Configuration: ${config.profileName}`;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={modalTitle}>
      <div className="space-y-6">
        <Accordion title="Save/Load Profiles" defaultOpen>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h4 className="font-semibold text-slate-300 mb-2">Save Current Configuration</h4>
                    <div className="flex space-x-2">
                        <input
                            type="text"
                            placeholder="Enter new profile name..."
                            value={newProfileName}
                            onChange={(e) => setNewProfileName(e.target.value)}
                            className="flex-grow bg-slate-800 border border-slate-600 rounded-md py-1.5 px-3 text-slate-200 text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500"
                        />
                        <button onClick={handleSaveProfile} className="px-4 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white font-semibold rounded-md text-sm transition">Save</button>
                    </div>
                </div>
                 <div>
                    <h4 className="font-semibold text-slate-300 mb-2">Load a Profile</h4>
                    <ul className="max-h-40 overflow-y-auto space-y-2 p-2 bg-slate-900/50 rounded-md border border-slate-700">
                        {savedProfiles.map(profile => (
                            <li key={profile.profileName} className="flex items-center justify-between p-2 bg-slate-800 rounded">
                                <span className="text-sm text-slate-300 truncate pr-2">{profile.profileName}</span>
                                <div className="flex items-center space-x-2 flex-shrink-0">
                                    <button onClick={() => handleLoadProfile(profile)} className="px-3 py-1 bg-slate-600 hover:bg-slate-500 text-white rounded-md text-xs font-semibold">Load</button>
                                    {!isTemplate(profile.profileName) && (
                                        <button onClick={() => handleDeleteProfile(profile.profileName)} className="px-2 py-1 bg-rose-800 hover:bg-rose-700 text-white rounded-md text-xs">
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                                        </button>
                                    )}
                                </div>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </Accordion>
        
        <Accordion title="Global Context">
            <div className="space-y-4">
                <ParamSlider 
                    label="Electoral Competitiveness" 
                    field="electoral_competitiveness" 
                    value={config.globalContext.electoral_competitiveness} 
                    min={0} max={1} step={0.01} 
                    handler={globalHandler} 
                    tooltip="Probability that a single vote will be decisive. High values (near 1) indicate a dead heat."
                />
                <ParamSlider 
                    label="Voting Cost (Total)" 
                    field="voting_cost_total" 
                    value={config.globalContext.voting_cost_total} 
                    min={0} max={1} step={0.01} 
                    handler={globalHandler} 
                    tooltip="The aggregate barrier to voting (time, effort, logistical friction). Higher values reduce turnout."
                />
            </div>
        </Accordion>

        <Accordion title="Agent Generation Profile">
            <div className="space-y-4">
                <ParamSlider 
                    label="Education Skew" 
                    field="education_skew" 
                    value={config.agentGeneration.education_skew} 
                    min={0.1} max={5} step={0.1} 
                    handler={agentHandler} 
                    tooltip="Controls population education distribution. >1 skews towards high education, <1 skews towards low."
                />
                 <ParamSlider 
                    label="Urban Probability" 
                    field="urban_prob" 
                    value={config.agentGeneration.urban_prob} 
                    min={0} max={1} step={0.01} 
                    handler={agentHandler} 
                    tooltip="Probability that an agent lives in an urban environment."
                />
                <ParamSlider 
                    label="Civic Duty Skew" 
                    field="civic_duty_skew" 
                    value={config.agentGeneration.civic_duty_skew} 
                    min={0.1} max={5} step={0.1} 
                    handler={agentHandler} 
                    tooltip="Controls distribution of intrinsic civic duty. >1 means most agents feel a strong duty to vote."
                />
                <ParamSlider 
                    label="Past Vote Probability" 
                    field="past_vote_prob" 
                    value={config.agentGeneration.past_vote_prob} 
                    min={0} max={1} step={0.01} 
                    handler={agentHandler} 
                    tooltip="Probability that agents voted in previous elections, determining their baseline Habit Strength."
                />
                 <ParamSlider 
                    label="Risk Aversion Skew" 
                    field="risk_aversion_skew" 
                    value={config.agentGeneration.risk_aversion_skew} 
                    min={0.1} max={5} step={0.1} 
                    handler={agentHandler} 
                    tooltip="Controls distribution of risk tolerance. >1 implies most agents are risk-averse (cautious)."
                />
                 <ParamSlider 
                    label="Social Pressure Skew" 
                    field="social_pressure_skew" 
                    value={config.agentGeneration.social_pressure_skew} 
                    min={0.1} max={5} step={0.1} 
                    handler={agentHandler} 
                    tooltip="Distribution of sensitivity to social pressure. >1 means most agents are sensitive."
                />
                <ParamSlider 
                    label="Partisan Strength Skew" 
                    field="partisan_strength_skew" 
                    value={config.agentGeneration.partisan_strength_skew} 
                    min={0.1} max={5} step={0.1} 
                    handler={agentHandler} 
                    tooltip="Distribution of partisan identity strength. >1 means most agents are strongly partisan."
                />
            </div>
        </Accordion>

        <Accordion title="Model Physics (Calibration)">
           <div className="space-y-4">
             <h3 className="text-lg font-semibold text-cyan-400">Utility Model</h3>
             <ParamSlider 
                label="β (pB)" 
                field="beta_pB" 
                value={config.modelPhysics.utility.beta_pB} 
                min={0} max={3} step={0.1} 
                handler={utilityHandler} 
                tooltip="Weight assigned to the Instrumental Benefit (Pivotality × Stakes)."
             />
             <ParamSlider 
                label="β (Cost)" 
                field="beta_C" 
                value={config.modelPhysics.utility.beta_C} 
                min={-3} max={0} step={0.1} 
                handler={utilityHandler} 
                tooltip="Negative weight assigned to the Cost of voting. Stronger negative values mean costs deter voting more."
             />
             <ParamSlider 
                label="β (Duty)" 
                field="beta_D" 
                value={config.modelPhysics.utility.beta_D} 
                min={0} max={3} step={0.1} 
                handler={utilityHandler} 
                tooltip="Weight assigned to the intrinsic satisfaction of Civic Duty."
             />
             <ParamSlider 
                label="β (Habit)" 
                field="beta_H" 
                value={config.modelPhysics.utility.beta_H} 
                min={0} max={3} step={0.1} 
                handler={utilityHandler} 
                tooltip="Weight assigned to Habit (past voting history)."
             />
             <ParamSlider 
                label="β (Social)" 
                field="beta_S" 
                value={config.modelPhysics.utility.beta_S} 
                min={0} max={3} step={0.1} 
                handler={utilityHandler} 
                tooltip="Weight assigned to Social Pressure (Reward/Punishment)."
             />
             <ParamSlider 
                label="Decision Noise" 
                field="decision_noise" 
                value={config.modelPhysics.utility.decision_noise} 
                min={0.1} max={5} step={0.1} 
                handler={utilityHandler} 
                tooltip="Amount of randomness in the final decision (Temperature)."
             />
             
             <h3 className="text-lg font-semibold text-cyan-400 mt-6">Drift-Diffusion Model</h3>
             <ParamSlider 
                label="Base Drift (μ)" 
                field="base_mu" 
                value={config.modelPhysics.ddm.base_mu} 
                min={-0.5} max={0.5} step={0.01} 
                handler={ddmHandler} 
                tooltip="Baseline drift rate. Positive drives towards 'Vote', negative towards 'Abstain'."
             />
             <ParamSlider 
                label="Threshold (a)" 
                field="threshold_a" 
                value={config.modelPhysics.ddm.threshold_a} 
                min={0.5} max={5} step={0.1} 
                handler={ddmHandler} 
                tooltip="The amount of evidence required to make a decision. Higher values = more caution/deliberation."
             />
              <ParamSlider 
                label="Noise (σ)" 
                field="noise" 
                value={config.modelPhysics.ddm.noise} 
                min={0.1} max={5} step={0.1} 
                handler={ddmHandler} 
                tooltip="Standard deviation of the accumulation process (Randomness)."
             />
             <ParamSlider 
                label="β (Duty)" 
                field="beta_D" 
                value={config.modelPhysics.ddm.beta_D} 
                min={0} max={1} step={0.01} 
                handler={ddmHandler} 
                tooltip="Impact of Civic Duty on drift rate."
             />
              <ParamSlider 
                label="β (Habit)" 
                field="beta_H" 
                value={config.modelPhysics.ddm.beta_H} 
                min={0} max={1} step={0.01} 
                handler={ddmHandler} 
                tooltip="Impact of Habit on drift rate."
             />
              <ParamSlider 
                label="β (Social)" 
                field="beta_S" 
                value={config.modelPhysics.ddm.beta_S} 
                min={0} max={1} step={0.01} 
                handler={ddmHandler} 
                tooltip="Impact of Social Pressure on drift rate."
             />
             <ParamSlider 
                label="β (Cost)" 
                field="beta_C" 
                value={config.modelPhysics.ddm.beta_C} 
                min={-1} max={0} step={0.01} 
                handler={ddmHandler} 
                tooltip="Impact of Voting Cost on drift rate (Negative)."
             />
             <ParamSlider 
                label="β (pB)" 
                field="beta_pB" 
                value={config.modelPhysics.ddm.beta_pB} 
                min={0} max={1} step={0.01} 
                handler={ddmHandler} 
                tooltip="Impact of Instrumental Benefit on drift rate."
             />
             
             <h3 className="text-lg font-semibold text-indigo-400 mt-6">Dual-System (S1: Heuristic vs S2: Utility)</h3>
             <div className="p-3 bg-indigo-900/20 rounded-md mb-4 border border-indigo-800/50">
                <p className="text-xs text-indigo-300 mb-2 font-bold uppercase">System 1: Heuristic Activation</p>
                <ParamSlider label="S1 Habit" field="h_habit" value={config.modelPhysics.dual_system.h_habit} min={0} max={3} step={0.1} handler={dsHandler} tooltip="Weight of Habit in System 1." />
                <ParamSlider label="S1 Social" field="h_social" value={config.modelPhysics.dual_system.h_social} min={0} max={3} step={0.1} handler={dsHandler} tooltip="Weight of Social norms in System 1." />
                <ParamSlider label="S1 Affect" field="h_affect" value={config.modelPhysics.dual_system.h_affect} min={0} max={3} step={0.1} handler={dsHandler} tooltip="Weight of Affect (liking) in System 1." />
                <ParamSlider label="S1 Momentum" field="h_momentum" value={config.modelPhysics.dual_system.h_momentum} min={-1} max={1} step={0.1} handler={dsHandler} tooltip="Baseline impulsive tendency." />
             </div>

             <div className="p-3 bg-purple-900/20 rounded-md mb-4 border border-purple-800/50">
                 <p className="text-xs text-purple-300 mb-2 font-bold uppercase">System 2: Rational Utility</p>
                 <ParamSlider label="S2 Duty" field="u_duty" value={config.modelPhysics.dual_system.u_duty} min={0} max={3} step={0.1} handler={dsHandler} tooltip="Utility weight of Civic Duty." />
                 <ParamSlider label="S2 Benefit" field="u_pB" value={config.modelPhysics.dual_system.u_pB} min={0} max={3} step={0.1} handler={dsHandler} tooltip="Utility weight of Instrumental Benefit (P*B)." />
                 <ParamSlider label="S2 Cost" field="u_cost" value={config.modelPhysics.dual_system.u_cost} min={-5} max={0} step={0.1} handler={dsHandler} tooltip="Utility weight of Cost (Negative)." />
             </div>

             <div className="p-3 bg-slate-800/50 rounded-md border border-slate-700">
                 <p className="text-xs text-slate-300 mb-2 font-bold uppercase">Cognitive Arbiter</p>
                 <ParamSlider label="λ Base" field="lambda_base" value={config.modelPhysics.dual_system.lambda_base} min={0} max={1} step={0.01} handler={dsHandler} tooltip="Baseline weight for System 1 (Impulse)." />
                 <ParamSlider label="λ Edu Factor" field="lambda_edu_factor" value={config.modelPhysics.dual_system.lambda_edu_factor} min={-1} max={1} step={0.01} handler={dsHandler} tooltip="Education's effect on S1 usage (Negative = Edu increases S2)." />
                 <ParamSlider label="λ Risk Factor" field="lambda_risk_factor" value={config.modelPhysics.dual_system.lambda_risk_factor} min={-1} max={1} step={0.01} handler={dsHandler} tooltip="Risk Aversion's effect on S1 usage." />
             </div>
           </div>
        </Accordion>

        <Accordion title="Import / Export JSON">
            <div className="space-y-4">
                <p className="text-xs text-slate-400">
                    Copy the configuration below to save it externally, or paste a configuration JSON here and click "Apply" to load it.
                </p>
                <textarea
                    className="w-full h-64 bg-slate-900 font-mono text-xs text-slate-300 border border-slate-700 rounded p-2 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                    value={jsonText}
                    onChange={(e) => setJsonText(e.target.value)}
                />
                <div className="flex justify-end space-x-3">
                    <button
                        onClick={handleCopyJson}
                        className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold rounded transition"
                    >
                        Copy to Clipboard
                    </button>
                    <button
                        onClick={handleApplyJson}
                        className="px-3 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white text-xs font-semibold rounded transition"
                    >
                        Apply Configuration
                    </button>
                </div>
            </div>
        </Accordion>
      </div>
    </Modal>
  );
};

export default ConfigurationDashboard;
