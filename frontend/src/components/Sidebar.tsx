import React from 'react';
import { 
  LayoutDashboard, 
  Plus, 
  Folder, 
  History as HistoryIcon, 
  FileText, 
  BarChart3, 
  Settings, 
  CheckCircle2, 
  XCircle, 
  Moon, 
  Sun,
  ChevronRight,
  Clock
} from 'lucide-react';
import { TaskHistoryItem, NavModalType } from '../types';

interface SidebarProps {
  isOpen: boolean;
  activeNav: string;
  onSelectNav: (nav: string) => void;
  onNewTask: () => void;
  onOpenNavModal: (type: NavModalType) => void;
  taskHistory: TaskHistoryItem[];
  onSelectTask: (task: TaskHistoryItem) => void;
  onViewAllHistory: () => void;
  isDarkMode: boolean;
  onToggleTheme: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  activeNav,
  onSelectNav,
  onNewTask,
  onOpenNavModal,
  taskHistory,
  onSelectTask,
  onViewAllHistory,
  isDarkMode,
  onToggleTheme,
}) => {
  return (
    <aside 
      className={`fixed lg:static top-0 left-0 bottom-0 z-30 w-72 bg-[#080d1e] border-r border-[#15203d] flex flex-col justify-between transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      }`}
    >
      {/* Top Part: Branding & Primary Nav */}
      <div className="flex flex-col flex-1 overflow-y-auto px-4 pt-5 pb-3">
        {/* NOVAX Brand Header matching screenshot */}
        <div className="flex items-center gap-3 px-2 mb-6 cursor-pointer" onClick={() => onSelectNav('Dashboard')}>
          {/* Stylized Logo 'N' */}
          <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 via-indigo-600 to-purple-600 flex items-center justify-center p-[2px] shadow-[0_0_18px_rgba(59,130,246,0.35)]">
            <div className="w-full h-full bg-[#080d1e] rounded-[10px] flex items-center justify-center">
              <svg viewBox="0 0 32 32" className="w-6 h-6 text-white drop-shadow-[0_0_8px_#38bdf8]">
                <path 
                  d="M8 6 L8 26 L12 26 L20 12 L20 26 L24 26 L24 6 L20 6 L12 20 L12 6 Z" 
                  fill="url(#logoNgrad)" 
                />
                <defs>
                  <linearGradient id="logoNgrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#38bdf8" />
                    <stop offset="100%" stopColor="#a855f7" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>

          <div>
            <h1 className="text-xl font-bold tracking-wider text-white flex items-center gap-1.5 font-sans">
              NOVAX
            </h1>
            <p className="text-[11px] text-slate-400 font-normal leading-tight">
              Autonomous Software Engineer
            </p>
          </div>
        </div>

        {/* Primary Navigation List */}
        <nav className="space-y-1.5 mb-6">
          {/* Dashboard */}
          <button
            onClick={() => onSelectNav('Dashboard')}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
              activeNav === 'Dashboard' 
                ? 'text-white bg-[#101b38] border border-[#1e2f5d]' 
                : 'text-slate-300 hover:text-white hover:bg-[#0f1730]'
            }`}
          >
            <LayoutDashboard className="w-4 h-4 text-slate-400" />
            <span>Dashboard</span>
          </button>

          {/* + New Task (Highlighted Pill Button) */}
          <button
            onClick={onNewTask}
            className="w-full flex items-center gap-2.5 px-4 py-2.5 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 shadow-md shadow-blue-600/25 transition-all transform active:scale-[0.98] group"
          >
            <Plus className="w-4 h-4 transition-transform group-hover:rotate-90 duration-200" />
            <span>New Task</span>
          </button>

          {/* Projects */}
          <button
            onClick={() => onOpenNavModal('projects')}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-[#0f1730] transition-colors"
          >
            <Folder className="w-4 h-4 text-slate-400" />
            <span>Projects</span>
          </button>

          {/* History */}
          <button
            onClick={() => onOpenNavModal('history')}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-[#0f1730] transition-colors"
          >
            <HistoryIcon className="w-4 h-4 text-slate-400" />
            <span>History</span>
          </button>

          {/* Reports */}
          <button
            onClick={() => onOpenNavModal('reports')}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-[#0f1730] transition-colors"
          >
            <FileText className="w-4 h-4 text-slate-400" />
            <span>Reports</span>
          </button>

          {/* Analytics */}
          <button
            onClick={() => onOpenNavModal('analytics')}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-[#0f1730] transition-colors"
          >
            <BarChart3 className="w-4 h-4 text-slate-400" />
            <span>Analytics</span>
          </button>

          {/* Settings */}
          <button
            onClick={() => onOpenNavModal('settings')}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:text-white hover:bg-[#0f1730] transition-colors"
          >
            <Settings className="w-4 h-4 text-slate-400" />
            <span>Settings</span>
          </button>
        </nav>

        {/* Task History Section */}
        <div className="pt-3 border-t border-[#141e3a]">
          <div className="flex items-center justify-between px-2 mb-3">
            <h2 className="text-sm font-bold text-white tracking-wide">
              Task History
            </h2>
            <button
              onClick={onViewAllHistory}
              className="text-xs text-blue-400 hover:text-blue-300 hover:underline font-medium"
            >
              View All
            </button>
          </div>

          {/* List of Tasks from screenshot */}
          <div className="space-y-1">
            {taskHistory.map((task) => (
              <div
                key={task.id}
                onClick={() => onSelectTask(task)}
                className="group p-2 rounded-xl hover:bg-[#0f1938] transition-all cursor-pointer border border-transparent hover:border-[#1c2c59]"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2.5 min-w-0">
                    {/* Status icon: Green check for Verified, Red X for Failed */}
                    {task.status === 'Verified' ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-500 flex-shrink-0 mt-0.5" />
                    )}
                    <div className="min-w-0">
                      <p className="text-xs font-medium text-slate-200 truncate group-hover:text-white transition-colors">
                        {task.title}
                      </p>
                      <p className="text-[11px] text-slate-400 mt-0.5">
                        {task.timestamp}
                      </p>
                    </div>
                  </div>

                  {/* Right Status Badge: Verified (green text) / Failed (red text) */}
                  <span 
                    className={`text-[11px] font-medium flex-shrink-0 ${
                      task.status === 'Verified' ? 'text-emerald-400' : 'text-rose-500'
                    }`}
                  >
                    {task.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Section: Theme Switcher matching screenshot */}
      <div className="p-4 border-t border-[#141e3a] bg-[#070b18]/60">
        <div className="flex items-center justify-between">
          <div 
            onClick={onToggleTheme}
            className="flex items-center bg-[#0d162f] p-1 rounded-xl border border-[#19274e] cursor-pointer"
            title="Toggle theme appearance"
          >
            <div className={`p-1.5 rounded-lg transition-all ${isDarkMode ? 'bg-[#1b2b54] text-cyan-400 shadow-sm' : 'text-slate-400'}`}>
              <Moon className="w-3.5 h-3.5" />
            </div>
            <div className={`p-1.5 rounded-lg transition-all ${!isDarkMode ? 'bg-[#1b2b54] text-amber-400 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}>
              <Sun className="w-3.5 h-3.5" />
            </div>
          </div>

          <span className="text-[11px] font-mono text-slate-500">
            NOVAX v4.1
          </span>
        </div>
      </div>
    </aside>
  );
};
