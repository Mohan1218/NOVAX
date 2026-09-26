import React, { useState } from 'react';
import { BookOpen, Search, Code, Terminal, Cpu, ArrowRight, ExternalLink, X } from 'lucide-react';

interface DocumentationModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DocumentationModal: React.FC<DocumentationModalProps> = ({ isOpen, onClose }) => {
  const [selectedTopic, setSelectedTopic] = useState('quickstart');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-4xl h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">NOVAX Documentation & Developer Guide</h2>
              <p className="text-xs text-slate-400">Architecture, SDK reference, and autonomous agent orchestration manual</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar */}
          <div className="w-60 border-r border-[#17254d] bg-[#070c1e] p-3 space-y-1 text-xs">
            <button
              onClick={() => setSelectedTopic('quickstart')}
              className={`w-full text-left px-3 py-2 rounded-lg font-medium transition-colors ${
                selectedTopic === 'quickstart' ? 'bg-blue-600/30 text-cyan-300 font-semibold' : 'text-slate-300 hover:bg-[#111c38]'
              }`}
            >
              1. Quickstart & Overview
            </button>
            <button
              onClick={() => setSelectedTopic('orchestrator')}
              className={`w-full text-left px-3 py-2 rounded-lg font-medium transition-colors ${
                selectedTopic === 'orchestrator' ? 'bg-blue-600/30 text-cyan-300 font-semibold' : 'text-slate-300 hover:bg-[#111c38]'
              }`}
            >
              2. Agent Orchestration Loop
            </button>
            <button
              onClick={() => setSelectedTopic('cli')}
              className={`w-full text-left px-3 py-2 rounded-lg font-medium transition-colors ${
                selectedTopic === 'cli' ? 'bg-blue-600/30 text-cyan-300 font-semibold' : 'text-slate-300 hover:bg-[#111c38]'
              }`}
            >
              3. NOVAX CLI Reference
            </button>
            <button
              onClick={() => setSelectedTopic('sandbox')}
              className={`w-full text-left px-3 py-2 rounded-lg font-medium transition-colors ${
                selectedTopic === 'sandbox' ? 'bg-blue-600/30 text-cyan-300 font-semibold' : 'text-slate-300 hover:bg-[#111c38]'
              }`}
            >
              4. gVisor Isolated Sandbox
            </button>
          </div>

          {/* Right Reading Pane */}
          <div className="flex-1 p-6 overflow-y-auto space-y-4 text-xs text-slate-300 leading-relaxed select-text">
            {selectedTopic === 'quickstart' && (
              <div className="space-y-4">
                <h3 className="text-base font-bold text-white">Welcome to NOVAX</h3>
                <p>
                  NOVAX is an Autonomous Software Engineer that reads natural language bug reports, scans codebases, replicates failures, synthesizes precision code patches, and verifies fixes with automated test suites.
                </p>
                <div className="p-4 rounded-xl bg-[#0d1633] border border-[#1b2b52] space-y-2">
                  <h4 className="font-semibold text-white">Key Capabilities:</h4>
                  <ul className="list-disc pl-4 space-y-1 text-slate-300">
                    <li><strong className="text-cyan-300">Deep AST Comprehension:</strong> Indexes semantic references and types across your repo.</li>
                    <li><strong className="text-cyan-300">Reproduce-Before-Patch:</strong> Formulates reproduction test cases before writing code.</li>
                    <li><strong className="text-cyan-300">Zero Regression Guarantee:</strong> Enforces automated regression test execution.</li>
                  </ul>
                </div>
              </div>
            )}

            {selectedTopic === 'orchestrator' && (
              <div className="space-y-4">
                <h3 className="text-base font-bold text-white">Autonomous Agent Loop</h3>
                <p>
                  The agent execution cycle operates across four distinct deterministic states:
                </p>
                <pre className="p-4 rounded-xl bg-[#060914] border border-[#162348] font-mono text-[11px] text-cyan-300">
{`+---------------------+
|  Ingest Bug Report  |
+----------+----------+
           |
           v
+---------------------+      +---------------------+
| Localize AST Nodes  +----->| Synthesize Test Case|
+---------------------+      +----------+----------+
                                        |
                                        v
                             +---------------------+
                             | Execute Container   |
                             |   Verified Patch    |
                             +---------------------+`}
                </pre>
              </div>
            )}

            {selectedTopic === 'cli' && (
              <div className="space-y-4">
                <h3 className="text-base font-bold text-white">NOVAX CLI Commands</h3>
                <div className="space-y-3 font-mono text-[11px]">
                  <div className="p-3 rounded-lg bg-[#070c1e] border border-[#17254d]">
                    <span className="text-emerald-400">$ novax serve --port 8000</span>
                    <p className="text-slate-400 font-sans mt-1">Starts local WebSocket orchestrator daemon.</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#070c1e] border border-[#17254d]">
                    <span className="text-emerald-400">$ novax run "Fix cart calculation bug"</span>
                    <p className="text-slate-400 font-sans mt-1">Dispatches autonomous agent directly in current directory.</p>
                  </div>
                </div>
              </div>
            )}

            {selectedTopic === 'sandbox' && (
              <div className="space-y-4">
                <h3 className="text-base font-bold text-white">Sandbox Security & Isolation</h3>
                <p>
                  All bash commands, test executions, and dependency installations occur within an unprivileged gVisor sandbox container, safeguarding host systems against side-effects.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 px-6 bg-[#0c142b] border-t border-[#17254d] flex justify-end">
          <button onClick={onClose} className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
