"""
Central module for all Git-related data classes in ScrapLogGit2Net.
Now using pathlib.Path for all file system paths.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union
from utils.validators import validate_git_commit_block

@dataclass
class GitEmail:
    """Represents a validated Git email address"""
    value: str
    
    def __post_init__(self):
        from utils.validators import validate_git_email
        valid, msg = validate_git_email(self.value)
        if not valid:
            raise ValueError(f"Invalid Git email: {msg}")

@dataclass 
class GitName:
    """Represents a validated Git author name"""
    value: str
    
    def __post_init__(self):
        from utils.validators import validate_git_name
        valid, msg = validate_git_name(self.value)
        if not valid:
            raise ValueError(f"Invalid Git name: {msg}")

@dataclass
class GitCommitBlock:
    """
    Represents a validated Git commit message block
    with proper Path objects for files
    """
    hash: str
    author: GitName
    email: GitEmail
    timestamp: datetime
    message: str
    files: List[Path]  # Changed from List[str]
    
    @classmethod
    def from_raw(cls, raw_block: str, repo_root: Union[str, Path]):
        """
        Alternative constructor from raw git log output
        Args:
            raw_block: Raw git log output
            repo_root: Repository root path (converted to Path)
        """
        repo_root = Path(repo_root) if repo_root else None
        
        # Your parsing logic here
        parsed_data = parse_git_log(raw_block)  # Implement this
        
        return cls(
            hash=parsed_data['hash'],
            author=GitName(parsed_data['author']),
            email=GitEmail(parsed_data['email']),
            timestamp=parsed_data['timestamp'],
            message=parsed_data['message'],
            files=[repo_root.joinpath(f) if repo_root else Path(f) 
                  for f in parsed_data['files']]
        )
        
    def validate(self):
        """Validate all commit components"""
        valid, msg = validate_git_commit_block(
            self.author.value,
            self.email.value,
            str(int(self.timestamp.timestamp())) + " +0000",
            [str(f) for f in self.files]  # Convert Path to str for validation
        )
        if not valid:
            raise ValueError(f"Commit validation failed: {msg}")

    def get_relative_files(self, base_path: Union[str, Path]) -> List[Path]:
        """Returns files relative to given base path"""
        base = Path(base_path)
        return [f.relative_to(base) for f in self.files if base in f.parents]

@dataclass
class GitLog:
    """Represents a collection of Git commits with Path objects"""
    commits: List[GitCommitBlock]
    repository: 'Repository'  # Forward reference
    
    def filter_by_author(self, author: GitName) -> 'GitLog':
        """Return filtered log by author"""
        return GitLog(
            commits=[c for c in self.commits if c.author == author],
            repository=self.repository
        )
    
    def get_all_files(self) -> List[Path]:
        """Get all unique files referenced in commits"""
        return list({f for commit in self.commits for f in commit.files})

@dataclass
class Repository:
    """Represents a Git repository with Path objects"""
    path: Path  # Changed from str
    name: str
    remote_url: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        self.path = Path(self.path) if not isinstance(self.path, Path) else self.path
    
    def get_commits(self) -> GitLog:
        """Retrieve commits from this repository"""
        # Your implementation here
        return GitLog(
            commits=[],  # Populate with actual commits
            repository=self
        )

@dataclass
class RepositoryCollection:
    """Collection of multiple Git repositories"""
    repositories: List[Repository]
    
    def get_all_commits(self) -> Dict[str, GitLog]:
        """Get commits from all repositories"""
        return {
            repo.name: repo.get_commits()
            for repo in self.repositories
        }
