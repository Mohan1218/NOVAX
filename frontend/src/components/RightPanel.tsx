import React from 'react';
import { 
  Zap, 
  Radio, 
  FileText, 
  Clock, 
  Play, 
  Folder, 
  Code2, 
  Search, 
  FlaskConical, 
  ShieldCheck, 
  BookOpen, 
  ChevronRight 
} from 'lucide-react';
import { FeatureModalType } from '../types';

interface RightPanelProps {
  onOpenFeature: (feature: FeatureModalType) => void;
}

interface FeatureItem {
  id: FeatureModalType;
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  iconBg: string;
}

export const RightPanel: React.FC<RightPanelProps> = ({ onOpenFeature }) => {
  const features: FeatureItem[] = [
    {
      id: 'live-streaming',
      title: 'Live Streaming',
      subtitle: 'Watch real-time agent activity',
      icon: <Radio className="w-4 h-4 text-cyan-400" />,
      iconBg: 'bg-cyan-500/20 border border-cyan-500/30'
    },
    {
      id: 'novax-report',
      title: 'NOVAX Report',
      subtitle: 'View detailed execution report',
      icon: <FileText className="w-4 h-4 text-sky-400" />,
      iconBg: 'bg-sky-500/20 border border-sky-500/30'
    },
    {
      id: 'time-performance',
      title: 'Time & Performance',
      subtitle: 'See metrics and statistics',
      icon: <Clock className="w-4 h-4 text-emerald-400" />,
      iconBg: 'bg-emerald-500/20 border border-emerald-500/30'
    },
    {
      id: 'execution-replay',
      title: 'Execution Replay',
      subtitle: 'Replay the full process',
      icon: <Play className="w-4 h-4 text-orange-400 fill-orange-400" />,
      iconBg: 'bg-orange-500/20 border border-orange-500/30'
    },
    {
      id: 'repository-explorer',
      title: 'Repository Explorer',
      subtitle: 'Browse and explore codebase',
      icon: <Folder className="w-4 h-4 text-cyan-300" />,
      iconBg: 'bg-cyan-600/20 border border-cyan-500/30'
    },
    {
      id: 'diff-viewer',
      title: 'Diff Viewer',
      subtitle: 'View code changes',
      icon: <Code2 className="w-4 h-4 text-rose-400" />,
      iconBg: 'bg-rose-500/20 border border-rose-500/30'
    },
    {
      id: 'code-analysis',
      title: 'Code Analysis',
      subtitle: 'Analyze and understand code',
      icon: <Search className="w-4 h-4 text-purple-400" />,
      iconBg: 'bg-purple-500/20 border border-purple-500/30'
    },
    {
      id: 'test-results',
      title: 'Test Results',
      subtitle: 'View test execution results',
      icon: <FlaskConical className="w-4 h-4 text-indigo-400" />,
      iconBg: 'bg-indigo-500/20 border border-indigo-500/30'
    },
    {
      id: 'verification',
      title: 'Verification',
      subtitle: 'Check and verify fixes',
      icon: <ShieldCheck className="w-4 h-4 text-teal-400" />,
      iconBg: 'bg-teal-500/20 border border-teal-500/30'
    },
    {
      id: 'documentation',
      title: 'Documentation',
      subtitle: 'Guides and help',
      icon: <BookOpen className="w-4 h-4 text-blue-400" />,
      iconBg: 'bg-blue-600/20 border border-blue-500/30'
    }
  ];

  return (
    <aside className="w-80 flex-shrink-0 bg-[#080d1e] border-l border-[#15203d] p-4 flex flex-col h-full overflow-y-auto">
      {/* Header */}
      <div className="flex items-center gap-2.5 mb-1 px-1">
        <div className="w-7 h-7 rounded-lg bg-purple-600/20 border border-purple-500/30 flex items-center justify-center">
          <Zap className="w-4 h-4 text-purple-400 fill-purple-400" />
        </div>
        <h2 className="text-sm font-bold text-white tracking-wide">
          Quick Feature Access
        </h2>
      </div>
      <p className="text-[11px] text-slate-400 mb-4 px-1">
        Access key features instantly
      </p>

      {/* Feature Cards Stack */}
      <div className="space-y-2">
        {features.map((feature) => (
          <button
            key={feature.id}
            onClick={() => onOpenFeature(feature.id)}
            className="w-full flex items-center justify-between p-2.5 rounded-xl bg-[#0c142b] border border-[#172346] hover:border-[#283b70] hover:bg-[#111c3d] transition-all duration-200 group text-left cursor-pointer shadow-sm hover:shadow-md"
          >
            <div className="flex items-center gap-3 min-w-0">
              {/* Rounded Square Icon Badge */}
              <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-105 ${feature.iconBg}`}>
                {feature.icon}
              </div>

              {/* Title & Subtitle */}
              <div className="min-w-0">
                <h3 className="text-xs font-semibold text-white tracking-tight group-hover:text-cyan-300 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-[11px] text-slate-400 truncate mt-0.5">
                  {feature.subtitle}
                </p>
              </div>
            </div>

            {/* Right Chevron */}
            <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-white group-hover:translate-x-0.5 transition-all flex-shrink-0 ml-2" />
          </button>
        ))}
      </div>
    </aside>
  );
};
