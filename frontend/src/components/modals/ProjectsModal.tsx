import React, { useState } from 'react';
import { Folder, GitBranch, Star, Clock, Plus, ExternalLink, X, Check } from 'lucide-react';
import { Repository } from '../../types';
import { MOCK_REPOSITORIES } from '../../data/mockData';

interface ProjectsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectProject: (repo: Repository) => void;
}

export const ProjectsModal: React.FC<ProjectsModalProps> = ({ isOpen, onClose, onSelectProject }) => {
  const [projects] = useState<Repository[]>(MOCK_REPOSITORIES);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-3xl max-h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Folder className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Connected Projects & Repositories</h2>
              <p className="text-xs text-slate-400">Manage autonomous workspace bindings and git sync policies</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* List of projects */}
        <div className="p-6 overflow-y-auto space-y-3 flex-1 text-xs">
          {projects.map((proj) => (
            <div
              key={proj.id}
              className="p-4 rounded-xl bg-[#0d1633] border border-[#1b2b52] hover:border-[#2b417d] transition-all flex items-center justify-between"
            >
              <div className="space-y-1.5">
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-sm text-white">{proj.name}</h3>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#1b2b52] text-slate-300">
                    {proj.language}
                  </span>
                </div>
                <p className="text-slate-400 font-mono text-[11px]">{proj.fullPath}</p>
                <div className="flex items-center gap-4 text-slate-400 text-[11px]">
                  <span className="flex items-center gap-1"><GitBranch className="w-3 h-3" /> {proj.branch}</span>
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> Updated {proj.updatedAt}</span>
                  <span className="flex items-center gap-1"><Star className="w-3 h-3 text-amber-400" /> {proj.stars} stars</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    onSelectProject(proj);
                    onClose();
                  }}
                  className="px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-xs transition-colors shadow-sm"
                >
                  Open in Workspace
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-4 px-6 bg-[#0c142b] border-t border-[#17254d] flex justify-end">
          <button onClick={onClose} className="px-4 py-1.5 rounded-lg bg-[#142145] hover:bg-[#1a2d5e] text-slate-300 text-xs font-medium">
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
