
import React from 'react';
import { ModelType, NudgeType, SimulationSettings, EditableNudgeParams, FullSimulationConfig } from '../types';
import Card from './ui/Card';
import Tooltip from './ui/Tooltip';
import NudgeParamsEditor from './NudgeParamsEditor';
import { MODEL_DESCRIPTIONS, NUDGE_DESCRIPTIONS } from '../constants';

interface ControlPanelProps {
  settings: Omit<SimulationSettings, 'nudgeParams'>;
  setSettings: React.Dispatch<React.SetStateAction<Omit<SimulationSettings, 'nudgeParams'>>>;
  onRunSimulation: () => void;
  isLoading: boolean;
  nudgeParams: EditableNudgeParams;
  setNudgeParams: React.Dispatch<React.SetStateAction<EditableNudgeParams>>;
  onOpenConfig: () => void;
  currentProfileName: string;
  savedProfiles: FullSimulationConfig[];
  onProfileChange: (profileName: string) => void;
  config: FullSimulationConfig;
  setConfig: React.Dispatch<React.SetStateAction<FullSimulationConfig>>;
}

const ControlPanel: React.FC<ControlPanelProps> = ({ 
  settings, 
  setSettings, 
  onRunSimulation, 
  isLoading, 
  nudgeParams, 
  setNudgeParams, 
  onOpenConfig, 
  currentProfileName, 
  savedProfiles, 
  onProfileChange,
  config,
  setConfig
}) => {
  const handleSettingChange = <K extends keyof Omit<SimulationSettings, 'nudgeParams'>>(key: K, value: Omit<SimulationSettings, 'nudgeParams'>[K]) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleDurationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value, 10);
    setConfig(prev => {
        const newConfig = {
            ...prev,
            globalContext: {
                ...prev.globalContext,
                campaign_duration: newValue
            }
        };
        if (!newConfig.profileName.endsWith(' (Customized)')) {
            newConfig.profileName = `${newConfig.profileName} (Customized)`;
        }
        return newConfig;
    });
  };
  
  const Label: React.FC<{htmlFor: string, children: React.ReactNode, tooltip?: string}> = ({ htmlFor, children, tooltip }) => (
    <label htmlFor={htmlFor} className="block text-sm font-medium text-slate-400 mb-1.5">
        <span className="flex items-center">
            {children}
            {tooltip && <Tooltip text={tooltip} />}
        </span>
    </label>
  );

  const Select: React.FC<{id: string, value: string, onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void, children: React.ReactNode}> = ({ id, value, onChange, children }) => (
    <select
      id={id}
      value={value}
      onChange={onChange}
      className="w-full bg-slate-800 border border-slate-700 rounded-md shadow-sm py-2 px-3 text-slate-200 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 transition"
    >
      {children}
    </select>
  );
  
  const Section: React.FC<{title: string, children: React.ReactNode}> = ({ title, children }) => (
    <div className="space-y-4">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider pb-2 border-b border-slate-800">{title}</h3>
        <div className="pt-2 space-y-4">
            {children}
        </div>
    </div>
  );

  const profileOptionNames = savedProfiles.map(p => p.profileName);
  if (!profileOptionNames.includes(currentProfileName)) {
    profileOptionNames.unshift(currentProfileName);
  }

  return (
    <Card className="p-6 h-full">
      <div className="space-y-8">
        <div>
          <h2 className="text-lg font-bold text-white">Simulation Controls</h2>
          <p className="text-sm text-slate-400 mt-1">Configure the scenario and run the simulation.</p>
        </div>
        
        <div className="space-y-8">
           <Section title="Scenario">
                <div>
                    <Label htmlFor="scenario">Simulation Profile</Label>
                    <div className="flex items-center space-x-2">
                        <div className="flex-grow">
                            <Select
                                id="scenario"
                                value={currentProfileName}
                                onChange={(e) => onProfileChange(e.target.value)}
                            >
                                {profileOptionNames.map(name => <option key={name} value={name}>{name}</option>)}
                            </Select>
                        </div>
                        <button
                        onClick={onOpenConfig}
                        className="p-2 bg-slate-700 hover:bg-slate-600 text-slate-300 font-semibold rounded-md text-sm transition"
                        aria-label="Edit simulation profiles"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M17.293 3.293a1 1 0 011.414 0l2 2a1 1 0 010 1.414l-9 9a1 1 0 01-.39.242l-3 1a1 1 0 01-1.242-1.242l1-3a1 1 0 01.242-.39l9-9zM19 6l-2-2-7.586 7.586-1 3 3-1L19 6z" />
                                <path d="M15 5l2 2" />
                            </svg>
                        </button>
                    </div>
                </div>
                <div>
                    <Label htmlFor="campaignDuration">Campaign Duration: {config.globalContext.campaign_duration} Days</Label>
                    <input
                        type="range"
                        id="campaignDuration"
                        min="7"
                        max="120"
                        step="1"
                        value={config.globalContext.campaign_duration}
                        onChange={handleDurationChange}
                        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-sky-500"
                    />
                </div>
           </Section>
            
           <Section title="Model & Intervention">
                 <div>
                    <Label htmlFor="model" tooltip={MODEL_DESCRIPTIONS[settings.model]}>Behavioral Model</Label>
                    <Select
                        id="model"
                        value={settings.model}
                        onChange={(e) => handleSettingChange('model', e.target.value as ModelType)}
                    >
                        {Object.values(ModelType).map(m => <option key={m} value={m}>{m}</option>)}
                    </Select>
                </div>
                <div>
                    <Label htmlFor="nudge" tooltip={NUDGE_DESCRIPTIONS[settings.nudge]}>Nudge Intervention</Label>
                    <Select
                        id="nudge"
                        value={settings.nudge}
                        onChange={(e) => handleSettingChange('nudge', e.target.value as NudgeType)}
                    >
                        {Object.values(NudgeType).map(n => (
                            <option key={n} value={n} title={NUDGE_DESCRIPTIONS[n]}>
                                {n}
                            </option>
                        ))}
                    </Select>
                </div>

                {settings.nudge !== NudgeType.None && (
                    <NudgeParamsEditor
                        nudgeType={settings.nudge}
                        params={nudgeParams}
                        setParams={setNudgeParams}
                    />
                )}
           </Section>

           <Section title="Population">
                <div>
                    <Label htmlFor="numAgents">Number of Agents: {settings.numAgents.toLocaleString()}</Label>
                    <input
                        type="range"
                        id="numAgents"
                        min="1000"
                        max="10000"
                        step="1000"
                        value={settings.numAgents}
                        onChange={(e) => handleSettingChange('numAgents', parseInt(e.target.value, 10))}
                        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-sky-500"
                    />
                </div>
            </Section>
        </div>

        <button
          onClick={onRunSimulation}
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-sky-600 to-cyan-500 hover:from-sky-500 hover:to-cyan-400 disabled:bg-slate-600 disabled:from-slate-600 disabled:cursor-not-allowed text-white font-bold py-3 px-4 rounded-lg transition duration-300 ease-in-out transform hover:scale-105 active:scale-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 focus:ring-sky-500 flex items-center justify-center shadow-lg hover:shadow-cyan-500/30"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Simulating...
            </>
          ) : 'Run Simulation'}
        </button>
      </div>
    </Card>
  );
};

export default ControlPanel;
