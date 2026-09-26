import React from 'react';
import { BarChart3, TrendingUp, CheckCircle, Clock, Zap, Cpu, X } from 'lucide-react';

interface AnalyticsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AnalyticsModal: React.FC<AnalyticsModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const weeklyStats = [
    { day: 'Mon', tasks: 8, height: '60%' },
    { day: 'Tue', tasks: 12, height: '85%' },
    { day: 'Wed', tasks: 10, height: '70%' },
    { day: 'Thu', tasks: 14, height: '100%' },
    { day: 'Fri', tasks: 11, height: '78%' },
    { day: 'Sat', tasks: 4, height: '30%' },
    { day: 'Sun', tasks: 3, height: '22%' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-3xl max-h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <BarChart3 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Autonomous Agent Analytics</h2>
              <p className="text-xs text-slate-400">Productivity, resolution rate, token burn, and velocity metrics</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-300">
          {/* Key Metric Cards */}
          <div className="grid grid-cols-4 gap-3">
            <div className="p-3.5 rounded-xl bg-[#0e1633] border border-[#1c2c58]">
              <span className="text-[11px] text-slate-400 block mb-1">Tasks Solved</span>
              <span className="text-xl font-bold text-white font-mono">62</span>
              <span className="text-[10px] text-emerald-400 font-medium">↑ +18% vs last week</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0e1633] border border-[#1c2c58]">
              <span className="text-[11px] text-slate-400 block mb-1">Success Rate</span>
              <span className="text-xl font-bold text-emerald-400 font-mono">95.1%</span>
              <span className="text-[10px] text-slate-400">59 verified / 3 failed</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0e1633] border border-[#1c2c58]">
              <span className="text-[11px] text-slate-400 block mb-1">Avg Resolution Time</span>
              <span className="text-xl font-bold text-cyan-400 font-mono">3m 12s</span>
              <span className="text-[10px] text-emerald-400">⚡ 12x faster than human</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0e1633] border border-[#1c2c58]">
              <span className="text-[11px] text-slate-400 block mb-1">Token Efficiency</span>
              <span className="text-xl font-bold text-purple-400 font-mono">1.2M</span>
              <span className="text-[10px] text-slate-400">\$2.40 total API cost</span>
            </div>
          </div>

          {/* Weekly Velocity Chart */}
          <div className="p-4 rounded-xl bg-[#0d152f] border border-[#1a2850]">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider mb-4 flex items-center justify-between">
              <span>Weekly Solved Tasks Distribution</span>
              <span className="text-slate-400 font-mono font-normal">Apr 20 - Apr 26</span>
            </h3>

            <div className="flex items-end justify-between h-40 pt-4 px-2">
              {weeklyStats.map((stat) => (
                <div key={stat.day} className="flex flex-col items-center gap-2 flex-1">
                  <span className="text-[11px] font-mono font-semibold text-slate-300">{stat.tasks}</span>
                  <div className="w-8 bg-[#17254c] rounded-t-lg relative overflow-hidden h-32 flex items-end">
                    <div
                      className="w-full bg-gradient-to-t from-blue-600 to-cyan-400 rounded-t-lg transition-all duration-500"
                      style={{ height: stat.height }}
                    />
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono">{stat.day}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 px-6 bg-[#0c142b] border-t border-[#17254d] flex justify-end">
          <button onClick={onClose} className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
