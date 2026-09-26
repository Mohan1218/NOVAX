import React, { useState, useEffect, useRef } from 'react';
import { Radio, Play, Pause, RotateCcw, Download, Terminal, X, Zap, Cpu, CheckCircle } from 'lucide-react';

interface LiveStreamingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const LiveStreamingModal: React.FC<LiveStreamingModalProps> = ({ isOpen, onClose }) => {
  const [isPlaying, setIsPlaying] = useState(true);
  const [autoScroll, setAutoScroll] = useState(true);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  const [logs, setLogs] = useState<Array<{ id: number; time: string; tag: string; color: string; message: string }>>([
    { id: 1, time: '15:20:01', tag: 'ORCHESTRATOR', color: 'text-blue-400', message: 'Task initialized: Autonomous session 0fed28a5 allocated to worker pod-7.' },
    { id: 2, time: '15:20:03', tag: 'ENVIRONMENT', color: 'text-cyan-400', message: 'Mounted workspace /workspace/ecommerce-engine in isolated gVisor container.' },
    { id: 3, time: '15:20:04', tag: 'AST_PARSER', color: 'text-purple-400', message: 'Indexing symbol tree: 142 python modules, 8,920 LOC discovered.' },
    { id: 4, time: '15:20:06', tag: 'THINKING', color: 'text-amber-400', message: 'Analyzing bug report: "Cart discount calculation precision error in tiered SKU rules".' },
    { id: 5, time: '15:20:08', tag: 'TOOL_CALL', color: 'text-emerald-400', message: 'run_command: pytest tests/test_discounts.py -k "test_tier_precision"' },
    { id: 6, time: '15:20:10', tag: 'TEST_RUNNER', color: 'text-rose-400', message: 'FAILED: test_tier_precision - AssertionError: 84.99999999999999 != Decimal("85.00")' },
    { id: 7, time: '15:20:12', tag: 'THINKING', color: 'text-amber-400', message: 'Root cause identified: IEEE-754 float multiplication without quantization in services/cart_calculator.py:84' },
    { id: 8, time: '15:20:14', tag: 'CODE_PATCH', color: 'text-cyan-400', message: 'Applying diff: Replacing `rate * price` with `(rate * Decimal(str(price))).quantize(Decimal("0.01"))`' },
    { id: 9, time: '15:20:16', tag: 'VERIFY', color: 'text-emerald-400', message: 'Re-running test suite: 48 passed, 0 failed in 0.84s. Regression tests clean.' },
  ]);

  useEffect(() => {
    if (!isOpen || !isPlaying) return;

    const streamInterval = setInterval(() => {
      setLogs((prev) => {
        const nextId = prev.length + 1;
        const now = new Date().toTimeString().split(' ')[0];
        const simulatedPool = [
          { tag: 'THINKING', color: 'text-amber-400', message: 'Checking type constraints with mypy --strict on patched cart module.' },
          { tag: 'TOOL_CALL', color: 'text-emerald-400', message: 'run_command: mypy src/services/cart_calculator.py --strict' },
          { tag: 'LINTER', color: 'text-cyan-400', message: 'Success: no issues found in 1 source file.' },
          { tag: 'GIT', color: 'text-indigo-400', message: 'git commit -m "fix(pricing): quantize decimal discount arithmetic to prevent rounding errors"' },
          { tag: 'ORCHESTRATOR', color: 'text-blue-400', message: 'Telemetry ping: Worker latency 11ms, GPU VRAM 3.2GB / 24GB.' },
        ];
        const randomItem = simulatedPool[Math.floor(Math.random() * simulatedPool.length)];
        return [...prev.slice(-30), { id: nextId, time: now, ...randomItem }];
      });
    }, 2800);

    return () => clearInterval(streamInterval);
  }, [isOpen, isPlaying]);

  useEffect(() => {
    if (autoScroll && terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-4xl h-[82vh] rounded-2xl bg-[#090e1f] border border-[#20315e] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#18264c] bg-[#0c142b] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Radio className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">Live Agent Activity Streaming</h2>
                <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-[10px] font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" /> LIVE STREAM
                </span>
              </div>
              <p className="text-xs text-slate-400">Watch real-time reasoning, tool executions, and verification loops</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                isPlaying 
                  ? 'bg-amber-500/20 border-amber-500/40 text-amber-300' 
                  : 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
              }`}
            >
              {isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
              <span>{isPlaying ? 'Pause Feed' : 'Resume Feed'}</span>
            </button>
            <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Live Metrics Ribbon */}
        <div className="px-6 py-2.5 bg-[#070b18] border-b border-[#162345] flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-6">
            <span className="text-slate-400 flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-amber-400" /> Speed: <span className="text-white">68 tokens/s</span>
            </span>
            <span className="text-slate-400 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" /> Active Pod: <span className="text-white">pod-us-east-7</span>
            </span>
            <span className="text-slate-400">
              Session: <span className="text-blue-400">0fed28a5</span>
            </span>
          </div>

          <label className="flex items-center gap-2 cursor-pointer text-slate-400 hover:text-white select-none">
            <input 
              type="checkbox" 
              checked={autoScroll} 
              onChange={(e) => setAutoScroll(e.target.checked)} 
              className="rounded bg-[#162345] border-slate-600 text-blue-500 focus:ring-0"
            />
            <span className="text-[11px]">Auto-scroll</span>
          </label>
        </div>

        {/* Terminal Window */}
        <div className="flex-1 p-5 bg-[#050813] font-mono text-xs overflow-y-auto space-y-2 select-text">
          {logs.map((log) => (
            <div key={log.id} className="flex items-start gap-3 hover:bg-white/[0.02] p-1 rounded transition-colors">
              <span className="text-slate-500 select-none flex-shrink-0 text-[11px]">{log.time}</span>
              <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold tracking-wider bg-white/5 border border-white/10 flex-shrink-0 ${log.color}`}>
                [{log.tag}]
              </span>
              <span className="text-slate-200 leading-relaxed break-all">{log.message}</span>
            </div>
          ))}
          <div ref={terminalEndRef} />
        </div>

        {/* Footer */}
        <div className="p-3 px-6 bg-[#0c142b] border-t border-[#18264c] flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-slate-400">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>Autonomous agent pipeline operational</span>
          </div>
          <button 
            onClick={() => setLogs(logs.slice(0, 3))}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#142145] hover:bg-[#1a2d5e] text-slate-300 text-xs transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Clear Buffer</span>
          </button>
        </div>
      </div>
    </div>
  );
};
