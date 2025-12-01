
import React, { useState, useMemo } from 'react';
import { AgentDecision } from '../../types';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis, Legend, BarChart, Bar } from 'recharts';

interface AgentExplorerProps {
  agents: AgentDecision[];
}

type AgentKey = keyof Omit<AgentDecision, 'id' | 'voted' | 'affect'>;

const AGENT_ATTRIBUTE_LABELS: Record<AgentKey, string> = {
    education_normalized: 'Education (Normalized)',
    age: 'Age',
    urbanicity: 'Urbanicity',
    civic_duty: 'Civic Duty',
    habit_strength: 'Habit Strength',
    social_pressure_sensitivity: 'Social Pressure Sensitivity',
    risk_aversion: 'Risk Aversion',
    partisan_identity_strength: 'Partisan Strength',
    overconfidence: 'Overconfidence',
    personality_match_candidate: 'Candidate Match',
    issue_salience: 'Issue Salience',
    voteProb: 'Vote Probability',
};

const getHistogramData = (agents: AgentDecision[], key: AgentKey, bins: number = 20) => {
    if (agents.length === 0) return [];
    
    // For boolean/binary fields like urbanicity, use 2 bins specifically
    const isBinary = key === 'urbanicity';
    const effectiveBins = isBinary ? 2 : bins;

    const values = agents.map(a => a[key] as number);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = (max - min) < 0.000001 ? 1 : max - min;
    const step = range / effectiveBins;

    const data = Array.from({ length: effectiveBins }, (_, i) => {
        const start = min + i * step;
        const end = min + (i + 1) * step;
        let name = `${start.toFixed(2)}`;
        
        if (key === 'age') {
            name = `${start.toFixed(0)}-${end.toFixed(0)}`;
        } else if (isBinary) {
             name = start < 0.5 ? 'Rural (0)' : 'Urban (1)';
        }

        return {
            name,
            rangeStart: start,
            rangeEnd: end,
            Voted: 0,
            Abstained: 0,
            Total: 0,
        };
    });

    agents.forEach(agent => {
        const val = agent[key] as number;
        let binIndex = Math.floor((val - min) / step);
        if (binIndex >= effectiveBins) binIndex = effectiveBins - 1;
        if (binIndex < 0) binIndex = 0;

        if (agent.voted) {
            data[binIndex].Voted++;
        } else {
            data[binIndex].Abstained++;
        }
        data[binIndex].Total++;
    });

    return data;
};

