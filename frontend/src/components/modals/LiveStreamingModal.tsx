import React, { useState, useEffect, useRef } from 'react';
import { Radio, Play, Pause, RotateCcw, X, Zap, Cpu, CheckCircle } from 'lucide-react';

interface LiveStreamingModalProps {
  isOpen: boolean;
  onClose: () => void;
  jobId?: string | null;
  jobState?: any;
}

export const LiveStreamingModal: React.FC<LiveStreamingModalProps> = ({ isOpen, onClose, jobId, jobState }) => {
  const [isPlaying, setIsPlaying] = useState(true);
  const [autoScroll, setAutoScroll] = useState(true);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  const defaultLogs = [
    { id: 1, time: '15:20:01', tag: 'ORCHESTRATOR', color: 'text-blue-400', message: 'Task initialized: Autonomous session 0fed28a5 allocated to worker.' },
    { id: 2, time: '15:20:03', tag: 'INSPECTING', color: 'text-cyan-400', message: 'Inspecting workspace "demo_project". Discovered 10 execution tools.' },
    { id: 3, time: '15:20:04', tag: 'TESTING', color: 'text-purple-400', message: 'Running baseline pytest suite on workspace.' },
    { id: 4, time: '15:20:06', tag: 'DIAGNOSING', color: 'text-amber-400', message: 'Analyzing test failure with Gemini 2.5 Flash model.' },
    { id: 5, time: '15:20:08', tag: 'FIXING', color: 'text-emerald-400', message: 'Applying patch fix candidate to calculator.py.' },
    { id: 6, time: '15:20:10', tag: 'VERIFYING', color: 'text-cyan-400', message: 'Re-running test suite: All tests passed cleanly.' },
  ];

  const logsToDisplay = (jobState?.logs && jobState.logs.length > 0)
    ? jobState.logs.map((log: any, idx: number) => ({
        id: idx + 1,
        time: typeof log.timestamp === 'number'
          ? new Date(log.timestamp * 1000).toLocaleTimeString()
          : (log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString()),
        tag: log.level ? log.level.toUpperCase() : 'AGENT',
        color: log.level === 'error'
          ? 'text-rose-400'
          : log.level === 'warning'
          ? 'text-amber-400'
          : 'text-emerald-400',
        message: log.message
      }))
    : defaultLogs;

  useEffect(() => {
    if (autoScroll && terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logsToDisplay, autoScroll]);

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
                <h2 className="text-base font-bold text-white">Live Agent Thought & Execution Stream</h2>
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
              <Zap className="w-3.5 h-3.5 text-amber-400" /> Model: <span className="text-white">Gemini 2.5 Flash</span>
            </span>
            <span className="text-slate-400 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" /> Progress: <span className="text-white">{jobState?.progress ?? 0}%</span>
            </span>
            <span className="text-slate-400">
              Job ID: <span className="text-blue-400">{jobId || jobState?.job_id || 'active'}</span>
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
          {logsToDisplay.map((log: any) => (
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
            <span>Autonomous agent pipeline operational — {jobState?.current_step || 'running'}</span>
          </div>
          <button 
            onClick={onClose}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#142145] hover:bg-[#1a2d5e] text-slate-300 text-xs transition-colors"
          >
            <span>Close Modal</span>
          </button>
        </div>
      </div>
    </div>
  );
};
