import { TaskHistoryItem, Repository } from '../types';

export const INITIAL_TASK_HISTORY: TaskHistoryItem[] = [
  {
    id: 'task-1',
    title: 'Fix discount calculation bug',
    timestamp: 'Apr 26, 10:32 AM',
    status: 'Verified',
    description: 'Resolved floating-point precision error in cart discount tiered pricing calculations where 15% discount applied incorrect subtraction on zero-margin SKUs.',
    duration: '2m 45s',
    filesChanged: 3,
    branch: 'fix/discount-tier-precision',
    commitHash: '7f9a2e1'
  },
  {
    id: 'task-2',
    title: 'Login validation error',
    timestamp: 'Apr 25, 04:12 PM',
    status: 'Verified',
    description: 'Fixed race condition in OAuth2 callback handler when JWT refresh token was exchanged asynchronously before session handshake completed.',
    duration: '4m 10s',
    filesChanged: 2,
    branch: 'fix/oauth-jwt-handshake',
    commitHash: '3a18d9c'
  },
  {
    id: 'task-3',
    title: 'API timeout issue',
    timestamp: 'Apr 24, 11:20 AM',
    status: 'Failed',
    description: 'Orchestrator failed to acquire ephemeral worker pod within 120s due to Kubernetes cluster resource saturation during heavy load test.',
    duration: '5m 02s',
    filesChanged: 0,
    branch: 'chore/k8s-pod-provisioning',
    commitHash: 'e410b37'
  },
  {
    id: 'task-4',
    title: 'Database connection bug',
    timestamp: 'Apr 23, 02:15 PM',
    status: 'Verified',
    description: 'PostgreSQL connection pool exhaust fix: replaced unbounded connection spawn with resilient pgBouncer connection pooling and graceful retry backoff.',
    duration: '3m 18s',
    filesChanged: 4,
    branch: 'fix/db-pool-exhaustion',
    commitHash: '98d5c1a'
  },
  {
    id: 'task-5',
    title: 'UI rendering issue',
    timestamp: 'Apr 22, 09:40 AM',
    status: 'Verified',
    description: 'Corrected virtualized list reflow jitter in high-frequency WebSocket metrics stream by memoizing row rendering height and batching state updates.',
    duration: '1m 55s',
    filesChanged: 2,
    branch: 'fix/virtual-list-repaint',
    commitHash: '52bf890'
  }
];

export const MOCK_REPOSITORIES: Repository[] = [
  {
    id: 'repo-1',
    name: 'ecommerce-engine',
    fullPath: 'novax-ai/ecommerce-engine',
    branch: 'main',
    branches: ['main', 'develop', 'release/v2.4', 'hotfix/cart-calc'],
    stars: 342,
    language: 'Python',
    updatedAt: '2 hours ago'
  },
  {
    id: 'repo-2',
    name: 'auth-gateway-service',
    fullPath: 'novax-ai/auth-gateway-service',
    branch: 'master',
    branches: ['master', 'feature/passkeys', 'staging'],
    stars: 189,
    language: 'TypeScript',
    updatedAt: 'Yesterday'
  },
  {
    id: 'repo-3',
    name: 'fintech-core-api',
    fullPath: 'novax-ai/fintech-core-api',
    branch: 'develop',
    branches: ['develop', 'main', 'feat/iso20022'],
    stars: 520,
    language: 'Go',
    updatedAt: '3 days ago'
  },
  {
    id: 'repo-4',
    name: 'cloud-infra-orchestrator',
    fullPath: 'novax-ai/cloud-infra-orchestrator',
    branch: 'main',
    branches: ['main', 'feature/terraform-aws'],
    stars: 87,
    language: 'Rust',
    updatedAt: '5 days ago'
  }
];

export const QUICK_EXAMPLES = [
  {
    id: 'ex-1',
    label: 'Fix the login function error',
    icon: 'code',
    prompt: 'Investigate and fix the login function error in auth_controller.py. Users report intermittent 401 Unauthorized responses during token refresh on session expiration.',
    language: 'Python' as const
  },
  {
    id: 'ex-2',
    label: 'Analyze this repository',
    icon: 'folder',
    prompt: 'Perform a comprehensive architectural and vulnerability analysis of this codebase. Identify performance bottlenecks, dead code, and security risks.',
    language: 'Python' as const
  },
  {
    id: 'ex-3',
    label: 'Add a new feature',
    icon: 'plus',
    prompt: 'Implement a new automated rate-limiting middleware using Redis sliding-window algorithm, configured for 120 requests/minute per authenticated API key.',
    language: 'TypeScript' as const
  },
  {
    id: 'ex-4',
    label: 'Run tests and fix failures',
    icon: 'check-circle',
    prompt: 'Execute the entire test suite via pytest, locate failing unit and regression tests, formulate root causes, and autonomously apply verified code patches.',
    language: 'Python' as const
  }
];

export const MOCK_NOTIFICATIONS = [
  {
    id: 'n-1',
    title: 'Task Verified: Fix discount calculation bug',
    time: '15m ago',
    type: 'success',
    read: false
  },
  {
    id: 'n-2',
    title: 'Model Update: NOVAX Agent v4.1 is active',
    time: '1h ago',
    type: 'info',
    read: false
  },
  {
    id: 'n-3',
    title: 'Automated test suite passed (48/48 tests)',
    time: '3h ago',
    type: 'success',
    read: true
  },
  {
    id: 'n-4',
    title: 'Orchestrator node US-East latency 12ms',
    time: '6h ago',
    type: 'info',
    read: true
  }
];
