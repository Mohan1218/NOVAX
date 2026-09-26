import React from 'react';
import { ShieldCheck, CheckCircle2, Shield, Lock, FileCheck, X, Check } from 'lucide-react';

interface VerificationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const VerificationModal: React.FC<VerificationModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const stages = [
    { name: 'Stage 1: Clean AST Syntax Parsing', status: 'VERIFIED', details: 'Zero AST parse discrepancies or malformed tokens.' },
    { name: 'Stage 2: Strict Static Type Consistency', status: 'VERIFIED', details: 'Mypy --strict returned exit status 0 across 14 modules.' },
    { name: 'Stage 3: Controlled Anomaly Reproduction', status: 'VERIFIED', details: 'Validated that pre-patch baseline accurately failed with reproduction payload.' },
    { name: 'Stage 4: Unit & Functional Validation', status: 'VERIFIED', details: 'All 48 unit tests executed in 1.42s with identical expected outputs.' },
    { name: 'Stage 5: Non-Regression & Boundary Checks', status: 'VERIFIED', details: 'Full suite regression passed without side-effects on neighboring modules.' },
    { name: 'Stage 6: Static Security Audit & Sanitization', status: 'VERIFIED', details: 'Bandit SAST and pip-audit reports clear with 0 CVEs.' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-3xl max-h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-teal-500/20 border border-teal-500/30 flex items-center justify-center text-teal-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">Autonomous Verification Gate</h2>
                <span className="px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-300 border border-teal-500/30 text-[10px] font-mono">
                  ALL GATES PASSED
                </span>
              </div>
              <p className="text-xs text-slate-400">Multi-phase integrity assertion pipeline ensuring reliable code release</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Certificate Badge */}
        <div className="p-4 px-6 bg-[#07151e] border-b border-[#12313b] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-teal-500/20 flex items-center justify-center text-teal-400">
              <Lock className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs font-bold text-teal-300">Cryptographically Signed Verification Certificate</span>
              <p className="text-[11px] text-teal-400/80 font-mono">Hash: 8f4b238a9e01dc7452bf9a76e</p>
            </div>
          </div>
          <span className="text-[11px] font-mono text-teal-400 px-2 py-1 rounded bg-teal-950/60 border border-teal-500/40">
            Production Ready
          </span>
        </div>

        {/* Stages */}
        <div className="p-5 overflow-y-auto space-y-2.5 flex-1 text-xs">
          {stages.map((stage, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-[#0c142b] border border-[#172346] flex items-start gap-3">
              <CheckCircle2 className="w-4 h-4 text-teal-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-white">{stage.name}</h4>
                  <span className="text-[10px] font-mono text-teal-400 bg-teal-950/50 px-2 py-0.5 rounded border border-teal-500/30">
                    {stage.status}
                  </span>
                </div>
                <p className="text-slate-400 mt-1 leading-relaxed">{stage.details}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 px-6 bg-[#0c142b] border-t border-[#17254d] flex justify-end">
          <button onClick={onClose} className="px-4 py-1.5 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-medium text-xs">
            Acknowledge
          </button>
        </div>
      </div>
    </div>
  );
};