const AgentExplorer: React.FC<AgentExplorerProps> = ({ agents }) => {
  const agentKeys = Object.keys(AGENT_ATTRIBUTE_LABELS) as AgentKey[];
  const [viewMode, setViewMode] = useState<'scatter' | 'histogram'>('scatter');

  // Scatter State
  const [xAxisKey, setXAxisKey] = useState<AgentKey>('age');
  const [yAxisKey, setYAxisKey] = useState<AgentKey>('social_pressure_sensitivity');
  const [zAxisKey, setZAxisKey] = useState<AgentKey>('habit_strength');

  // Histogram State
  const [histKey, setHistKey] = useState<AgentKey>('age');

  const chartData = useMemo(() => agents.map(agent => ({
    x: agent[xAxisKey],
    y: agent[yAxisKey],
    z: agent[zAxisKey],
    voted: agent.voted ? 1 : 0,
  })), [agents, xAxisKey, yAxisKey, zAxisKey]);
  
  const histData = useMemo(() => getHistogramData(agents, histKey), [agents, histKey]);

  const Select: React.FC<{id: string, value: string, onChange: (val: AgentKey) => void}> = ({ id, value, onChange }) => (
    <select
      id={id}
      value={value}
      onChange={e => onChange(e.target.value as AgentKey)}
      className="w-full bg-slate-800 border-slate-700 rounded-md py-1 px-2 text-slate-200 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500"
    >
      {agentKeys.map(key => <option key={key} value={key}>{AGENT_ATTRIBUTE_LABELS[key]}</option>)}
    </select>
  );

  const getTickFormatter = (key: AgentKey) => (value: number) => {
      if (key === 'age') return value.toFixed(0);
      return value.toFixed(2);
  };
  
  const ViewToggle = () => (
      <div className="flex justify-center mb-4 space-x-2">
          <button 
            onClick={() => setViewMode('scatter')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${viewMode === 'scatter' ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
          >
              Scatter Plot
          </button>
           <button 
            onClick={() => setViewMode('histogram')}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-colors ${viewMode === 'histogram' ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
          >
              Distribution
          </button>
      </div>
  );

  return (
    <div className="h-full flex flex-col">
      <h3 className="text-lg font-semibold text-white mb-4 text-center">Agent Population Analysis</h3>
      
      <ViewToggle />

      {viewMode === 'scatter' ? (
        <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 p-4 bg-slate-900/50 rounded-lg border border-slate-800">
                <div>
                <label htmlFor="x-axis" className="text-sm font-medium text-slate-400 mb-1 block">X-Axis:</label>
                <Select id="x-axis" value={xAxisKey} onChange={setXAxisKey} />
                </div>
                <div>
                <label htmlFor="y-axis" className="text-sm font-medium text-slate-400 mb-1 block">Y-Axis:</label>
                <Select id="y-axis" value={yAxisKey} onChange={setYAxisKey} />
                </div>
                <div>
                <label htmlFor="z-axis" className="text-sm font-medium text-slate-400 mb-1 block">Size by:</label>
                <Select id="z-axis" value={zAxisKey} onChange={setZAxisKey} />
                </div>
            </div>
            <div className="flex-grow w-full h-96">
                <ResponsiveContainer>
                <ScatterChart margin={{ top: 10, right: 30, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" strokeOpacity={0.3} />
                    <XAxis 
                    type="number" 
                    dataKey="x" 
                    name={AGENT_ATTRIBUTE_LABELS[xAxisKey]} 
                    tick={{ fill: '#94a3b8', fontSize: 12 }} 
                    axisLine={false} tickLine={false}
                    domain={['dataMin', 'dataMax']}
                    label={{ value: AGENT_ATTRIBUTE_LABELS[xAxisKey], position: 'insideBottom', offset: -15, fill: '#94a3b8' }}
                    tickFormatter={getTickFormatter(xAxisKey)}
                    />
                    <YAxis 
                    type="number" 
                    dataKey="y" 
                    name={AGENT_ATTRIBUTE_LABELS[yAxisKey]} 
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                    axisLine={false} tickLine={false}
                    domain={['dataMin', 'dataMax']}
                    label={{ value: AGENT_ATTRIBUTE_LABELS[yAxisKey], angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
                    tickFormatter={getTickFormatter(yAxisKey)}
                    />
                    <ZAxis dataKey="z" name={AGENT_ATTRIBUTE_LABELS[zAxisKey]} range={[10, 200]} />
                    <Tooltip
                        cursor={{ stroke: '#475569', strokeDasharray: '3 3' }}
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem' }}
                        itemStyle={{ color: '#e2e8f0' }}
                        formatter={(value: number, name: string) => [name === 'Age' ? value.toFixed(0) : value.toFixed(2), name]}
                        labelFormatter={() => ''}
                    />
                    <Legend wrapperStyle={{ color: '#e2e8f0', paddingTop: '20px' }} />
                    <Scatter name="Voted" data={chartData.filter(d => d.voted)} fill="#0ea5e9" opacity={0.6} shape="circle" />
                    <Scatter name="Abstained" data={chartData.filter(d => !d.voted)} fill="#f43f5e" opacity={0.6} shape="circle" />
                </ScatterChart>
                </ResponsiveContainer>
            </div>
        </>
      ) : (
        <>
            <div className="mb-4 p-4 bg-slate-900/50 rounded-lg border border-slate-800">
                <label htmlFor="hist-key" className="text-sm font-medium text-slate-400 mb-1 block">Attribute Distribution:</label>
                <Select id="hist-key" value={histKey} onChange={setHistKey} />
                <p className="text-xs text-slate-500 mt-2">
                    Shows population density for <strong>{AGENT_ATTRIBUTE_LABELS[histKey]}</strong>, broken down by voting decision.
                </p>
            </div>
            <div className="flex-grow w-full h-96">
                <ResponsiveContainer>
                    <BarChart data={histData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" strokeOpacity={0.3} vertical={false} />
                        <XAxis 
                            dataKey="name" 
                            tick={{ fill: '#94a3b8', fontSize: 11 }} 
                            axisLine={false} 
                            tickLine={false}
                            label={{ value: AGENT_ATTRIBUTE_LABELS[histKey], position: 'insideBottom', offset: -10, fill: '#94a3b8' }}
                        />
                        <YAxis 
                            tick={{ fill: '#94a3b8', fontSize: 12 }} 
                            axisLine={false} 
                            tickLine={false}
                            label={{ value: "Number of Agents", angle: -90, position: 'insideLeft', fill: '#94a3b8' }}
                        />
                        <Tooltip 
                            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '0.5rem' }}
                            labelStyle={{ color: '#e2e8f0', marginBottom: '0.5rem' }}
                        />
                        <Legend wrapperStyle={{ paddingTop: '20px' }} />
                        <Bar dataKey="Voted" stackId="a" fill="#0ea5e9" />
                        <Bar dataKey="Abstained" stackId="a" fill="#f43f5e" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </>
      )}
    </div>
  );
};

export default AgentExplorer;
