import React, { useState } from 'react';
import { Folder, Search, GitBranch, Star, Check, X, Plus, ExternalLink } from 'lucide-react';
import { Repository } from '../../types';
import { MOCK_REPOSITORIES } from '../../data/mockData';

interface SelectRepositoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedRepo: Repository | null;
  onSelectRepo: (repo: Repository) => void;
}

export const SelectRepositoryModal: React.FC<SelectRepositoryModalProps> = ({
  isOpen,
  onClose,
  selectedRepo,
  onSelectRepo,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [customRepoUrl, setCustomRepoUrl] = useState('');
  const [showAddCustom, setShowAddCustom] = useState(false);
  const [repos, setRepos] = useState<Repository[]>(MOCK_REPOSITORIES);

  if (!isOpen) return null;

  const filteredRepos = repos.filter(r => 
    r.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.fullPath.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.language.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAddCustom = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customRepoUrl.trim()) return;
    const name = customRepoUrl.split('/').pop()?.replace('.git', '') || 'custom-repo';
    const newRepo: Repository = {
      id: `repo-${Date.now()}`,
      name: name,
      fullPath: customRepoUrl,
      branch: 'main',
      branches: ['main', 'dev'],
      stars: 1,
      language: 'TypeScript',
      updatedAt: 'Just now'
    };
    setRepos([newRepo, ...repos]);
    onSelectRepo(newRepo);
    setCustomRepoUrl('');
    setShowAddCustom(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-xl rounded-2xl bg-[#0c1328] border border-[#203260] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200 flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="p-5 border-b border-[#18264e] flex items-center justify-between bg-[#0e1732]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Folder className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Select Repository</h2>
              <p className="text-xs text-slate-400">Connect a codebase for autonomous analysis and fixes</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-4 border-b border-[#18264e] bg-[#090f22] flex items-center gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search repositories by name, language..."
              className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#111c3b] border border-[#1f2f5c] text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button
            onClick={() => setShowAddCustom(!showAddCustom)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-xs font-medium text-blue-300 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Repo</span>
          </button>
        </div>

        {/* Add Custom Repo Accordion */}
        {showAddCustom && (
          <form onSubmit={handleAddCustom} className="p-4 border-b border-[#18264e] bg-[#0d1631] space-y-3">
            <label className="block text-xs font-medium text-slate-300">
              Clone from GitHub / GitLab / Bitbucket
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={customRepoUrl}
                onChange={(e) => setCustomRepoUrl(e.target.value)}
                placeholder="https://github.com/organization/repository"
                className="flex-1 px-3 py-1.5 rounded-xl bg-[#111c3b] border border-[#1f2f5c] text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
              <button
                type="submit"
                className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold"
              >
                Import
              </button>
            </div>
          </form>
        )}

        {/* Repositories List */}
        <div className="p-4 overflow-y-auto space-y-2 flex-1">
          {filteredRepos.map((repo) => {
            const isSelected = selectedRepo?.id === repo.id;
            return (
              <div
                key={repo.id}
                onClick={() => {
                  onSelectRepo(repo);
                  onClose();
                }}
                className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                  isSelected
                    ? 'bg-blue-950/40 border-blue-500/60 shadow-[0_0_15px_rgba(59,130,246,0.2)]'
                    : 'bg-[#0f1836] border-[#1b2b52] hover:border-blue-500/30 hover:bg-[#142045]'
                }`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-8 h-8 rounded-lg bg-[#142145] border border-[#243768] flex items-center justify-center text-slate-300">
                    <Folder className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-xs text-white truncate">{repo.name}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#1b2a52] text-slate-300 font-mono">
                        {repo.language}
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mt-1 text-[11px] text-slate-400 font-mono">
                      <span className="flex items-center gap-1">
                        <GitBranch className="w-3 h-3 text-slate-500" /> {repo.branch}
                      </span>
                      <span>Updated {repo.updatedAt}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {isSelected ? (
                    <span className="flex items-center gap-1 px-2 py-1 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-medium border border-emerald-500/30">
                      <Check className="w-3.5 h-3.5" /> Selected
                    </span>
                  ) : (
                    <button className="px-3 py-1.5 rounded-lg bg-[#142247] hover:bg-blue-600 hover:text-white text-xs text-slate-300 transition-colors">
                      Select
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-[#18264e] bg-[#090f22] flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl text-xs font-medium text-slate-400 hover:text-white transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
