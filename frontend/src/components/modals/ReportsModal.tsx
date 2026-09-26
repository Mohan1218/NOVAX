import React from 'react';
import { FileText, Download, CheckCircle, ExternalLink, X, Shield, Clock } from 'lucide-react';

interface ReportsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenReportView: () => void;
}

export const ReportsModal: React.FC<ReportsModalProps> = ({ isOpen, onClose, onOpenReportView }) => {
  if (!isOpen) return null;

  const reports = [
    { id: 'rep-1', title: 'Fix discount calculation bug - Verification Audit', date: 'Apr 26, 2026', size: '24 KB', type: 'Verification' },
    { id: 'rep-2', title: 'Weekly Autonomous Resolution Digest #16', date: 'Apr 25, 2026', size: '112 KB', type: 'Executive' },
    { id: 'rep-3', title: 'Static Security & Dependency CVE Audit (Bandit SAST)', date: 'Apr 24, 2026', size: '48 KB', type: 'Security' },
    { id: 'rep-4', title: 'Database Connection Pool Exhaustion Incident Postmortem', date: 'Apr 23, 2026', size: '36 KB', type: 'Incident' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="w-full max-w-3xl max-h-[85vh] rounded-2xl bg-[#0a0f24] border border-[#203260] shadow-2xl flex flex-col overflow-hidden animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-4 px-6 border-b border-[#17254d] bg-[#0d1633] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-sky-500/20 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Execution & Compliance Reports</h2>
              <p className="text-xs text-slate-400">Autonomous software engineering records, test traces, and audit logs</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* List of Reports */}
        <div className="p-6 overflow-y-auto space-y-3 flex-1 text-xs">
          {reports.map((rep) => (
            <div
              key={rep.id}
              className="p-4 rounded-xl bg-[#0d1633] border border-[#1b2b52] hover:border-sky-500/30 transition-all flex items-center justify-between"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold text-white text-sm">{rep.title}</h4>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#1b2b52] text-sky-300">
                    {rep.type}
                  </span>
                </div>
                <div className="flex items-center gap-4 text-slate-400 text-[11px]">
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {rep.date}</span>
                  <span>{rep.size}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    onClose();
                    onOpenReportView();
                  }}
                  className="px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-medium text-xs transition-colors flex items-center gap-1.5"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>View</span>
                </button>
              </div>
            </div>
          ))}
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
