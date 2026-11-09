from pydriller import Repository
from pydriller.metrics.process.lines_count import LinesCount

def get_file_changes_by_commit_pydriller(repo_path, commit_hash, file_path):
    """Get added/deleted lines using PyDriller"""
    for commit in Repository(repo_path, single=commit_hash).traverse_commits():
        for modification in commit.modified_files:
            if modification.filename == file_path or modification.new_path == file_path:
                return {
                    'added': modification.added_lines,
                    'deleted': modification.deleted_lines,
                    'total': modification.added_lines + modification.deleted_lines,
                    'old_path': modification.old_path,
                    'new_path': modification.new_path,
                    'change_type': modification.change_type.name
                }
    return None

# Get all commits for a file with changes
def get_file_history_pydriller(repo_path, file_path, from_commit=None, to_commit=None):
    """Get complete history for a file"""
    changes = []
    
    # Traverse repository or commit range
    repo = Repository(repo_path, 
                     from_commit=from_commit,
                     to_commit=to_commit,
                     only_modifications_with_file_paths=[file_path])
    
    for commit in repo.traverse_commits():
        for modification in commit.modified_files:
            # Match by filename or path
            if (modification.filename == file_path or 
                modification.new_path == file_path or 
                modification.old_path == file_path):
                
                changes.append({
                    'commit_hash': commit.hash,
                    'author': commit.author.name,
                    'date': commit.committer_date,
                    'message': commit.msg,
                    'file': modification.filename,
                    'added': modification.added_lines,
                    'deleted': modification.deleted_lines,
                    'total': modification.added_lines + modification.deleted_lines,
                    'change_type': modification.change_type.name
                })
    
    return changes

# Example usage
changes = get_file_history_pydriller('/path/to/repo', 'src/main.py')
for change in changes:
    print(f"{change['commit_hash'][:8]} - {change['author']}: +{change['added']} -{change['deleted']}")
