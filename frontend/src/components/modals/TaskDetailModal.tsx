import React from 'react';
import { CheckCircle2, XCircle, Clock, GitBranch, GitCommit, FileCode, X, Play, RotateCcw } from 'lucide-react';
import { TaskHistoryItem } from '../../types';

interface TaskDetailModalProps {
  task: TaskHistoryItem | null;
  onClose: () => void;
  onRerun: (task: TaskHistoryItem) => void;
}

export const TaskDetailModal: React.FC<TaskDetailModalProps> = ({ task, onClose, onRerun }) => {
  if (!task) return null;

  const isVerified = task.status === 'Verified';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-2xl rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
              isVerified ? 'bg-emerald-500/20 border border-emerald-500/30 text-emerald-400' : 'bg-rose-500/20 border border-rose-500/30 text-rose-400'
            }`}>
              {isVerified ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">{task.title}</h2>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono border ${
                  isVerified ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border-rose-500/30'
                }`}>
                  {task.status}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">{task.timestamp} · Task ID: {task.id}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs text-slate-300">
          {/* Metadata pill ribbon */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 rounded-xl bg-[#0e1633] border border-[#1b2b52]">
              <span className="text-slate-400 text-[11px] block">Duration</span>
              <span className="text-sm font-bold text-white font-mono mt-0.5">{task.duration || '2m 14s'}</span>
            </div>
            <div className="p-3 rounded-xl bg-[#0e1633] border border-[#1b2b52]">
              <span className="text-slate-400 text-[11px] block">Branch</span>
              <span className="text-xs font-mono text-cyan-300 truncate mt-0.5 flex items-center gap-1">
                <GitBranch className="w-3 h-3" /> {task.branch || 'main'}
              </span>
            </div>
            <div className="p-3 rounded-xl bg-[#0e1633] border border-[#1b2b52]">
              <span className="text-slate-400 text-[11px] block">Commit</span>
              <span className="text-xs font-mono text-purple-300 mt-0.5 flex items-center gap-1">
                <GitCommit className="w-3 h-3" /> {task.commitHash || 'a9f24c1'}
              </span>
            </div>
          </div>

          {/* Description */}
          <div className="p-4 rounded-xl bg-[#0d152f] border border-[#1a2850] space-y-1.5">
            <h3 className="font-semibold text-white">Execution Summary</h3>
            <p className="text-slate-300 leading-relaxed">
              {task.description || 'Autonomous agent inspected the codebase, reproduced the issue with targeted test cases, applied verified code diffs, and executed regression checks.'}
            </p>
          </div>

          {/* Diagnostics / Steps */}
          <div className="space-y-2">
            <h3 className="font-semibold text-white">Verification Status</h3>
            <div className="p-3 rounded-xl bg-[#070b18] border border-[#172346] font-mono text-[11px] space-y-1 text-slate-300">
              <p className="text-emerald-400">✓ Unit tests: 48 passed, 0 failed</p>
              <p className="text-emerald-400">✓ Static type checker: Clean</p>
              <p className="text-emerald-400">✓ Regression suite: Verified zero side-effects</p>
              <p className="text-slate-400">→ Code patch deployed to remote testing branch</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 px-6 bg-[#0c142b] border-t border-[#17254d] flex items-center justify-between">
          <button
            onClick={() => onRerun(task)}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-[#142145] hover:bg-[#1a2d5e] text-xs font-medium text-slate-300 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Load into Workspace</span>
          </button>

          <button onClick={onClose} className="px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
