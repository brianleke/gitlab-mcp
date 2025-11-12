"""
Shared GitLab client utility for API routes.
"""

import os
import gitlab
from typing import Optional

# Global GitLab client instance
_gl: Optional[gitlab.Gitlab] = None


def get_gitlab_client() -> gitlab.Gitlab:
    """Get or create the GitLab client instance."""
    global _gl
    if _gl is None:
        gitlab_url = os.getenv("GITLAB_URL", "https://gitlab.com")
        gitlab_token = os.getenv("GITLAB_TOKEN")
        
        if not gitlab_token:
            raise ValueError(
                "GITLAB_TOKEN environment variable is required. "
                "Get a personal access token from GitLab with 'api' scope."
            )
        
        _gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
        _gl.auth()
    
    return _gl

