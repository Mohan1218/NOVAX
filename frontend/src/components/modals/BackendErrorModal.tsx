import React, { useState } from 'react';
import { 
  AlertCircle, 
  RefreshCw, 
  Terminal, 
  Copy, 
  Check, 
  X, 
  ExternalLink,
  PlayCircle,
  ServerOff
} from 'lucide-react';

interface BackendErrorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRetry: () => void;
  onStartSimulation: () => void;
  isRetrying: boolean;
}

export const BackendErrorModal: React.FC<BackendErrorModalProps> = ({
  isOpen,
  onClose,
  onRetry,
  onStartSimulation,
  isRetrying,
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const errorLogs = `[15:20:18] NOVAX-CLIENT: Initiating WebSocket handshake with orchestrator...
[15:20:18] NOVAX-CLIENT: Target: ws://localhost:8000/agent/ws
[15:20:19] NOVAX-CLIENT: TCP Connection attempt to 127.0.0.1:8000
[15:20:20] NOVAX-NET: connect ECONNREFUSED 127.0.0.1:8000
[15:20:20] NOVAX-CORE: WebSocket connection to 'ws://localhost:8000/agent/ws' failed: Error in connection establishment: net::ERR_CONNECTION_REFUSED
[15:20:20] NOVAX-AGENT: Disconnected. Standalone UI mode active.`;

  const copyLog = () => {
    navigator.clipboard.writeText(errorLogs);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-in fade-in duration-200">
      <div 
        className="w-full max-w-xl rounded-2xl bg-[#0c1224] border border-rose-500/40 shadow-[0_0_50px_rgba(244,63,94,0.25)] overflow-hidden animate-in zoom-in-95 duration-200"
        role="dialog"
      >
        {/* Header */}
        <div className="p-5 border-b border-[#1b2545] bg-gradient-to-r from-rose-950/40 via-[#0f1730] to-[#0c1224] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 shadow-sm">
              <ServerOff className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                Backend Connection Failed
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">
                  ERR_CONNECTION_REFUSED
                </span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Unable to connect to NOVAX Orchestrator at <code className="text-rose-300 font-mono">ws://localhost:8000/agent/ws</code>
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 space-y-4">
          {/* Explanation Alert */}
          <div className="p-3.5 rounded-xl bg-[#141b36] border border-[#22315c] text-xs text-slate-300 space-y-1.5">
            <p className="font-semibold text-slate-200 flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 text-amber-400" />
              The autonomous backend agent daemon is not currently running.
            </p>
            <p className="text-slate-400 leading-relaxed">
              This React + Vite frontend requires the Python/Docker orchestrator service to parse repositories and execute real shell commands. You can start the local orchestrator or test the interface using the simulated demo mode.
            </p>
          </div>

          {/* Diagnostic Log Output */}
          <div>
            <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5">
              <span className="flex items-center gap-1.5 font-mono text-[11px]">
                <Terminal className="w-3.5 h-3.5 text-cyan-400" /> Connection Telemetry Log
              </span>
              <button
                onClick={copyLog}
                className="flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 transition-colors"
              >
                {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copied ? 'Copied' : 'Copy Log'}</span>
              </button>
            </div>
            <pre className="p-3 rounded-xl bg-[#070b18] border border-[#192447] text-[11px] font-mono text-rose-300/90 overflow-x-auto max-h-36 leading-relaxed select-text">
              {errorLogs}
            </pre>
          </div>

          {/* Quick CLI command helper */}
          <div className="p-3 rounded-xl bg-[#090f23] border border-[#1a2850] flex items-center justify-between">
            <div className="min-w-0">
              <p className="text-[11px] text-slate-400 font-mono">To start local orchestrator daemon:</p>
              <code className="text-xs text-cyan-300 font-mono">novax serve --host 127.0.0.1 --port 8000</code>
            </div>
            <span className="text-[10px] text-slate-500 font-mono px-2 py-1 rounded bg-[#111c38]">CLI</span>
          </div>
        </div>

        {/* Modal Footer Actions */}
        <div className="p-4 border-t border-[#1b2545] bg-[#090f23] flex flex-wrap items-center justify-between gap-3">
          <button
            onClick={onStartSimulation}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium text-cyan-300 bg-cyan-950/40 hover:bg-cyan-900/50 border border-cyan-500/30 transition-all shadow-sm"
          >
            <PlayCircle className="w-4 h-4 text-cyan-400" />
            <span>Launch Interactive Demo Mode</span>
          </button>

          <div className="flex items-center gap-2.5">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-300 hover:text-white hover:bg-[#162347] transition-colors"
            >
              Dismiss
            </button>
            <button
              onClick={onRetry}
              disabled={isRetrying}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-md transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRetrying ? 'animate-spin' : ''}`} />
              <span>{isRetrying ? 'Reconnecting...' : 'Retry Connection'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
