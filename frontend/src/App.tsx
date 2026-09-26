import React, { useState } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Workspace } from './components/Workspace';
import { RightPanel } from './components/RightPanel';
import { ToastContainer } from './components/Toast';

// Modals
import { BackendErrorModal } from './components/modals/BackendErrorModal';
import { SelectRepositoryModal } from './components/modals/SelectRepositoryModal';
import { LiveStreamingModal } from './components/modals/LiveStreamingModal';
import { NovaxReportModal } from './components/modals/NovaxReportModal';
import { TimePerformanceModal } from './components/modals/TimePerformanceModal';
import { ExecutionReplayModal } from './components/modals/ExecutionReplayModal';
import { RepositoryExplorerModal } from './components/modals/RepositoryExplorerModal';
import { DiffViewerModal } from './components/modals/DiffViewerModal';
import { CodeAnalysisModal } from './components/modals/CodeAnalysisModal';
import { TestResultsModal } from './components/modals/TestResultsModal';
import { VerificationModal } from './components/modals/VerificationModal';
import { DocumentationModal } from './components/modals/DocumentationModal';
import { TaskDetailModal } from './components/modals/TaskDetailModal';
import { ProjectsModal } from './components/modals/ProjectsModal';
import { HistoryModal } from './components/modals/HistoryModal';
import { ReportsModal } from './components/modals/ReportsModal';
import { AnalyticsModal } from './components/modals/AnalyticsModal';
import { SettingsModal } from './components/modals/SettingsModal';

import { 
  Language, 
  AttachedFile, 
  Repository, 
  TaskHistoryItem, 
  FeatureModalType, 
  NavModalType, 
  ToastMessage 
} from './types';
import { INITIAL_TASK_HISTORY, MOCK_REPOSITORIES } from './data/mockData';
import { api } from './api';

