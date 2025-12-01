import React, { useState, useEffect } from 'react';
import { SimulationResult, ModelType, FullSimulationConfig, SimulationSettings, NudgeType, EditableNudgeParams } from '../types';
import Card from './ui/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Cell, LabelList, AreaChart, Area } from 'recharts';
import AgentExplorer from './results/AgentExplorer';
import DecisionInspector from './results/DecisionInspector';
import ThinkerIcon from './ui/ThinkerIcon';

interface ResultsDisplayProps {
  result: SimulationResult | null;
  isLoading: boolean;
  error: string | null;
  selectedModel: ModelType;
  fullConfig: FullSimulationConfig;
  settings: Omit<SimulationSettings, 'nudgeParams'>;
  nudgeParams: EditableNudgeParams;
}

type Tab = 'performance' | 'distribution' | 'inspector' | 'explorer';

const PerformanceIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>;
const DistributionIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" /><path strokeLinecap="round" strokeLinejoin="round" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" /></svg>;
const InspectorIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>;
const ExplorerIcon = () => <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>;

const StatMetric: React.FC<{ title: string; value: string; subvalue?: string; colorClass?: string; large?: boolean }> = ({ title, value, subvalue, colorClass = "text-sky-400", large = false }) => (
    <div className="text-center p-4 bg-slate-900/50 rounded-lg">
        <p className={`text-xs font-medium text-slate-400 uppercase tracking-wider`}>{title}</p>
        <p className={`font-semibold tracking-tight ${large ? 'text-4xl' : 'text-2xl'} ${colorClass}`}>{value}</p>
        {subvalue && <p className="text-xs text-slate-500">{subvalue}</p>}
    </div>
);

const AnimatedTurnoutGauge: React.FC<{ result: SimulationResult }> = ({ result }) => {
    const { turnout, groundTruth, baselineTurnout } = result;
    const [displayTurnout, setDisplayTurnout] = useState(0);

    useEffect(() => {
        const timeout = setTimeout(() => setDisplayTurnout(turnout), 100);
        return () => clearTimeout(timeout);
    }, [turnout]);

    const angle = displayTurnout * 180;
    const groundTruthAngle = groundTruth * 180;
    const baselineAngle = baselineTurnout !== undefined ? baselineTurnout * 180 : null;

    const polarToCartesian = (centerX: number, centerY: number, radius: number, angleInDegrees: number) => {
        // angleInDegrees: 0 = Left, 180 = Right.
        // SVG coord system: (angle - 180) * PI/180.
        // 0 deg -> -180 rad -> cos(-180)=-1 (Left).
        // 180 deg -> 0 rad -> cos(0)=1 (Right).
        const angleInRadians = (angleInDegrees - 180) * Math.PI / 180.0;
        return {
            x: centerX + (radius * Math.cos(angleInRadians)),
            y: centerY + (radius * Math.sin(angleInRadians))
        };
    };

    const endPoint = polarToCartesian(100, 100, 80, angle);

    return (
        <div className="relative h-52 w-full flex flex-col items-center justify-center">
            <svg viewBox="0 0 200 110" className="w-full h-full">
                <defs>
                    <linearGradient id="gaugeGradient" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stopColor="#0ea5e9" />
                        <stop offset="100%" stopColor="#22d3ee" />
                    </linearGradient>
                </defs>
                {/* Background Arc */}
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#1e293b" strokeWidth="20" strokeLinecap="round" />
                {/* Foreground Arc */}
                <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="url(#gaugeGradient)" strokeWidth="20" strokeLinecap="round"
                    strokeDasharray={`${angle / 180 * Math.PI * 80}, ${Math.PI * 80}`}
                    style={{ transition: 'stroke-dasharray 1s ease-in-out' }}
                />
                
                {/* Ground Truth Marker (Inside Arc) */}
                {/* Radius 75 for tip (just inside 80), Text at 60 */}
                <line x1="100" y1="100" x2={polarToCartesian(100, 100, 75, groundTruthAngle).x} y2={polarToCartesian(100, 100, 75, groundTruthAngle).y} stroke="#64748b" strokeWidth="2" />
                <circle cx={polarToCartesian(100, 100, 75, groundTruthAngle).x} cy={polarToCartesian(100, 100, 75, groundTruthAngle).y} r="3" fill="#64748b" />
                <text x={polarToCartesian(100, 100, 60, groundTruthAngle).x} y={polarToCartesian(100, 100, 60, groundTruthAngle).y} fill="#94a3b8" fontSize="10" fontWeight="bold" textAnchor="middle" dy="3">GT</text>


                {/* Baseline Marker (Inside Arc) */}
                {/* Radius 75 for tip, Text at 45 to avoid overlapping GT if close */}
                {baselineAngle !== null && (
                    <>
                    <line x1="100" y1="100" x2={polarToCartesian(100, 100, 75, baselineAngle).x} y2={polarToCartesian(100, 100, 75, baselineAngle).y} stroke="#a3a3a3" strokeWidth="1" strokeDasharray="2 2" />
                    <text x={polarToCartesian(100, 100, 45, baselineAngle).x} y={polarToCartesian(100, 100, 45, baselineAngle).y} fill="#a3a3a3" fontSize="8" textAnchor="middle" dy="3">Base</text>
                    </>
                )}

            </svg>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center mt-6">
                <p className="text-5xl font-bold text-sky-300 tracking-tighter">{(turnout * 100).toFixed(2)}%</p>
                <p className="text-sm text-slate-400 font-medium">Simulated Turnout</p>
            </div>
        </div>
    );
};

