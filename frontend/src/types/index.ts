export type Language = 'Python' | 'TypeScript' | 'JavaScript' | 'Go' | 'Rust' | 'Java' | 'C++';

export interface TaskHistoryItem {
  id: string;
  title: string;
  timestamp: string;
  status: 'Verified' | 'Failed' | 'In Progress';
  description?: string;
  duration?: string;
  filesChanged?: number;
  branch?: string;
  commitHash?: string;
}

export interface AttachedFile {
  id: string;
  name: string;
  size: number;
  type: string;
}

export interface Repository {
  id: string;
  name: string;
  fullPath: string;
  branch: string;
  branches: string[];
  stars?: number;
  language: string;
  updatedAt: string;
}

export type FeatureModalType = 
  | 'live-streaming'
  | 'novax-report'
  | 'time-performance'
  | 'execution-replay'
  | 'repository-explorer'
  | 'diff-viewer'
  | 'code-analysis'
  | 'test-results'
  | 'verification'
  | 'documentation';

export type NavModalType =
  | 'projects'
  | 'history'
  | 'reports'
  | 'analytics'
  | 'settings';

export interface ToastMessage {
  id: string;
  type: 'error' | 'warning' | 'success' | 'info';
  title: string;
  message: string;
  timestamp: Date;
}
