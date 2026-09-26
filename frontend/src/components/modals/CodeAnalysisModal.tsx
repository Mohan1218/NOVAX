import React from 'react';
import { Search, ShieldCheck, AlertTriangle, CheckCircle2, FileCode, X, Layers, Cpu } from 'lucide-react';

interface CodeAnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CodeAnalysisModal: React.FC<CodeAnalysisModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-3xl max-h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
              <Search className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">Static Code & Security Analysis</h2>
                <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 text-[10px] font-mono">
                  Grade A (94/100)
                </span>
              </div>
              <p className="text-xs text-slate-400">AST linting, cyclomatic complexity scores, and security audit</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs text-slate-300">
          {/* Metrics Overview */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3.5 rounded-xl bg-[#0e1633] border border-[#1c2c58]">
              <span className="text-[11px] text-slate-400 block mb-1">Maintainability Index</span>
              <span className="text-lg font-bold text-emerald-400 font-mono">89 / 100</span>
              <span className="text-[10px] text-emerald-400">High modularity</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0e1633] border border-[#1c2c58]">
              <span className="text-[11px] text-slate-400 block mb-1">Avg Cyclomatic Complexity</span>
              <span className="text-lg font-bold text-cyan-400 font-mono">2.8 (Optimal)</span>
              <span className="text-[10px] text-slate-400">&lt; 10 is low risk</span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#0e1633] border border-[#1c2c58]">
              <span className="text-[11px] text-slate-400 block mb-1">Security Vulnerabilities</span>
              <span className="text-lg font-bold text-white font-mono">0 Critical</span>
              <span className="text-[10px] text-emerald-400">Bandit SAST clean</span>
            </div>
          </div>

          {/* Detailed Checks */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Static Audit Highlights
            </h3>

            <div className="p-3 rounded-xl bg-[#0d152f] border border-[#1a2850] space-y-2.5">
              <div className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-white">Strict Decimal Typing Enforced</h4>
                  <p className="text-slate-400 mt-0.5">All monetary calculations now require Decimal inputs, eliminating future float coercion errors.</p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 pt-2 border-t border-[#172346]">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-white">Dependency CVE Scan (pip-audit)</h4>
                  <p className="text-slate-400 mt-0.5">Scanned 34 production dependencies; 0 known Common Vulnerabilities and Exposures found.</p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 pt-2 border-t border-[#172346]">
                <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-semibold text-white">Informational: Legacy Function Deprecation</h4>
                  <p className="text-slate-400 mt-0.5">`calculate_discount_v1` is marked deprecated. Scheduled for removal in v3.0 release.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 px-6 bg-[#0d1633] border-t border-[#17254d] flex justify-end">
          <button onClick={onClose} className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs">
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
};
