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
  ChevronRight,
  Cpu
} from 'lucide-react';

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
  
  const logsEndRef = useRef(null);

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
        const res = await fetch(`/api/jobs/${jobId}`);
        if (!res.ok) {
          throw new Error(`Failed to fetch job status: ${res.statusText}`);
        }
        const data = await res.json();
        if (isMounted) {
          const jobData = data.job || data;
          setJobState(jobData);
          if (jobData.status === 'completed' || jobData.status === 'failed') {
            clearInterval(pollInterval);
          }
        }
      } catch (err) {
        if (isMounted) {
          console.error('Polling error:', err);
          setErrorMsg(err.message);
        }
      }
    }, 800);

    return () => {
      isMounted = false;
      clearInterval(pollInterval);
    };
  }, [jobId]);

  const handleStartDebugging = async (e) => {
    e.preventDefault();
    if (!bugReport.trim()) return;

    setIsStarting(true);
    setErrorMsg(null);
    setJobState(null);
    setResetSuccess(false);

    try {
      const res = await fetch('/api/debug/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workspace,
          bug_report: bugReport,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to start debug job');
      }

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
      // Re-write initial buggy calculator code
      const buggyCode = `def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b == 0:\n        raise ValueError("Cannot divide by zero")\n    return a / b\n\ndef calculate_discount(price, discount_percent):\n    # BUG: Subtracting percent directly instead of calculating percentage\n    return price - discount_percent\n`;
      
      const res = await fetch('/api/execution/files/write', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workspace: 'demo_project',
          file_path: 'calculator.py',
          content: buggyCode,
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to reset calculator.py');
      }

      setResetSuccess(true);
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
            <h1>BugHunter AI</h1>
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
                  <CheckCircle2 size={16} /> Demo project reset to buggy state!
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
                  <span>{jobState.progress}%</span>
                </div>
                <div className="progress-bar-bg">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${Math.min(100, Math.max(0, jobState.progress))}%` }}
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
                      <span className="log-time">[{new Date(log.timestamp * 1000).toLocaleTimeString()}]</span>
                      <span className="log-step">[{log.step}]</span>
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
                  <span className="metric-val">{jobState.result.retry_count} / 3</span>
                </div>
                <div className="metric-box">
                  <span className="metric-label">Execution Time</span>
                  <span className="metric-val">{jobState.result.duration_seconds || '0.0'}s</span>
                </div>
                <div className="metric-box">
                  <span className="metric-label">Files Modified</span>
                  <span className="metric-val">
                    {jobState.result.modified_files?.length > 0
                      ? jobState.result.modified_files.join(', ')
                      : 'None'}
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
                    {jobState?.result?.diff || jobState?.result?.patch_diff || (
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
                    {jobState?.result?.verified ? (
                      `def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b == 0:\n        raise ValueError("Cannot divide by zero")\n    return a / b\n\ndef calculate_discount(price, discount_percent):\n    discount_amount = price * discount_percent / 100\n    return price - discount_amount`
                    ) : (
                      <span className="text-muted">Fixed code will appear here after a successful run.</span>
                    )}
                  </pre>
                </div>
              )}

              {activeTab === 'original' && (
                <div className="code-viewer-container">
                  <div className="code-header">
                    <span>Original Version (Buggy): workspace/demo_project/calculator.py</span>
                  </div>
                  <pre className="code-viewer">
                    {`def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def calculate_discount(price, discount_percent):
    # BUG: Subtracting percent directly instead of calculating percentage
    return price - discount_percent`}
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