const DistributionChart: React.FC<{ data: { prob: number; density: number }[] }> = ({ data }) => {
    return (
        <div className="h-full flex flex-col">
            <h3 className="text-lg font-semibold text-white mb-2 text-center">Vote Probability Distribution</h3>
            <p className="text-sm text-slate-400 text-center mb-4">Shows model confidence across all agents. A U-shape indicates high confidence.</p>
            <div className="flex-grow w-full h-96">
                <ResponsiveContainer>
                    <AreaChart data={data} margin={{ top: 10, right: 30, bottom: 20, left: 10 }}>
                        <defs>
                            <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.8}/>
                                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid stroke="#334155" strokeDasharray="3 3" strokeOpacity={0.3} />
                        <XAxis 
                            dataKey="prob" 
                            unit="%" 
                            tick={{ fill: '#94a3b8', fontSize: 12 }} 
                            axisLine={false} 
                            tickLine={false}
                            label={{ value: "Predicted Vote Probability", position: "insideBottom", dy: 20, fill: '#94a3b8' }}
                        />
                        <YAxis 
                            tick={{ fill: '#94a3b8', fontSize: 12 }} 
                            axisLine={false} 
                            tickLine={false}
                            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                            label={{ value: "Population Share", angle: -90, position: 'insideLeft', dx: -10, fill: '#94a3b8' }}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem' }}
                            formatter={(value, name, props) => [`${(Number(value) * 100).toFixed(1)}%`, `Population Share`]}
                            labelFormatter={(label) => `Vote Prob: ~${Number(label).toFixed(0)}%`}
                        />
                        <Area type="monotone" dataKey="density" stroke="#0ea5e9" fill="url(#colorUv)" />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};


const InitialStateGraphic = () => (
    <div className="flex flex-col items-center justify-center h-full text-slate-500 p-6 opacity-70">
         <div className="h-32 w-32 mb-6 opacity-80 hover:opacity-100 transition-all duration-500 rounded-full bg-slate-900 p-4 border-4 border-slate-700 shadow-2xl flex items-center justify-center">
            <ThinkerIcon className="w-20 h-20 text-slate-400" />
         </div>
        <p className="text-lg text-slate-400 font-medium">Ready to Simulate</p>
        <p className="text-sm mt-1">Configure controls and press "Run Simulation".</p>
    </div>
);


const LoadingGraphic = () => (
    <div className="flex flex-col items-center justify-center h-full text-slate-400 p-6">
        <svg width="120" height="120" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" stroke="#0ea5e9" fill="#0ea5e9">
            <g transform="translate(50 50)">
                <circle r="5" transform="translate(0 -30)">
                    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle r="5" transform="translate(0 30)">
                    <animateTransform attributeName="transform" type="rotate" from="180" to="540" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle r="5" transform="translate(30 0)">
                    <animateTransform attributeName="transform" type="rotate" from="90" to="450" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle r="5" transform="translate(-30 0)">
                    <animateTransform attributeName="transform" type="rotate" from="270" to="630" dur="2s" repeatCount="indefinite" />
                </circle>
            </g>
        </svg>
        <p className="text-lg mt-4 tracking-wider">SIMULATING...</p>
    </div>
);


