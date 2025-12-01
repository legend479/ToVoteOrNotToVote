
import React, { useState } from 'react';
import ThinkerIcon from './ui/ThinkerIcon';

const Header: React.FC = () => {
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    const handleNavClick = (e: React.MouseEvent<HTMLAnchorElement>, hash: string) => {
        e.preventDefault();
        window.location.hash = hash;
        setIsDropdownOpen(false);
    };


    return (
        <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-40 transition-all duration-300">
            <div className="container mx-auto flex items-center justify-between p-4">
                <div className="text-lg font-bold text-white tracking-tight flex items-center gap-3">
                     <div className="h-10 w-10 rounded bg-gradient-to-br from-sky-900 to-slate-900 p-1.5 border border-slate-700 flex items-center justify-center shadow-lg shadow-sky-900/20">
                        <ThinkerIcon className="text-sky-100 w-full h-full" />
                     </div>
                    <a href="#simulator" onClick={(e) => handleNavClick(e, 'simulator')}>Agentic Election Simulator</a>
                </div>
                <nav>
                    <ul className="flex items-center space-x-1 md:space-x-6 text-sm font-medium">
                        <li>
                            <a href="#simulator" onClick={(e) => handleNavClick(e, 'simulator')} className="text-slate-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md transition-colors flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                <span className="hidden md:inline">Simulator</span>
                            </a>
                        </li>
                        <li>
                            <a href="#model-tuner" onClick={(e) => handleNavClick(e, 'model-tuner')} className="text-slate-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md transition-colors flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg>
                                <span className="hidden md:inline">Tuner & Analysis</span>
                            </a>
                        </li>
                        <li>
                            <a href="#documentation" onClick={(e) => handleNavClick(e, 'documentation')} className="text-slate-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md transition-colors flex items-center gap-2">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                                <span className="hidden md:inline">Docs</span>
                            </a>
                        </li>
                        <li className="relative">
                            <button 
                                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                                className="text-slate-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md transition-colors flex items-center gap-2"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>
                                <span className="hidden md:inline">Model Theory</span>
                                <svg xmlns="http://www.w3.org/2000/svg" className={`h-3 w-3 ml-1 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                            </button>
                            {isDropdownOpen && (
                                <>
                                <div className="fixed inset-0 z-40" onClick={() => setIsDropdownOpen(false)}></div>
                                <div className="absolute right-0 mt-2 w-64 bg-slate-900 border border-slate-700 rounded-lg shadow-xl py-2 z-50 animate-fade-in">
                                    <div className="px-4 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">Models</div>
                                    <a href="#utility-model" onClick={(e) => handleNavClick(e, 'utility-model')} className="flex items-center px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-sky-400 transition-colors">
                                        <span className="w-2 h-2 rounded-full bg-sky-500 mr-2"></span>Extended Utility
                                    </a>
                                    <a href="#ddm-model" onClick={(e) => handleNavClick(e, 'ddm-model')} className="flex items-center px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-purple-400 transition-colors">
                                         <span className="w-2 h-2 rounded-full bg-purple-500 mr-2"></span>Drift-Diffusion
                                    </a>
                                    <a href="#dual-system-model" onClick={(e) => handleNavClick(e, 'dual-system-model')} className="flex items-center px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-indigo-400 transition-colors">
                                         <span className="w-2 h-2 rounded-full bg-indigo-500 mr-2"></span>Dual-System
                                    </a>
                                    <div className="border-t border-slate-800 my-2"></div>
                                    <a href="#parameters-explained" onClick={(e) => handleNavClick(e, 'parameters-explained')} className="flex items-center px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 hover:text-emerald-400 transition-colors">
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                                        Parameter Guide
                                    </a>
                                </div>
                                </>
                            )}
                        </li>
                    </ul>
                </nav>
            </div>
        </header>
    );
};

export default Header;
