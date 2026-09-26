import React, { useState } from 'react';
import { History, Search, CheckCircle2, XCircle, ArrowUpRight, X, Filter } from 'lucide-react';
import { TaskHistoryItem } from '../../types';

interface HistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  tasks: TaskHistoryItem[];
  onSelectTask: (task: TaskHistoryItem) => void;
}

export const HistoryModal: React.FC<HistoryModalProps> = ({
  isOpen,
  onClose,
  tasks,
  onSelectTask,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'All' | 'Verified' | 'Failed'>('All');

  if (!isOpen) return null;

  const filteredTasks = tasks.filter((t) => {
    const matchesSearch = t.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.timestamp.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'All' ? true : t.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-4xl max-h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Full Task Execution History</h2>
              <p className="text-xs text-slate-400">All autonomous debug, patch, and verification runs</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search & Filter Toolbar */}
        <div className="p-4 px-6 border-b border-[#162348] bg-[#080d21] flex flex-wrap items-center justify-between gap-3">
          <div className="relative flex-1 max-w-xs">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search historical runs..."
              className="w-full pl-9 pr-3 py-1.5 rounded-lg bg-[#0e1735] border border-[#1b2b52] text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="flex items-center gap-1.5 bg-[#0e1735] p-1 rounded-lg border border-[#1b2b52]">
            {(['All', 'Verified', 'Failed'] as const).map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  filterStatus === status ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                {status}
              </button>
            ))}
          </div>
        </div>

        {/* Task List */}
        <div className="p-6 overflow-y-auto space-y-2 flex-1 text-xs">
          {filteredTasks.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              No tasks matching query.
            </div>
          ) : (
            filteredTasks.map((task) => (
              <div
                key={task.id}
                onClick={() => {
                  onSelectTask(task);
                  onClose();
                }}
                className="p-3.5 rounded-xl bg-[#0d1633] border border-[#1b2b52] hover:border-blue-500/40 hover:bg-[#121f47] transition-all cursor-pointer flex items-center justify-between group"
              >
                <div className="flex items-center gap-3 min-w-0">
                  {task.status === 'Verified' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  ) : (
                    <XCircle className="w-4 h-4 text-rose-500 flex-shrink-0" />
                  )}
                  <div className="min-w-0">
                    <h4 className="font-semibold text-white group-hover:text-blue-300 transition-colors truncate">
                      {task.title}
                    </h4>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      {task.timestamp} · {task.branch || 'main'} · {task.duration || '2m 30s'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`text-[11px] font-semibold ${
                    task.status === 'Verified' ? 'text-emerald-400' : 'text-rose-500'
                  }`}>
                    {task.status}
                  </span>
                  <ArrowUpRight className="w-4 h-4 text-slate-500 group-hover:text-white transition-colors" />
                </div>
              </div>
            ))
          )}
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