const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result, isLoading, error, selectedModel, fullConfig, settings, nudgeParams }) => {
  const [activeTab, setActiveTab] = useState<Tab>('performance');

  const modelComparisonData = result ? result.turnoutByModel.map(d => ({
    name: d.model,
    Turnout: d.turnout * 100
  })).sort((a,b) => b.Turnout - a.Turnout) : [];

  const renderInitialState = () => <InitialStateGraphic />;
  const renderLoading = () => <LoadingGraphic />;
  
  const renderError = () => (
    <div className="flex items-center justify-center h-full text-red-400 p-6">
      <p>Error: {error}</p>
    </div>
  );

  const TabButton: React.FC<{tabName: Tab, currentTab: Tab, children: React.ReactNode, icon: React.ReactNode}> = ({ tabName, currentTab, children, icon }) => (
    <button
        onClick={() => setActiveTab(tabName)}
        className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
            currentTab === tabName
            ? 'text-white border-sky-500'
            : 'text-slate-400 hover:text-white border-transparent'
        }`}
    >
        {icon}
        <span>{children}</span>
    </button>
  );

  const renderResults = () => {
    if (!result) return renderInitialState();
    
    const nudgeLift = result.baselineTurnout !== undefined ? result.turnout - result.baselineTurnout : null;

    return (
        <div className="flex flex-col h-full animate-fade-in">
            <div className="p-6 border-b border-slate-800">
                <AnimatedTurnoutGauge result={result} />
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
                   <StatMetric title="Ground Truth" value={`${(result.groundTruth * 100).toFixed(2)}%`} colorClass="text-slate-400" />
                   <StatMetric title="Model Error" value={`${((result.turnout - result.groundTruth) * 100).toFixed(2)}pp`} colorClass="text-yellow-400" />
                   {nudgeLift !== null && (
                       <StatMetric
                           title="Nudge Lift" 
                           value={`${nudgeLift >= 0 ? '▲' : '▼'} ${Math.abs(nudgeLift * 100).toFixed(2)}pp`}
                           colorClass={nudgeLift >= 0 ? 'text-green-400' : 'text-red-400'}
                       />
                   )}
                   {settings.nudge !== NudgeType.None && result.baselineTurnout && (
                       <StatMetric title="Baseline Turnout" value={`${(result.baselineTurnout * 100).toFixed(2)}%`} colorClass="text-slate-400" />
                   )}
                </div>
            </div>
            
            <div className="flex justify-between items-center border-b border-slate-800 bg-slate-900/50 px-4">
                <div className="flex">
                    <TabButton tabName="performance" currentTab={activeTab} icon={<PerformanceIcon/>}>Performance</TabButton>
                    <TabButton tabName="distribution" currentTab={activeTab} icon={<DistributionIcon/>}>Distribution</TabButton>
                    <TabButton tabName="inspector" currentTab={activeTab} icon={<InspectorIcon/>}>Inspector</TabButton>
                    <TabButton tabName="explorer" currentTab={activeTab} icon={<ExplorerIcon/>}>Explorer</TabButton>
                </div>
                <div className="text-right pr-2">
                    <p className="text-xs text-slate-500">Profile</p>
                    <p className="text-sm font-semibold text-slate-300 truncate">{fullConfig.profileName}</p>
                </div>
            </div>
            
            <div className="flex-grow overflow-y-auto p-6 bg-slate-950/20">
                {activeTab === 'performance' && (
                     <div className="space-y-8">
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-4 text-center">Model Comparison</h3>
                            <div className="h-60 w-full">
                                <ResponsiveContainer>
                                    <BarChart data={modelComparisonData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
                                        <CartesianGrid stroke="#334155" strokeDasharray="3 3" strokeOpacity={0.3} />
                                        <XAxis type="number" unit="%" domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} tickLine={false} />
                                        <YAxis type="category" dataKey="name" tick={{ fill: '#e2e8f0', fontSize: 12, fontWeight: 500 }} width={110} axisLine={false} tickLine={false} />
                                        <Tooltip
                                            cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem' }}
                                            formatter={(value: number) => [`${value.toFixed(2)}%`, 'Turnout']}
                                            labelStyle={{ color: '#e2e8f0' }}
                                        />
                                        <ReferenceLine x={result.groundTruth * 100} stroke="#64748b" strokeDasharray="4 4" />
                                        <Bar dataKey="Turnout" name="Simulated Turnout" barSize={20}>
                                            <LabelList dataKey="Turnout" position="right" formatter={(v:number) => `${v.toFixed(1)}%`} fill="#e2e8f0" fontSize={12} />
                                            {modelComparisonData.map((entry) => (
                                                <Cell key={`cell-${entry.name}`} fill={entry.name === selectedModel ? '#0ea5e9' : '#38bdf8'} fillOpacity={entry.name === selectedModel ? 1 : 0.6} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {selectedModel === ModelType.DualSystem && result.diagnostics && (
                            <div className="pt-4">
                                <h3 className="text-lg font-semibold text-white mb-4 text-center">Dual-System Diagnostics</h3>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                                    <StatMetric title="Avg. System 1 (Auto) Prob." value={`${(result.diagnostics.avgP1 * 100).toFixed(1)}%`} />
                                    <StatMetric title="Avg. System 2 (Deliberate) Prob." value={`${(result.diagnostics.avgP2 * 100).toFixed(1)}%`} />
                                    <StatMetric title="Avg. System 1 Weight (λ)" value={`${(result.diagnostics.avgLambda).toFixed(2)}`} />
                                </div>
                            </div>
                        )}
                    </div>
                )}
                {activeTab === 'distribution' && (
                    <DistributionChart data={result.voteProbDistribution} />
                )}
                {activeTab === 'inspector' && (
                    <DecisionInspector result={result} config={fullConfig} settings={settings} nudgeParams={nudgeParams} />
                )}
                {activeTab === 'explorer' && (
                    <AgentExplorer agents={result.agents} />
                )}
            </div>
        </div>
    );
  }

  return (
    <Card className="h-full min-h-[600px] flex flex-col overflow-hidden">
        {isLoading ? renderLoading() : error ? renderError() : renderResults()}
    </Card>
  );
};

export default ResultsDisplay;
