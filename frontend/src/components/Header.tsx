import React, { useState, useRef, useEffect } from 'react';
import { Menu, Bell, ChevronDown, Check, Wifi, Shield, Cpu, ExternalLink, X } from 'lucide-react';
import { MOCK_NOTIFICATIONS } from '../data/mockData';

interface HeaderProps {
  onToggleSidebar: () => void;
  onOpenSettings: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar, onOpenSettings }) => {
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [notifications, setNotifications] = useState(MOCK_NOTIFICATIONS);

  const notifRef = useRef<HTMLDivElement>(null);
  const userRef = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter(n => !n.read).length;

  // Close menus on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setShowNotifications(false);
      }
      if (userRef.current && !userRef.current.contains(e.target as Node)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  return (
    <header className="h-16 border-b border-[#141e38] bg-[#070b18]/80 backdrop-blur-md px-6 flex items-center justify-between z-20 sticky top-0">
      {/* Left: Hamburger menu toggle */}
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          aria-label="Toggle Sidebar"
          className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-[#111c38] transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
      </div>

      {/* Right: Badges, Notifications, User */}
      <div className="flex items-center gap-4">
        {/* System Online Badge */}
        <div className="relative">
          <button
            onClick={() => setShowStatusModal(!showStatusModal)}
            className="flex items-center gap-2.5 px-3 py-1.5 rounded-full bg-[#0d162e] border border-[#1b2a52] text-xs font-medium text-slate-200 hover:border-emerald-500/50 hover:bg-[#111e3f] transition-all shadow-sm"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="tracking-wide">System Online</span>
          </button>

          {/* System Online popover modal */}
          {showStatusModal && (
            <div className="absolute right-0 mt-2 w-72 rounded-xl bg-[#0e1730] border border-[#223565] shadow-2xl p-4 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="flex items-center justify-between pb-3 border-b border-[#1b2b52]">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 novax-badge-glow"></span>
                  <span className="font-semibold text-white text-sm">Orchestrator Cluster</span>
                </div>
                <button 
                  onClick={() => setShowStatusModal(false)}
                  className="text-slate-400 hover:text-white p-1"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-3 space-y-2.5 text-xs">
                <div className="flex justify-between items-center text-slate-300">
                  <span className="flex items-center gap-1.5 text-slate-400">
                    <Wifi className="w-3.5 h-3.5 text-cyan-400" /> Ping Latency
                  </span>
                  <span className="font-mono text-emerald-400 font-semibold">14 ms (Optimal)</span>
                </div>
                <div className="flex justify-between items-center text-slate-300">
                  <span className="flex items-center gap-1.5 text-slate-400">
                    <Cpu className="w-3.5 h-3.5 text-indigo-400" /> GPU Allocation
                  </span>
                  <span className="font-mono text-white font-semibold">16 / 16 Nodes active</span>
                </div>
                <div className="flex justify-between items-center text-slate-300">
                  <span className="flex items-center gap-1.5 text-slate-400">
                    <Shield className="w-3.5 h-3.5 text-blue-400" /> Sandbox Isolation
                  </span>
                  <span className="text-emerald-400 font-semibold">gVisor Containerized</span>
                </div>
                <div className="pt-2 border-t border-[#1b2b52] flex justify-between text-[11px] text-slate-400">
                  <span>Region: us-east-1</span>
                  <span className="text-blue-400">v4.1.0-prod</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Notifications Bell */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            aria-label="Notifications"
            className="relative p-2 text-slate-400 hover:text-white rounded-lg hover:bg-[#111c38] transition-colors"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_8px_#3b82f6]"></span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 rounded-xl bg-[#0e1730] border border-[#223565] shadow-2xl p-3 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="flex items-center justify-between pb-2 border-b border-[#1b2b52] px-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-white text-sm">Notifications</span>
                  {unreadCount > 0 && (
                    <span className="px-1.5 py-0.2 bg-blue-600/30 text-blue-400 border border-blue-500/40 text-[10px] rounded-full font-mono">
                      {unreadCount} new
                    </span>
                  )}
                </div>
                <button
                  onClick={markAllAsRead}
                  className="text-xs text-blue-400 hover:text-blue-300 font-medium"
                >
                  Mark all read
                </button>
              </div>

              <div className="mt-2 divide-y divide-[#18264d] max-h-72 overflow-y-auto">
                {notifications.map(n => (
                  <div key={n.id} className={`p-2 rounded-lg my-1 transition-colors ${n.read ? 'opacity-70 hover:bg-[#131f42]' : 'bg-[#142145] hover:bg-[#182752]'}`}>
                    <div className="flex items-start gap-2">
                      <span className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${n.type === 'success' ? 'bg-emerald-400' : 'bg-blue-400'}`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-slate-200 leading-snug">{n.title}</p>
                        <span className="text-[10px] text-slate-400 font-mono mt-0.5 block">{n.time}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* User Profile Dropdown */}
        <div className="relative" ref={userRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg hover:bg-[#111c38] transition-colors"
          >
            {/* Purple circle avatar matching screenshot */}
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-700 to-indigo-500 border border-purple-400/50 flex items-center justify-center font-bold text-white text-sm shadow-sm">
              N
            </div>
            <span className="text-xs font-medium text-slate-200">NOVAX User</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {/* User Menu Dropdown */}
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-56 rounded-xl bg-[#0e1730] border border-[#223565] shadow-2xl p-2 z-50">
              <div className="px-3 py-2 border-b border-[#1b2b52]">
                <p className="text-xs font-semibold text-white">novax-dev@enterprise.ai</p>
                <p className="text-[11px] text-slate-400">Autonomous Tier · Pro</p>
              </div>
              <div className="py-1">
                <button
                  onClick={() => { setShowUserMenu(false); onOpenSettings(); }}
                  className="w-full text-left px-3 py-2 text-xs text-slate-300 hover:text-white hover:bg-[#152347] rounded-lg transition-colors"
                >
                  Workspace Settings
                </button>
                <button
                  onClick={() => { setShowUserMenu(false); onOpenSettings(); }}
                  className="w-full text-left px-3 py-2 text-xs text-slate-300 hover:text-white hover:bg-[#152347] rounded-lg transition-colors"
                >
                  API Keys & Integrations
                </button>
                <a
                  href="https://github.com"
                  target="_blank"
                  rel="noreferrer"
                  className="w-full flex items-center justify-between px-3 py-2 text-xs text-slate-300 hover:text-white hover:bg-[#152347] rounded-lg transition-colors"
                >
                  <span>Connected GitHub</span>
                  <ExternalLink className="w-3 h-3 text-slate-400" />
                </a>
              </div>
              <div className="pt-1 border-t border-[#1b2b52]">
                <button
                  onClick={() => setShowUserMenu(false)}
                  className="w-full text-left px-3 py-2 text-xs text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                >
                  Log Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
