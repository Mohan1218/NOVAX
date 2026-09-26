import React, { useState } from 'react';
import { Settings, Cpu, Shield, Key, Database, Check, X, Save } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaveToast: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose, onSaveToast }) => {
  const [model, setModel] = useState('novax-4.1');
  const [orchestratorUrl, setOrchestratorUrl] = useState('ws://localhost:8000/agent/ws');
  const [autonomousMode, setAutonomousMode] = useState(true);
  const [sandboxIsolation, setSandboxIsolation] = useState(true);
  const [apiKey, setApiKey] = useState('nvx_live_99f28a501cde9941a87b');

  if (!isOpen) return null;

  const handleSave = () => {
    onSaveToast();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-2xl max-h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-slate-700/30 border border-slate-600/40 flex items-center justify-center text-slate-300">
              <Settings className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">NOVAX Workspace Settings</h2>
              <p className="text-xs text-slate-400">Configure AI model engine, sandbox limits, and orchestrator daemon</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs text-slate-300">
          {/* AI Model Selection */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold text-white">Default Autonomous Model Engine</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-[#0e1735] border border-[#1b2b52] text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
            >
              <option value="novax-4.1">NOVAX-Reasoner-v4.1 (Specialized Autonomous Software Engineer)</option>
              <option value="claude-3-5">Claude 3.5 Sonnet (Direct API)</option>
              <option value="gpt-4o">GPT-4o (Direct API)</option>
              <option value="deepseek-local">DeepSeek-Coder-V2 (Local Ollama:11434)</option>
            </select>
          </div>

          {/* Orchestrator WebSocket Host */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold text-white">Orchestrator Backend WebSocket URI</label>
            <input
              type="text"
              value={orchestratorUrl}
              onChange={(e) => setOrchestratorUrl(e.target.value)}
              placeholder="ws://localhost:8000/agent/ws"
              className="w-full px-3 py-2 rounded-xl bg-[#0e1735] border border-[#1b2b52] text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
            />
            <span className="text-[11px] text-slate-400">
              Default connection target for "Start Working" button.
            </span>
          </div>

          {/* API Key */}
          <div className="space-y-2">
            <label className="block text-xs font-semibold text-white">NOVAX Authentication Key</label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full px-3 py-2 rounded-xl bg-[#0e1735] border border-[#1b2b52] text-xs text-white focus:outline-none focus:border-blue-500 font-mono"
            />
          </div>

          {/* Toggles */}
          <div className="p-4 rounded-xl bg-[#0d1633] border border-[#1b2b52] space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <span className="font-semibold text-white block">Full Autonomous Patch Deployment</span>
                <span className="text-slate-400 text-[11px]">Automatically git commit and push when all tests pass</span>
              </div>
              <input
                type="checkbox"
                checked={autonomousMode}
                onChange={(e) => setAutonomousMode(e.target.checked)}
                className="rounded bg-[#1b2b52] border-slate-600 text-blue-600 focus:ring-0 w-4 h-4 cursor-pointer"
              />
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-[#17254d]">
              <div>
                <span className="font-semibold text-white block">gVisor Container Sandbox Isolation</span>
                <span className="text-slate-400 text-[11px]">Enforce unprivileged memory limits and isolated network egress</span>
              </div>
              <input
                type="checkbox"
                checked={sandboxIsolation}
                onChange={(e) => setSandboxIsolation(e.target.checked)}
                className="rounded bg-[#1b2b52] border-slate-600 text-blue-600 focus:ring-0 w-4 h-4 cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 px-6 bg-[#0c142b] border-t border-[#17254d] flex items-center justify-between">
          <button onClick={onClose} className="px-4 py-1.5 rounded-lg text-slate-400 hover:text-white text-xs font-medium">
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs shadow-md"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save Preferences</span>
          </button>
        </div>
      </div>
    </div>
  );
};
