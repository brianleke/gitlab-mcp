import { createMcpHandler } from 'mcp-handler';
import { z } from 'zod';

// GitLab API base URL - can be customized for self-hosted instances
const GITLAB_API_BASE = process.env.GITLAB_API_URL || 'https://gitlab.com/api/v4';
const GITLAB_TOKEN = process.env.GITLAB_PRIVATE_TOKEN;
const SERVER_BEARER_TOKEN = process.env.SERVER_BEARER_TOKEN;

if (!GITLAB_TOKEN) {
  throw new Error('GITLAB_PRIVATE_TOKEN environment variable is required');
}

if (!SERVER_BEARER_TOKEN) {
  throw new Error('Auth token environment variable is required');
}

// Helper function to extract bearer token from request
function extractBearerToken(request: Request): string | null {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader) {
    return null;
  }

  // Check for Bearer token format
  if (authHeader.startsWith('Bearer ')) {
    return authHeader.substring(7);
  }

  // Also accept just the token without "Bearer " prefix
  return authHeader;
}

// Helper function to validate bearer token
function validateBearerToken(request: Request): boolean {
  const providedToken = extractBearerToken(request);
  if (!providedToken) {
    return false;
  }
  return providedToken === SERVER_BEARER_TOKEN;
}

// Helper function to make GitLab API requests
async function gitlabRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<any> {
  const url = `${GITLAB_API_BASE}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'PRIVATE-TOKEN': GITLAB_TOKEN!,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`GitLab API error: ${response.status} ${response.statusText} - ${error}`);
  }

  return response.json();
}

const handler = createMcpHandler(
  (server) => {
    // List projects
    server.tool(
      'list_gitlab_projects',
      'Lists all projects accessible to the authenticated user or in a specific group',
      {
        groupId: z.string().optional().describe('Optional group ID to filter projects'),
        owned: z.boolean().optional().describe('Limit to projects owned by the user'),
        starred: z.boolean().optional().describe('Limit to starred projects'),
        search: z.string().optional().describe('Search projects by name'),
        perPage: z.number().optional().describe('Number of results per page (default: 20)'),
        page: z.number().optional().describe('Page number (default: 1)'),
      },
      async ({ groupId, owned, starred, search, perPage, page }) => {
        let endpoint = '/projects';
        
        if (groupId) {
          endpoint = `/groups/${groupId}/projects`;
        } else {
          const params = new URLSearchParams();
          if (owned) params.append('owned', 'true');
          if (starred) params.append('starred', 'true');
          if (search) params.append('search', search);
          if (perPage) params.append('per_page', perPage.toString());
          if (page) params.append('page', page.toString());
          
          const queryString = params.toString();
          if (queryString) {
            endpoint += `?${queryString}`;
          }
        }

        const projects = await gitlabRequest(endpoint);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(projects, null, 2),
            },
          ],
        };
      }
    );

    // Get project details
    server.tool(
      'get_gitlab_project',
      'Gets detailed information about a specific GitLab project',
      {
        projectId: z.string().describe('Project ID or path (e.g., "group/project" or numeric ID)'),
      },
      async ({ projectId }) => {
        const project = await gitlabRequest(`/projects/${encodeURIComponent(projectId)}`);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(project, null, 2),
            },
          ],
        };
      }
    );

    // List project issues
    server.tool(
      'list_gitlab_issues',
      'Lists issues for a GitLab project',
      {
        projectId: z.string().describe('Project ID or path'),
        state: z.enum(['opened', 'closed', 'all']).optional().describe('Filter by issue state'),
        labels: z.string().optional().describe('Comma-separated list of label names'),
        assigneeId: z.number().optional().describe('Filter by assignee ID'),
        milestone: z.string().optional().describe('Filter by milestone'),
        search: z.string().optional().describe('Search issues by title and description'),
        perPage: z.number().optional().describe('Number of results per page'),
        page: z.number().optional().describe('Page number'),
      },
      async ({ projectId, state, labels, assigneeId, milestone, search, perPage, page }) => {
        const params = new URLSearchParams();
        if (state) params.append('state', state);
        if (labels) params.append('labels', labels);
        if (assigneeId) params.append('assignee_id', assigneeId.toString());
        if (milestone) params.append('milestone', milestone);
        if (search) params.append('search', search);
        if (perPage) params.append('per_page', perPage.toString());
        if (page) params.append('page', page.toString());

        const queryString = params.toString();
        const endpoint = `/projects/${encodeURIComponent(projectId)}/issues${queryString ? `?${queryString}` : ''}`;
        
        const issues = await gitlabRequest(endpoint);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(issues, null, 2),
            },
          ],
        };
      }
    );

    // Get issue details
    server.tool(
      'get_gitlab_issue',
      'Gets detailed information about a specific GitLab issue',
      {
        projectId: z.string().describe('Project ID or path'),
        issueIid: z.number().describe('Issue IID (internal ID within the project)'),
      },
      async ({ projectId, issueIid }) => {
        const issue = await gitlabRequest(
          `/projects/${encodeURIComponent(projectId)}/issues/${issueIid}`
        );
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(issue, null, 2),
            },
          ],
        };
      }
    );

    // Create issue
    server.tool(
      'create_gitlab_issue',
      'Creates a new issue in a GitLab project',
      {
        projectId: z.string().describe('Project ID or path'),
        title: z.string().describe('Issue title'),
        description: z.string().optional().describe('Issue description'),
        labels: z.string().optional().describe('Comma-separated list of label names'),
        assigneeIds: z.array(z.number()).optional().describe('Array of user IDs to assign the issue to'),
        milestoneId: z.number().optional().describe('Milestone ID'),
        dueDate: z.string().optional().describe('Due date in YYYY-MM-DD format'),
      },
      async ({ projectId, title, description, labels, assigneeIds, milestoneId, dueDate }) => {
        const body: any = { title };
        if (description) body.description = description;
        if (labels) body.labels = labels;
        if (assigneeIds) body.assignee_ids = assigneeIds;
        if (milestoneId) body.milestone_id = milestoneId;
        if (dueDate) body.due_date = dueDate;

        const issue = await gitlabRequest(
          `/projects/${encodeURIComponent(projectId)}/issues`,
          {
            method: 'POST',
            body: JSON.stringify(body),
          }
        );
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(issue, null, 2),
            },
          ],
        };
      }
    );

    // List merge requests
    server.tool(
      'list_gitlab_merge_requests',
      'Lists merge requests for a GitLab project',
      {
        projectId: z.string().describe('Project ID or path'),
        state: z.enum(['opened', 'closed', 'locked', 'merged', 'all']).optional().describe('Filter by MR state'),
        labels: z.string().optional().describe('Comma-separated list of label names'),
        authorId: z.number().optional().describe('Filter by author ID'),
        assigneeId: z.number().optional().describe('Filter by assignee ID'),
        search: z.string().optional().describe('Search MRs by title and description'),
        perPage: z.number().optional().describe('Number of results per page'),
        page: z.number().optional().describe('Page number'),
      },
      async ({ projectId, state, labels, authorId, assigneeId, search, perPage, page }) => {
        const params = new URLSearchParams();
        if (state) params.append('state', state);
        if (labels) params.append('labels', labels);
        if (authorId) params.append('author_id', authorId.toString());
        if (assigneeId) params.append('assignee_id', assigneeId.toString());
        if (search) params.append('search', search);
        if (perPage) params.append('per_page', perPage.toString());
        if (page) params.append('page', page.toString());

        const queryString = params.toString();
        const endpoint = `/projects/${encodeURIComponent(projectId)}/merge_requests${queryString ? `?${queryString}` : ''}`;
        
        const mergeRequests = await gitlabRequest(endpoint);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(mergeRequests, null, 2),
            },
          ],
        };
      }
    );

    // Get merge request details
    server.tool(
      'get_gitlab_merge_request',
      'Gets detailed information about a specific GitLab merge request',
      {
        projectId: z.string().describe('Project ID or path'),
        mergeRequestIid: z.number().describe('Merge request IID (internal ID within the project)'),
      },
      async ({ projectId, mergeRequestIid }) => {
        const mergeRequest = await gitlabRequest(
          `/projects/${encodeURIComponent(projectId)}/merge_requests/${mergeRequestIid}`
        );
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(mergeRequest, null, 2),
            },
          ],
        };
      }
    );

    // List project branches
    server.tool(
      'list_gitlab_branches',
      'Lists branches for a GitLab project',
      {
        projectId: z.string().describe('Project ID or path'),
        search: z.string().optional().describe('Search branches by name'),
        perPage: z.number().optional().describe('Number of results per page'),
        page: z.number().optional().describe('Page number'),
      },
      async ({ projectId, search, perPage, page }) => {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (perPage) params.append('per_page', perPage.toString());
        if (page) params.append('page', page.toString());

        const queryString = params.toString();
        const endpoint = `/projects/${encodeURIComponent(projectId)}/repository/branches${queryString ? `?${queryString}` : ''}`;
        
        const branches = await gitlabRequest(endpoint);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(branches, null, 2),
            },
          ],
        };
      }
    );

    // List project commits
    server.tool(
      'list_gitlab_commits',
      'Lists commits for a GitLab project',
      {
        projectId: z.string().describe('Project ID or path'),
        refName: z.string().optional().describe('Branch, tag, or commit SHA to list commits from'),
        since: z.string().optional().describe('Only commits after this date (ISO 8601 format)'),
        until: z.string().optional().describe('Only commits before this date (ISO 8601 format)'),
        path: z.string().optional().describe('Only commits affecting this path'),
        author: z.string().optional().describe('Filter commits by author email'),
        perPage: z.number().optional().describe('Number of results per page'),
        page: z.number().optional().describe('Page number'),
      },
      async ({ projectId, refName, since, until, path, author, perPage, page }) => {
        const params = new URLSearchParams();
        if (refName) params.append('ref_name', refName);
        if (since) params.append('since', since);
        if (until) params.append('until', until);
        if (path) params.append('path', path);
        if (author) params.append('author', author);
        if (perPage) params.append('per_page', perPage.toString());
        if (page) params.append('page', page.toString());

        const queryString = params.toString();
        const endpoint = `/projects/${encodeURIComponent(projectId)}/repository/commits${queryString ? `?${queryString}` : ''}`;
        
        const commits = await gitlabRequest(endpoint);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(commits, null, 2),
            },
          ],
        };
      }
    );

    // Get current user
    server.tool(
      'get_gitlab_user',
      'Gets information about the authenticated user',
      {},
      async () => {
        const user = await gitlabRequest('/user');
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(user, null, 2),
            },
          ],
        };
      }
    );

    // List groups
    server.tool(
      'list_gitlab_groups',
      'Lists GitLab groups accessible to the authenticated user',
      {
        search: z.string().optional().describe('Search groups by name or path'),
        owned: z.boolean().optional().describe('Limit to groups owned by the user'),
        perPage: z.number().optional().describe('Number of results per page'),
        page: z.number().optional().describe('Page number'),
      },
      async ({ search, owned, perPage, page }) => {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (owned) params.append('owned', 'true');
        if (perPage) params.append('per_page', perPage.toString());
        if (page) params.append('page', page.toString());

        const queryString = params.toString();
        const endpoint = `/groups${queryString ? `?${queryString}` : ''}`;
        
        const groups = await gitlabRequest(endpoint);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(groups, null, 2),
            },
          ],
        };
      }
    );
  },
  {},
  { basePath: '/api' }
);

// Wrap handlers to add bearer token authentication
async function authenticatedHandler(request: Request) {
  // Validate bearer token
  if (!validateBearerToken(request)) {
    return new Response(
      JSON.stringify({ 
        error: 'Unauthorized. Provide a valid Bearer token in the Authorization header.' 
      }),
      { 
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }

  // Token is valid, proceed with the request
  return handler(request);
}

export async function GET(request: Request) {
  return authenticatedHandler(request);
}

export async function POST(request: Request) {
  return authenticatedHandler(request);
}

export async function DELETE(request: Request) {
  return authenticatedHandler(request);
}