export function App() {
  // Navigation & Workspace State
  const [activeNav, setActiveNav] = useState('Dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // Chatbox & Task Input State
  const [prompt, setPrompt] = useState('');
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<Language>('Python');
  const [taskHistory, setTaskHistory] = useState<TaskHistoryItem[]>(INITIAL_TASK_HISTORY);

  // Loading & Connection State
  const [isConnecting, setIsConnecting] = useState(false);
  const [showBackendErrorModal, setShowBackendErrorModal] = useState(false);
  const [isRetryingConnection, setIsRetryingConnection] = useState(false);

  // Active Job & Diff State
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [jobState, setJobState] = useState<any>(null);
  const [diffText, setDiffText] = useState<string>('');


  // Modals Active State
  const [isRepoPickerOpen, setIsRepoPickerOpen] = useState(false);
  const [activeFeatureModal, setActiveFeatureModal] = useState<FeatureModalType | null>(null);
  const [activeNavModal, setActiveNavModal] = useState<NavModalType | null>(null);
  const [selectedTaskDetail, setSelectedTaskDetail] = useState<TaskHistoryItem | null>(null);

  // Toast System
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (type: 'error' | 'warning' | 'success' | 'info', title: string, message: string) => {
    const newToast: ToastMessage = {
      id: `toast-${Date.now()}-${Math.random()}`,
      type,
      title,
      message,
      timestamp: new Date()
    };
    setToasts(prev => [newToast, ...prev]);

    // Auto dismiss after 6 seconds
    setTimeout(() => {
      removeToast(newToast.id);
    }, 6000);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  // Attach files handler
  const handleAddFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const newFiles: AttachedFile[] = Array.from(files).map((f, i) => ({
      id: `file-${Date.now()}-${i}`,
      name: f.name,
      size: f.size,
      type: f.type || 'text/plain'
    }));
    setAttachedFiles(prev => [...prev, ...newFiles]);
    addToast('info', 'Files Attached', `Added ${newFiles.length} file(s) to workspace context.`);
  };

  const handleRemoveFile = (fileId: string) => {
    setAttachedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  // Polling helper for active job
  const startPollingJob = (jobId: string, workspaceName: string) => {
    const interval = setInterval(async () => {
      try {
        const job = await api.getJobStatus(jobId);
        setJobState(job);
        if (['completed', 'failed', 'cancelled'].includes(job.status)) {
          clearInterval(interval);
          if (job.status === 'completed') {
            if (job.result?.verified) {
              addToast('success', 'VERIFIED FIX', 'All tests passed cleanly! Fix verified.');
            } else {
              addToast('warning', 'Task Completed', 'Job completed execution.');
            }
            try {
              const diffRes = await api.getGitDiff(workspaceName);
              setDiffText(typeof diffRes === 'string' ? diffRes : (diffRes.diff || ''));
            } catch (e) {
              console.warn('Could not fetch git diff:', e);
            }
          } else if (job.status === 'failed') {
            addToast('error', 'Debugging Failed', job.error || 'Job failed during execution.');
          }
        }
      } catch (err) {
        console.error('Error polling job status:', err);
      }
    }, 1500);
  };

  // Start Working Button Action -> calls real backend API
  const handleStartWorking = async () => {
    const workspaceName = selectedRepo?.name || 'demo_project';
    const bugReportText = prompt.trim() || 'Calculate percentage discount accurately (1000 with 10% discount should return 900)';

    setIsConnecting(true);
    try {
      const response = await api.startDebugRun(workspaceName, bugReportText);
      const jobId = response.job_id;
      setCurrentJobId(jobId);
      setIsConnecting(false);
      setActiveFeatureModal('live-streaming');
      addToast('info', 'Agent Dispatched', `Autonomous debugging run ${jobId.substring(0, 8)} started.`);
      startPollingJob(jobId, workspaceName);
    } catch (err: any) {
      setIsConnecting(false);
      setShowBackendErrorModal(true);
      addToast('error', 'Backend connection failed', err.message || 'Unable to connect to NOVAX Orchestrator at backend.');
    }
  };

  const handleRetryConnection = async () => {
    setIsRetryingConnection(true);
    try {
      const health = await api.getHealth();
      setIsRetryingConnection(false);
      if (health.status === 'ok') {
        setShowBackendErrorModal(false);
        addToast('success', 'Backend Connected', 'NOVAX Orchestrator service is online.');
      }
    } catch (err) {
      setIsRetryingConnection(false);
      addToast('error', 'Connection Refused', 'FastAPI backend server is unreachable.');
    }
  };

  const handleStartSimulation = () => {
    setShowBackendErrorModal(false);
    setActiveFeatureModal('live-streaming');
    addToast('info', 'Demo Simulation Mode', 'Live Streaming simulator started in local mock container.');
  };

  // New Task Reset
  const handleNewTask = () => {
    setPrompt('');
    setAttachedFiles([]);
    setSelectedRepo(null);
    addToast('info', 'New Task Ready', 'Workspace input cleared. Ready for your task description.');
  };

  // Load task into workspace
  const handleRerunTask = (task: TaskHistoryItem) => {
    setPrompt(task.description || `Investigate and resolve ${task.title}`);
    setSelectedTaskDetail(null);
    addToast('info', 'Task Loaded', `Loaded "${task.title}" into workspace.`);
  };

  // Theme toggle
  const handleToggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    addToast('info', 'Appearance Updated', isDarkMode ? 'Switched to Light contrast mode.' : 'Cyberpunk Dark mode enabled.');
  };

  return (
    <div className={`min-h-screen flex flex-col bg-[#070b18] text-slate-100 ${isDarkMode ? 'dark' : ''}`}>
      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />

      {/* Main App Container */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Header */}
        <Header 
          onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
          onOpenSettings={() => setActiveNavModal('settings')}
        />

        {/* 3-Column Body */}
        <div className="flex-1 flex overflow-hidden relative">
          {/* Column 1: Left Navigation & Task History */}
          <Sidebar
            isOpen={isSidebarOpen}
            activeNav={activeNav}
            onSelectNav={(nav) => {
              setActiveNav(nav);
              if (nav !== 'Dashboard') {
                setActiveNavModal(nav.toLowerCase() as NavModalType);
              }
            }}
            onNewTask={handleNewTask}
            onOpenNavModal={(type) => setActiveNavModal(type)}
            taskHistory={taskHistory}
            onSelectTask={(task) => setSelectedTaskDetail(task)}
            onViewAllHistory={() => setActiveNavModal('history')}
            isDarkMode={isDarkMode}
            onToggleTheme={handleToggleTheme}
          />

          {/* Column 2: Center Task Workspace */}
          <Workspace
            prompt={prompt}
            setPrompt={setPrompt}
            attachedFiles={attachedFiles}
            onAddFiles={handleAddFiles}
            onRemoveFile={handleRemoveFile}
            selectedRepo={selectedRepo}
            onOpenRepoPicker={() => setIsRepoPickerOpen(true)}
            onRemoveRepo={() => setSelectedRepo(null)}
            selectedLanguage={selectedLanguage}
            onSelectLanguage={setSelectedLanguage}
            onStartWorking={handleStartWorking}
            isConnecting={isConnecting}
          />

          {/* Column 3: Right Quick Feature Access */}
          <div className="hidden xl:block">
            <RightPanel onOpenFeature={(feat) => setActiveFeatureModal(feat)} />
          </div>
        </div>
      </div>

      {/* MODALS */}
      {/* 1. Backend Connection Error Modal */}
      <BackendErrorModal
        isOpen={showBackendErrorModal}
        onClose={() => setShowBackendErrorModal(false)}
        onRetry={handleRetryConnection}
        onStartSimulation={handleStartSimulation}
        isRetrying={isRetryingConnection}
      />

      {/* 2. Repository Selector Modal */}
      <SelectRepositoryModal
        isOpen={isRepoPickerOpen}
        onClose={() => setIsRepoPickerOpen(false)}
        selectedRepo={selectedRepo}
        onSelectRepo={(repo) => {
          setSelectedRepo(repo);
          addToast('success', 'Repository Connected', `Bound workspace to ${repo.name} (${repo.branch}).`);
        }}
      />

      {/* 3. Right Panel Feature Modals */}
      <LiveStreamingModal
        isOpen={activeFeatureModal === 'live-streaming'}
        onClose={() => setActiveFeatureModal(null)}
        jobId={currentJobId}
        jobState={jobState}
      />

      <NovaxReportModal
        isOpen={activeFeatureModal === 'novax-report'}
        onClose={() => setActiveFeatureModal(null)}
      />

      <TimePerformanceModal
        isOpen={activeFeatureModal === 'time-performance'}
        onClose={() => setActiveFeatureModal(null)}
      />

      <ExecutionReplayModal
        isOpen={activeFeatureModal === 'execution-replay'}
        onClose={() => setActiveFeatureModal(null)}
      />

      <RepositoryExplorerModal
        isOpen={activeFeatureModal === 'repository-explorer'}
        onClose={() => setActiveFeatureModal(null)}
      />

      <DiffViewerModal
        isOpen={activeFeatureModal === 'diff-viewer'}
        onClose={() => setActiveFeatureModal(null)}
        diffText={diffText}
        filePath={selectedRepo?.name ? `${selectedRepo.name}/calculator.py` : 'calculator.py'}
      />

      <CodeAnalysisModal
        isOpen={activeFeatureModal === 'code-analysis'}
        onClose={() => setActiveFeatureModal(null)}
      />

      <TestResultsModal
        isOpen={activeFeatureModal === 'test-results'}
        onClose={() => setActiveFeatureModal(null)}
      />

      <VerificationModal
        isOpen={activeFeatureModal === 'verification'}
        onClose={() => setActiveFeatureModal(null)}
      />

      <DocumentationModal
        isOpen={activeFeatureModal === 'documentation'}
        onClose={() => setActiveFeatureModal(null)}
      />

      {/* 4. Left Nav Modals */}
      <ProjectsModal
        isOpen={activeNavModal === 'projects'}
        onClose={() => setActiveNavModal(null)}
        onSelectProject={(proj) => {
          setSelectedRepo(proj);
          addToast('success', 'Project Activated', `Active project set to ${proj.name}.`);
        }}
      />

      <HistoryModal
        isOpen={activeNavModal === 'history'}
        onClose={() => setActiveNavModal(null)}
        tasks={taskHistory}
        onSelectTask={(task) => setSelectedTaskDetail(task)}
      />

      <ReportsModal
        isOpen={activeNavModal === 'reports'}
        onClose={() => setActiveNavModal(null)}
        onOpenReportView={() => setActiveFeatureModal('novax-report')}
      />

      <AnalyticsModal
        isOpen={activeNavModal === 'analytics'}
        onClose={() => setActiveNavModal(null)}
      />

      <SettingsModal
        isOpen={activeNavModal === 'settings'}
        onClose={() => setActiveNavModal(null)}
        onSaveToast={() => addToast('success', 'Settings Saved', 'Autonomous preferences updated.')}
      />

      {/* 5. Task Detail Modal for specific task clicked in sidebar */}
      <TaskDetailModal
        task={selectedTaskDetail}
        onClose={() => setSelectedTaskDetail(null)}
        onRerun={handleRerunTask}
      />
    </div>
  );
}

export default App;
