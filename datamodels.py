"""
Data models with integrated validation from utils.validators
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Union
from utils.validators import (
    validate_git_name,
    validate_git_email,
    validate_git_time,
    validate_git_files,
    validate_git_commit_block
)

@dataclass
class GitEmail:
    """Validated Git email using utils.validators"""
    value: str
    
    def __post_init__(self):
        valid, msg = validate_git_email(self.value)
        if not valid:
            raise ValueError(msg)

@dataclass 
class GitName:
    """Validated Git name using utils.validators"""
    value: str
    
    def __post_init__(self):
        valid, msg = validate_git_name(self.value)
        if not valid:
            raise ValueError(msg)

@dataclass
class GitCommitBlock:
    """Git commit with integrated validation"""
    hash: str
    author: GitName
    email: GitEmail
    timestamp: datetime
    message: str
    files: List[Path]
    
    @classmethod
    def from_raw(cls, raw_block: str, repo_root: Union[str, Path] = None):
        """Create from raw git log with validation"""
        repo_root = Path(repo_root) if repo_root else None
        # Parse logic here (example)
        parsed = {
            'hash': 'abc123',
            'author': 'Valid Name',
            'email': 'valid@example.com',
            'timestamp': datetime.now(),
            'message': 'commit message',
            'files': ['file1.txt', 'file2.py']
        }
        
        # Validate during creation
        valid, msg = validate_git_commit_block(
            parsed['author'],
            parsed['email'],
            str(int(parsed['timestamp'].timestamp())) + " +0000",
            parsed['files']
        )
        if not valid:
            raise ValueError(msg)
            
        return cls(
            hash=parsed['hash'],
            author=GitName(parsed['author']),
            email=GitEmail(parsed['email']),
            timestamp=parsed['timestamp'],
            message=parsed['message'],
            files=[repo_root.joinpath(f) if repo_root else Path(f) for f in parsed['files']]
        )

@dataclass
class GitLog:
    """Collection of validated commits"""
    commits: List[GitCommitBlock]
    repository: 'Repository'

@dataclass
class Repository:
    """Git repository with path validation"""
    path: Path
    name: str
    remote_url: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.path, Path):
            self.path = Path(self.path)
        if not self.path.exists():
            raise ValueError(f"Repository path does not exist: {self.path}")
