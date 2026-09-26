import React, { useState } from 'react';
import { Play, Pause, SkipBack, SkipForward, CheckCircle2, ChevronRight, X, Clock, Terminal } from 'lucide-react';

interface ExecutionReplayModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ExecutionReplayModal: React.FC<ExecutionReplayModalProps> = ({ isOpen, onClose }) => {
  const [currentStep, setCurrentStep] = useState(3);
  const [isPlaying, setIsPlaying] = useState(false);

  const steps = [
    {
      num: 1,
      title: 'Problem Ingestion & Context Loading',
      time: '00:12',
      details: 'Agent received bug report: "Cart discount calculation bug". Parsed AST for 142 files in repo ecommerce-engine.',
      codeSnippet: '# Searching symbols: cart, discount, pricing, calculate_total\nFound matching module: src/services/cart_calculator.py (confidence: 96%)'
    },
    {
      num: 2,
      title: 'Reproduction & Test Isolation',
      time: '00:35',
      details: 'Synthesized isolated test case to reproduce float subtraction rounding anomaly with sample items: SKU-492, SKU-104.',
      codeSnippet: 'def test_reproduce_rounding_bug():\n    cart = Cart([Item(price=19.99), Item(price=15.00)])\n    # Expect discount = 5.25\n    assert calculate_discount(cart) == Decimal("5.25") # FAILED: 5.249999999999999'
    },
    {
      num: 3,
      title: 'Root Cause Pinpointed in AST',
      time: '01:05',
      details: 'Identified IEEE-754 precision loss at Line 84: raw float multiplication coerced into native float type before final round().',
      codeSnippet: 'Line 84: total_discount += item.price * (tier.discount_percent / 100.0) # <--- Buggy float arithmetic'
    },
    {
      num: 4,
      title: 'Autonomous Patch Synthesis',
      time: '01:40',
      details: 'Constructed safe patch replacing float multiplication with Decimal quantization using ROUND_HALF_UP.',
      codeSnippet: 'from decimal import Decimal, ROUND_HALF_UP\ndiscount_pct = Decimal(str(tier.discount_percent)) / Decimal("100")\ntotal_discount += (Decimal(str(item.price)) * discount_pct).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)'
    },
    {
      num: 5,
      title: 'Sandboxed Patch Execution',
      time: '02:05',
      details: 'Injected patch into sandbox workspace and executed pytest across the full pricing test suite.',
      codeSnippet: '$ pytest tests/test_discounts.py\n============================== 48 passed in 0.82s =============================='
    },
    {
      num: 6,
      title: 'Verification & Static Analysis',
      time: '02:30',
      details: 'Ran mypy type checker, ruff linter, and black formatter to adhere to strict repo conventions.',
      codeSnippet: '$ ruff check src/services/cart_calculator.py\nAll checks passed! Zero warnings or lint discrepancies.'
    },
    {
      num: 7,
      title: 'Commit & Pull Request Assembly',
      time: '02:45',
      details: 'Packaged patch into clean git commit with atomic message and signed off verification certificate.',
      codeSnippet: 'git commit -m "fix(cart): prevent floating-point discount truncation using quantized Decimal math"'
    }
  ];

  if (!isOpen) return null;

  const activeStepData = steps[currentStep - 1];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-4xl rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-orange-500/20 border border-orange-500/30 flex items-center justify-center text-orange-400">
              <Play className="w-5 h-5 fill-orange-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Execution Replay Studio</h2>
              <p className="text-xs text-slate-400">Scrub through each autonomous decision step and sandbox snapshot</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Step Progress Bar */}
        <div className="px-6 py-4 bg-[#090f23] border-b border-[#162345]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-300">
              Step {currentStep} of {steps.length}: <span className="text-orange-400">{activeStepData.title}</span>
            </span>
            <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-orange-400" /> {activeStepData.time} elapsed
            </span>
          </div>

          {/* Stepper Buttons */}
          <div className="grid grid-cols-7 gap-2">
            {steps.map((s) => (
              <button
                key={s.num}
                onClick={() => setCurrentStep(s.num)}
                className={`h-2.5 rounded-full transition-all ${
                  s.num === currentStep
                    ? 'bg-orange-500 shadow-[0_0_10px_#f97316]'
                    : s.num < currentStep
                    ? 'bg-emerald-500'
                    : 'bg-[#18264e] hover:bg-[#223568]'
                }`}
                title={`Step ${s.num}: ${s.title}`}
              />
            ))}
          </div>
        </div>

        {/* Replay Details Body */}
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4 flex-1 overflow-y-auto">
          {/* Left: Step Description */}
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-[#0d1633] border border-[#1b2b52] space-y-2">
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-orange-500/20 text-orange-300 border border-orange-500/30">
                ACTION PHASE
              </span>
              <h3 className="text-sm font-bold text-white mt-1">{activeStepData.title}</h3>
              <p className="text-xs text-slate-300 leading-relaxed">{activeStepData.details}</p>
            </div>

            <div className="p-3.5 rounded-xl bg-[#070b18] border border-[#172346] text-xs text-slate-400 space-y-1">
              <span className="font-semibold text-slate-200 block">Agent State:</span>
              <p>• Memory Context: 8,420 tokens active</p>
              <p>• Sandbox Container ID: <code className="text-cyan-400 font-mono">c7e82b94a</code></p>
              <p>• Status: Step completed successfully (Exit Code 0)</p>
            </div>
          </div>

          {/* Right: Code / Command Snapshot */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1.5 font-mono text-[11px]">
                <Terminal className="w-3.5 h-3.5 text-cyan-400" /> Execution Snapshot
              </span>
            </div>
            <pre className="p-4 rounded-xl bg-[#050813] border border-[#18264e] font-mono text-xs text-cyan-300 leading-relaxed overflow-x-auto h-48 select-text">
              {activeStepData.codeSnippet}
            </pre>
          </div>
        </div>

        {/* Footer Playback Controls */}
        <div className="p-4 border-t border-[#17254d] bg-[#0c142b] flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
              disabled={currentStep === 1}
              className="p-2 rounded-lg bg-[#142145] hover:bg-[#1a2d5e] text-slate-300 disabled:opacity-40 transition-colors"
            >
              <SkipBack className="w-4 h-4" />
            </button>
            <button
              onClick={() => setCurrentStep(Math.min(steps.length, currentStep + 1))}
              disabled={currentStep === steps.length}
              className="p-2 rounded-lg bg-[#142145] hover:bg-[#1a2d5e] text-slate-300 disabled:opacity-40 transition-colors"
            >
              <SkipForward className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
