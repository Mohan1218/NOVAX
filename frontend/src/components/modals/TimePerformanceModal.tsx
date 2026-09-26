import React from 'react';
import { Clock, Zap, Cpu, Activity, BarChart, X, CheckCircle, TrendingUp } from 'lucide-react';

interface TimePerformanceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const TimePerformanceModal: React.FC<TimePerformanceModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-2xl rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Time & Performance Metrics</h2>
              <p className="text-xs text-slate-400">Runtime benchmarks, token generation throughput, and resource allocation</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-300">
          {/* Key Stat Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-[#0e1631] border border-[#1b2b52]">
              <span className="text-slate-400 text-[11px] block">Total Duration</span>
              <span className="text-lg font-bold text-white font-mono mt-1 block">2m 45s</span>
              <span className="text-[10px] text-emerald-400 font-medium">42% faster than avg</span>
            </div>
            <div className="p-3 rounded-xl bg-[#0e1631] border border-[#1b2b52]">
              <span className="text-slate-400 text-[11px] block">Token Speed</span>
              <span className="text-lg font-bold text-cyan-400 font-mono mt-1 block">74 tok/s</span>
              <span className="text-[10px] text-slate-400">Streaming active</span>
            </div>
            <div className="p-3 rounded-xl bg-[#0e1631] border border-[#1b2b52]">
              <span className="text-slate-400 text-[11px] block">Model Latency</span>
              <span className="text-lg font-bold text-white font-mono mt-1 block">14 ms</span>
              <span className="text-[10px] text-emerald-400">Direct PCIe link</span>
            </div>
            <div className="p-3 rounded-xl bg-[#0e1631] border border-[#1b2b52]">
              <span className="text-slate-400 text-[11px] block">Total Tokens</span>
              <span className="text-lg font-bold text-purple-400 font-mono mt-1 block">18,420</span>
              <span className="text-[10px] text-slate-400">Prompt: 12k | Gen: 6.4k</span>
            </div>
          </div>

          {/* Phase Breakdown Progress Bars */}
          <div className="p-4 rounded-xl bg-[#0d152f] border border-[#1b2a52] space-y-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Execution Phase Breakdown
            </h3>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span>1. AST Indexing & Repository Ingestion</span>
                  <span className="font-mono text-slate-400">12s (7%)</span>
                </div>
                <div className="h-2 w-full rounded-full bg-[#162348] overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: '7%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span>2. Autonomous Root-Cause Hypothesis & Reasoning</span>
                  <span className="font-mono text-slate-400">38s (23%)</span>
                </div>
                <div className="h-2 w-full rounded-full bg-[#162348] overflow-hidden">
                  <div className="h-full bg-purple-500 rounded-full" style={{ width: '23%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span>3. Code Patch Formulation & Test Execution</span>
                  <span className="font-mono text-slate-400">45s (27%)</span>
                </div>
                <div className="h-2 w-full rounded-full bg-[#162348] overflow-hidden">
                  <div className="h-full bg-cyan-400 rounded-full" style={{ width: '27%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs text-slate-300 mb-1">
                  <span>4. Multi-Stage Verification & Regression Test Suite</span>
                  <span className="font-mono text-slate-400">70s (43%)</span>
                </div>
                <div className="h-2 w-full rounded-full bg-[#162348] overflow-hidden">
                  <div className="h-full bg-emerald-500 rounded-full" style={{ width: '43%' }} />
                </div>
              </div>
            </div>
          </div>

          {/* System Resource Utilization */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3.5 rounded-xl bg-[#090e21] border border-[#162244] flex items-center justify-between">
              <div>
                <span className="text-[11px] text-slate-400 block">Peak GPU VRAM</span>
                <span className="font-mono text-sm font-semibold text-white">4.2 GB / 24 GB</span>
              </div>
              <Cpu className="w-5 h-5 text-indigo-400" />
            </div>
            <div className="p-3.5 rounded-xl bg-[#090e21] border border-[#162244] flex items-center justify-between">
              <div>
                <span className="text-[11px] text-slate-400 block">Sandbox CPU Load</span>
                <span className="font-mono text-sm font-semibold text-white">18% (4 cores)</span>
              </div>
              <Activity className="w-5 h-5 text-emerald-400" />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#17254d] bg-[#0c142b] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
