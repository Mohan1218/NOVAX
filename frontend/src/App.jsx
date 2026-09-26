import React, { useState, useEffect, useRef } from 'react';
import { 
  Bug, 
  Play, 
  RotateCcw, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Code2, 
  FileText, 
  Terminal, 
  Shield, 
  Sparkles,
  AlertTriangle,
  RefreshCw,
  Cpu
} from 'lucide-react';
import { api } from './api';

export default function App() {
  const [workspace, setWorkspace] = useState('demo_project');
  const [bugReport, setBugReport] = useState(
    'The discount calculation is incorrect. The test expects a 10% discount from 1000 to produce 900, but the current implementation produces 990.'
  );
  const [jobId, setJobId] = useState(null);
  const [jobState, setJobState] = useState(null);
  const [isStarting, setIsStarting] = useState(false);
  const [activeTab, setActiveTab] = useState('diff');
  const [errorMsg, setErrorMsg] = useState(null);
  const [resetSuccess, setResetSuccess] = useState(false);

  // Dynamic code content state
  const [originalCode, setOriginalCode] = useState('');
  const [fixedCode, setFixedCode] = useState('');
  const [gitDiffContent, setGitDiffContent] = useState('');

  const logsEndRef = useRef(null);

  // Fetch initial/original source code from backend API
  const fetchOriginalCode = async (targetWorkspace = workspace) => {
    try {
      const data = await api.readFile(targetWorkspace, 'calculator.py');
      if (data && data.content) {
        setOriginalCode(data.content);
      }
    } catch (err) {
      console.warn('Could not fetch original code:', err.message);
    }
  };

  // Fetch original code on workspace change or mount
  useEffect(() => {
    fetchOriginalCode(workspace);
  }, [workspace]);

  // Auto-scroll logs
  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [jobState?.logs]);

  // Polling loop when a job is active
  useEffect(() => {
    if (!jobId) return;

    let isMounted = true;
    const pollInterval = setInterval(async () => {
      try {
        const jobData = await api.getJobStatus(jobId);
        if (isMounted) {
          setJobState(jobData);

          if (jobData.status === 'completed' || jobData.status === 'failed' || jobData.status === 'cancelled') {
            clearInterval(pollInterval);
            
            // If verified successfully, fetch actual fixed code and diff from backend
            if (jobData.result?.verified) {
              try {
                const fixedData = await api.readFile(workspace, 'calculator.py');
                if (fixedData && fixedData.content) {
                  setFixedCode(fixedData.content);
                }
              } catch (e) {
                console.error('Failed to load fixed code:', e);
              }

              try {
                const diffData = await api.getGitDiff(workspace);
                if (diffData && diffData.diff) {
                  setGitDiffContent(diffData.diff);
                }
              } catch (e) {
                console.error('Failed to load git diff:', e);
              }
            }
          }
        }
      } catch (err) {
        if (isMounted) {
          console.error('Polling error:', err);
          setErrorMsg(err.message);
          clearInterval(pollInterval);
        }
      }
    }, 800);

    return () => {
      isMounted = false;
      clearInterval(pollInterval);
    };
  }, [jobId, workspace]);

  const handleStartDebugging = async (e) => {
    e.preventDefault();
    if (!bugReport.trim()) return;

    setIsStarting(true);
    setErrorMsg(null);
    setJobState(null);
    setJobId(null);
    setResetSuccess(false);
    setFixedCode('');
    setGitDiffContent('');

    // Save initial state of source file
    await fetchOriginalCode(workspace);

    try {
      const data = await api.startDebugRun(workspace, bugReport);
      setJobId(data.job_id);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsStarting(false);
    }
  };

  const handleResetDemo = async () => {
    setResetSuccess(false);
    setErrorMsg(null);
    try {
      await api.resetDemoProject(workspace);
      setResetSuccess(true);
      setJobId(null);
      setJobState(null);
      setFixedCode('');
      setGitDiffContent('');
      await fetchOriginalCode(workspace);
      setTimeout(() => setResetSuccess(false), 4000);
    } catch (err) {
      setErrorMsg(`Reset failed: ${err.message}`);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return (
          <span className="badge badge-success">
            <CheckCircle2 size={14} /> Completed
          </span>
        );
      case 'failed':
        return (
          <span className="badge badge-danger">
            <XCircle size={14} /> Failed
          </span>
        );
      case 'running':
        return (
          <span className="badge badge-running">
            <RefreshCw className="animate-spin" size={14} /> Running
          </span>
        );
      default:
        return (
          <span className="badge badge-queued">
            <Clock size={14} /> Queued
          </span>
        );
    }
  };

  const formatLogTimestamp = (timestamp) => {
    if (!timestamp) return '';
    if (typeof timestamp === 'number') {
      return new Date(timestamp * 1000).toLocaleTimeString();
    }
    return new Date(timestamp).toLocaleTimeString();
  };

  const isJobRunning = jobState && jobState.status === 'running';

  return (
    <div className="container">
      {/* Header */}
      <header className="header">
        <div className="logo-section">
          <div className="logo-icon">
            <Bug size={24} color="#00f2fe" />
          </div>
          <div>
            <h1>NOVAX BugHunter AI</h1>
            <p className="subtitle">Autonomous Software QA & Debugger Agent</p>
          </div>
        </div>
        <div className="header-badges">
          <span className="tech-badge">
            <Cpu size={14} /> Gemini 2.5 Flash / GenAI
          </span>
          <span className="tech-badge">
            <Shield size={14} /> Sandboxed Execution
          </span>
        </div>
      </header>

      {/* Main Grid */}
      <div className="main-grid">
        {/* Left Column: Controls & Live Debugging Panel */}
        <div className="left-panel">
          {/* Bug Input Card */}
          <div className="card">
            <div className="card-header">
              <Sparkles size={18} color="#4facfe" />
              <h3>Debug Request</h3>
            </div>
            
            <form onSubmit={handleStartDebugging}>
              <div className="form-group">
                <label htmlFor="workspace">Target Workspace</label>
                <select
                  id="workspace"
                  className="input-select"
                  value={workspace}
                  onChange={(e) => setWorkspace(e.target.value)}
                  disabled={isJobRunning || isStarting}
                >
                  <option value="demo_project">demo_project (Python Calculator)</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="bugReport">Bug Report Description</label>
                <textarea
                  id="bugReport"
                  className="input-textarea"
                  rows={4}
                  value={bugReport}
                  onChange={(e) => setBugReport(e.target.value)}
                  placeholder="Describe the unexpected behavior or failure..."
                  disabled={isJobRunning || isStarting}
                />
              </div>

              <div className="button-group">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isJobRunning || isStarting || !bugReport.trim()}
                >
                  {isStarting || isJobRunning ? (
                    <>
                      <RefreshCw className="animate-spin" size={16} />
                      Debugging in Progress...
                    </>
                  ) : (
                    <>
                      <Play size={16} />
                      START DEBUGGING
                    </>
                  )}
                </button>

                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleResetDemo}
                  disabled={isJobRunning || isStarting}
                  title="Reset calculator.py back to buggy state"
                >
                  <RotateCcw size={16} />
                  Reset Demo
                </button>
              </div>

              {resetSuccess && (
                <div className="alert alert-success mt-3">
                  <CheckCircle2 size={16} /> Demo project reset to initial buggy state!
                </div>
              )}

              {errorMsg && (
                <div className="alert alert-danger mt-3">
                  <AlertTriangle size={16} /> {errorMsg}
                </div>
              )}
            </form>
          </div>

          {/* Live Debugging Status Panel */}
          {jobState && (
            <div className="card">
              <div className="card-header">
                <Terminal size={18} color="#00f2fe" />
                <h3>Live Execution Status</h3>
              </div>

              <div className="job-meta">
                <div className="meta-item">
                  <span className="meta-label">Job ID:</span>
                  <span className="meta-value code">{jobState.job_id}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-label">Status:</span>
                  {getStatusBadge(jobState.status)}
                </div>
                <div className="meta-item">
                  <span className="meta-label">Current Step:</span>
                  <span className="step-tag">{jobState.current_step || 'initializing'}</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="progress-section">
                <div className="progress-label">
                  <span>Overall Progress</span>
                  <span>{jobState.progress ?? 0}%</span>
                </div>
                <div className="progress-bar-bg">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${Math.min(100, Math.max(0, jobState.progress ?? 0))}%` }}
                  />
                </div>
              </div>

              {/* Logs Stream */}
              <div className="logs-header">
                <h4>Agent Thought & Execution Stream</h4>
                <span className="log-count">{jobState.logs?.length || 0} entries</span>
              </div>
              <div className="logs-container">
                {jobState.logs && jobState.logs.length > 0 ? (
                  jobState.logs.map((log, index) => (
                    <div key={index} className="log-entry">
                      <span className="log-time">[{formatLogTimestamp(log.timestamp)}]</span>
                      <span className="log-step">[{log.level || 'info'}]</span>
                      <span className="log-msg">{log.message}</span>
                    </div>
                  ))
                ) : (
                  <div className="logs-empty">Waiting for logs...</div>
                )}
                <div ref={logsEndRef} />
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Code, Diff & Results */}
        <div className="right-panel">
          {/* Results Summary Card */}
          {jobState?.result && (
            <div className={`card result-card ${jobState.result.verified ? 'verified-border' : 'failed-border'}`}>
              <div className="result-header">
                {jobState.result.verified ? (
                  <div className="result-status verified">
                    <CheckCircle2 size={28} />
                    <div>
                      <h2>VERIFIED FIX</h2>
                      <p>All test suites passed and changes verified!</p>
                    </div>
                  </div>
                ) : (
                  <div className="result-status failed">
                    <XCircle size={28} />
                    <div>
                      <h2>FIX UNVERIFIED</h2>
                      <p>Agent could not verify a working fix after retries.</p>
                    </div>
                  </div>
                )}
              </div>

              <div className="metrics-grid">
                <div className="metric-box">
                  <span className="metric-label">Tests Passed</span>
                  <span className={`metric-val ${jobState.result.tests_passed ? 'text-success' : 'text-danger'}`}>
                    {jobState.result.tests_passed ? 'YES ✓' : 'NO ✗'}
                  </span>
                </div>
                <div className="metric-box">
                  <span className="metric-label">Retries Used</span>
                  <span className="metric-val">
                    {jobState.result.retries ?? jobState.result.retry_count ?? 0} / 3
                  </span>
                </div>
                <div className="metric-box">
                  <span className="metric-label">Execution Time</span>
                  <span className="metric-val">
                    {jobState.result.duration ?? jobState.result.duration_seconds ?? '0.0'}s
                  </span>
                </div>
                <div className="metric-box">
                  <span className="metric-label">Diagnosis</span>
                  <span className="metric-val text-truncate" title={jobState.result.diagnosis}>
                    {jobState.result.diagnosis || 'Analyzed'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Code / Diff Inspector */}
          <div className="card fill-height">
            <div className="card-header tabs-header">
              <div className="tabs">
                <button
                  className={`tab-btn ${activeTab === 'diff' ? 'active' : ''}`}
                  onClick={() => setActiveTab('diff')}
                >
                  <Code2 size={16} />
                  Git Diff
                </button>
                <button
                  className={`tab-btn ${activeTab === 'fixed' ? 'active' : ''}`}
                  onClick={() => setActiveTab('fixed')}
                >
                  <FileText size={16} />
                  Fixed Code
                </button>
                <button
                  className={`tab-btn ${activeTab === 'original' ? 'active' : ''}`}
                  onClick={() => setActiveTab('original')}
                >
                  <FileText size={16} />
                  Original Code
                </button>
              </div>
            </div>

            <div className="tab-content">
              {activeTab === 'diff' && (
                <div className="code-viewer-container">
                  <div className="code-header">
                    <span>git diff (calculator.py)</span>
                  </div>
                  <pre className="code-viewer diff-viewer">
                    {gitDiffContent || jobState?.result?.diff || jobState?.result?.patch_diff || (
                      <span className="text-muted">No diff available. Run debugging to generate patch diff.</span>
                    )}
                  </pre>
                </div>
              )}

              {activeTab === 'fixed' && (
                <div className="code-viewer-container">
                  <div className="code-header">
                    <span>Fixed Version: workspace/demo_project/calculator.py</span>
                  </div>
                  <pre className="code-viewer">
                    {fixedCode ? (
                      fixedCode
                    ) : jobState?.result?.verified ? (
                      <span className="text-muted">Loading fixed code from backend...</span>
                    ) : (
                      <span className="text-muted">Fixed code will appear here after a successful run.</span>
                    )}
                  </pre>
                </div>
              )}

              {activeTab === 'original' && (
                <div className="code-viewer-container">
                  <div className="code-header">
                    <span>Original Version: workspace/demo_project/calculator.py</span>
                  </div>
                  <pre className="code-viewer">
                    {originalCode || (
                      <span className="text-muted">Loading original file from backend...</span>
                    )}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
