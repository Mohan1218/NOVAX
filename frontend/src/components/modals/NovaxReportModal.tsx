import React, { useState } from 'react';
import { FileText, Download, CheckCircle, ShieldAlert, Cpu, GitCommit, Copy, Check, X } from 'lucide-react';

interface NovaxReportModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NovaxReportModal: React.FC<NovaxReportModalProps> = ({ isOpen, onClose }) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleDownload = () => {
    const reportText = `# NOVAX Autonomous Execution Report
Task ID: 0fed28a5-task-1
Timestamp: 2026-09-26 15:20:18 UTC
Target: ecommerce-engine (branch: fix/discount-tier-precision)
Status: VERIFIED (All tests passing)

## Executive Summary
NOVAX autonomously investigated a reported calculation discrepancy in the discount engine.
Root Cause: IEEE-754 precision inaccuracies when applying tiered cart discounts in Python float operations.
Fix: Refactored monetary arithmetic to use Python 'decimal.Decimal' with strict banker's quantization.
Verification: 48/48 unit & integration tests passed. 0 regression failures.
`;
    const blob = new Blob([reportText], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'NOVAX-Execution-Report.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-3xl max-h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-sky-500/20 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">NOVAX Execution Report</h2>
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono">
                  VERIFIED
                </span>
              </div>
              <p className="text-xs text-slate-400">Comprehensive audit and automated fix verification document</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs text-slate-300">
          {/* Top Status Cards */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-[#0f1836] border border-[#1d2d57]">
              <span className="text-[11px] text-slate-400 block mb-1">Execution Time</span>
              <span className="text-base font-bold text-white font-mono">2m 45s</span>
            </div>
            <div className="p-3 rounded-xl bg-[#0f1836] border border-[#1d2d57]">
              <span className="text-[11px] text-slate-400 block mb-1">Files Modified</span>
              <span className="text-base font-bold text-white font-mono">3 files (+42, -18)</span>
            </div>
            <div className="p-3 rounded-xl bg-[#0f1836] border border-[#1d2d57]">
              <span className="text-[11px] text-slate-400 block mb-1">Test Suite Pass Rate</span>
              <span className="text-base font-bold text-emerald-400 font-mono">100% (48/48)</span>
            </div>
          </div>

          {/* Section: Executive Summary */}
          <div className="p-4 rounded-xl bg-[#0e1633] border border-[#1c2c58] space-y-2">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400" /> Executive Summary
            </h3>
            <p className="text-slate-300 leading-relaxed">
              NOVAX Autonomous Agent detected and rectified a floating-point precision bug in the tiered SKU pricing pipeline. The issue caused intermittent \$0.01 cent rounding errors on bulk orders exceeding 50 items.
            </p>
          </div>

          {/* Section: Root Cause Analysis */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider text-slate-400">
              Root Cause Diagnosis
            </h3>
            <div className="p-4 rounded-xl bg-[#070b18] border border-[#18264e] font-mono text-[11px] space-y-1">
              <p className="text-rose-400">File: src/services/cart_calculator.py (Line 84)</p>
              <p className="text-slate-400">Old: discount_amt = round(base_price * discount_pct, 2)</p>
              <p className="text-emerald-400">New: discount_amt = (Decimal(str(base_price)) * Decimal(str(discount_pct))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)</p>
            </div>
          </div>

          {/* Section: Verification Evidence */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider text-slate-400">
              Automated Verification Trace
            </h3>
            <div className="p-3 rounded-xl bg-[#0c142e] border border-[#1a2954] space-y-2 text-slate-300">
              <div className="flex items-center justify-between">
                <span>1. Static Type Checking (mypy --strict)</span>
                <span className="text-emerald-400 font-mono">PASSED</span>
              </div>
              <div className="flex items-center justify-between">
                <span>2. Unit Test Suite (pytest tests/unit)</span>
                <span className="text-emerald-400 font-mono">32 / 32 PASSED</span>
              </div>
              <div className="flex items-center justify-between">
                <span>3. End-to-End Cart Checkout Regression</span>
                <span className="text-emerald-400 font-mono">16 / 16 PASSED</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#17254d] bg-[#0c142b] flex items-center justify-between">
          <span className="text-[11px] text-slate-400 font-mono">Signature: SHA-256: 7f9a2e1d03b</span>
          <div className="flex items-center gap-2">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 shadow-md transition-all"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Report (.md)</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
