const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Helper function for handling API requests and network errors cleanly.
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    const contentType = response.headers.get('content-type');
    
    let data;
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const errorMessage =
        (typeof data === 'object' && (data.detail || data.message || data.error)) ||
        `HTTP Error ${response.status}: ${response.statusText}`;
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error(`Failed to connect to backend server at ${API_BASE_URL || 'http://127.0.0.1:8000'}. Is FastAPI running?`);
    }
    throw error;
  }
}

export const api = {
  /**
   * Health check endpoint
   */
  getHealth: () => request('/health'),

  /**
   * Triggers an autonomous debugging run in the background.
   * POST /api/debug/run
   */
  startDebugRun: (workspace, bugReport) =>
    request('/api/debug/run', {
      method: 'POST',
      body: JSON.stringify({
        workspace,
        bug_report: bugReport,
      }),
    }),

  /**
   * Polls current status, progress, current_step, logs, and result of a job.
   * GET /api/jobs/{job_id}
   */
  getJobStatus: async (jobId) => {
    const data = await request(`/api/jobs/${jobId}`);
    return data.job || data;
  },

  /**
   * Retrieves list of files in workspace.
   * GET /api/execution/files/{workspace}
   */
  listFiles: (workspace) => request(`/api/execution/files/${workspace}`),

  /**
   * Reads content of a workspace file.
   * GET /api/execution/file/{workspace}/{filePath}
   */
  readFile: (workspace, filePath) => request(`/api/execution/file/${workspace}/${filePath}`),

  /**
   * Writes content to a workspace file.
   * POST /api/execution/file/{workspace}/{filePath}
   */
  writeFile: (workspace, filePath, content) =>
    request(`/api/execution/file/${workspace}/${filePath}`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),

  /**
   * Fetches Git diff for the workspace.
   * GET /api/execution/git-diff/{workspace}
   */
  getGitDiff: (workspace) => request(`/api/execution/git-diff/${workspace}`),

  /**
   * Fetches Git status for the workspace.
   * GET /api/execution/git-status/{workspace}
   */
  getGitStatus: (workspace) => request(`/api/execution/git-status/${workspace}`),

  /**
   * Resets demo workspace file (calculator.py) to initial buggy state.
   */
  resetDemoProject: async (workspace = 'demo_project') => {
    const buggyCode = `def calculate_discount(price, discount_percent):\n    """Calculate final price after percentage discount."""\n    return price - discount_percent\n`;
    return request(`/api/execution/file/${workspace}/calculator.py`, {
      method: 'POST',
      body: JSON.stringify({ content: buggyCode }),
    });
  },
};
