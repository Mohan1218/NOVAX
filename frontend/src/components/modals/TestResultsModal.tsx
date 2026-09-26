import React, { useState } from 'react';
import { FlaskConical, CheckCircle2, XCircle, Clock, Play, RotateCcw, X, Terminal } from 'lucide-react';

interface TestResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const TestResultsModal: React.FC<TestResultsModalProps> = ({ isOpen, onClose }) => {
  const [filter, setFilter] = useState<'all' | 'passed' | 'failed'>('all');

  const tests = [
    { id: 1, name: 'tests/test_discounts.py::test_tier_precision_rounding', status: 'passed', time: '14ms' },
    { id: 2, name: 'tests/test_discounts.py::test_bulk_order_percentage', status: 'passed', time: '18ms' },
    { id: 3, name: 'tests/test_discounts.py::test_zero_discount_edge_case', status: 'passed', time: '9ms' },
    { id: 4, name: 'tests/test_cart.py::test_cart_total_quantization', status: 'passed', time: '22ms' },
    { id: 5, name: 'tests/test_cart.py::test_multi_currency_conversion', status: 'passed', time: '35ms' },
    { id: 6, name: 'tests/test_checkout.py::test_atomic_payment_lock', status: 'passed', time: '41ms' },
    { id: 7, name: 'tests/test_checkout.py::test_session_timeout_cleanup', status: 'passed', time: '16ms' },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-3xl max-h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <FlaskConical className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">Automated Test Runner Results</h2>
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono">
                  48 / 48 PASSED
                </span>
              </div>
              <p className="text-xs text-slate-400">Pytest test suite execution in containerized gVisor environment</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Test Summary Banner */}
        <div className="px-6 py-4 bg-[#080e22] border-b border-[#162345] flex items-center justify-between">
          <div className="flex items-center gap-5 text-xs font-mono">
            <span className="text-emerald-400 font-bold flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" /> 48 Passed
            </span>
            <span className="text-slate-500">0 Failed</span>
            <span className="text-slate-500">1 Skipped</span>
            <span className="text-slate-400 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-slate-500" /> 1.42s total
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-500/30 font-mono">
              100% SUCCESS
            </span>
          </div>
        </div>

        {/* Tests List */}
        <div className="p-5 overflow-y-auto space-y-2 flex-1 font-mono text-xs">
          {tests.map((t) => (
            <div
              key={t.id}
              className="p-3 rounded-xl bg-[#0d1633] border border-[#1b2b52] flex items-center justify-between hover:bg-[#121e42] transition-colors"
            >
              <div className="flex items-center gap-3 min-w-0">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <span className="text-slate-200 truncate">{t.name}</span>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0 ml-3">
                <span className="text-[11px] text-slate-400">{t.time}</span>
                <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-400 font-bold">
                  PASS
                </span>
              </div>
            </div>
          ))}
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
