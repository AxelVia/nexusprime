"""GitHub integration client."""

from __future__ import annotations

import os
from typing import Optional

from github import Github
from github.Repository import Repository

from ..utils.logging import get_logger
from ..utils.security import get_required_env

logger = get_logger(__name__)


class GitHubClient:
    """Client for GitHub API operations."""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.
        
        Args:
            token: GitHub token (if None, reads from environment)
        """
        if token is None:
            token = get_required_env("GITHUB_TOKEN")
        
        self.github = Github(token)
        self.user = self.github.get_user()
        logger.info(f"GitHub client initialized for user: {self.user.login}")
    
    def get_or_create_repo(self, repo_name: str, description: str = "", private: bool = True) -> Repository:
        """
        Get existing repository or create new one.
        
        Args:
            repo_name: Repository name
            description: Repository description
            private: Whether repository should be private
        
        Returns:
            Repository object
        """
        try:
            repo = self.user.get_repo(repo_name)
            logger.info(f"Found existing repo: {repo.html_url}")
            return repo
        except Exception as e:
            logger.info(f"Repository {repo_name} not found, creating new one")
            try:
                repo = self.user.create_repo(
                    repo_name,
                    description=description,
                    private=private
                )
                logger.info(f"Created new repo: {repo.html_url}")
                return repo
            except Exception as create_error:
                logger.error(f"Failed to create repository: {create_error}")
                raise
    
    def create_or_update_file(
        self,
        repo: Repository,
        file_path: str,
        content: str,
        commit_message: str
    ) -> None:
        """
        Create or update a file in repository.
        
        Args:
            repo: Repository object
            file_path: Path to file in repository
            content: File content
            commit_message: Commit message
        """
        try:
            # Try to get existing file
            contents = repo.get_contents(file_path)
            repo.update_file(
                contents.path,
                commit_message,
                content,
                contents.sha
            )
            logger.info(f"Updated file: {file_path}")
        except Exception:
            # File doesn't exist, create it
            try:
                repo.create_file(
                    file_path,
                    commit_message,
                    content
                )
                logger.info(f"Created file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to create/update file {file_path}: {e}")
                raise
    
    def push_local_file(
        self,
        repo: Repository,
        local_path: str,
        repo_path: str,
        commit_message: str
    ) -> None:
        """
        Push a local file to repository.
        
        Args:
            repo: Repository object
            local_path: Path to local file
            repo_path: Destination path in repository
            commit_message: Commit message
        """
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.create_or_update_file(repo, repo_path, content, commit_message)
        except (OSError, IOError) as e:
            logger.error(f"Failed to read local file {local_path}: {e}")
            raise
