# scrap_repo_repositories_logs.py

`scrap_repo_repositories_logs.py` is an experimental, unfinished tool. Its module docstring says it is meant to mine all repository logs of a repository or directory, filter by year range or release names, and build networks for every branch. In the current code it only does part of this: it lists the remote branches of a local Git repository, checks out each one, and prints a table with the first and last commit date per branch. It writes no log files and no networks.

## Run it

From the repository root:

```
./scrap_repo_repositories_logs.py <input_dir> [options]
```

After `pip install -e .` the same tool is available as the console command `scrap-repo-repositories-logs`:

```
scrap-repo-repositories-logs <input_dir> [options]
```

## Input

`input_dir` must be a folder that is a local Git repository with a `.git` folder. The tool checks this with `git rev-parse --git-dir` and then needs `.git` to exist in that folder.

The help text describes `input_dir` as a "Directory containing gramphML files to process", and the tool description says "Deanonymize GitHub noreply emails in gramphML files". Both are copied from another tool and do not match the code: the folder must be a Git repository, and no GraphML file is read.

## Output

Console output only. No files are written.

When `--releases` is not given, the tool:

1. Lists the tags of the repository (`git tag -l`). The list is not used further.
2. Lists the remote branches (`git branch -r`), skips the `HEAD` entry, and removes an `origin/` prefix.
3. Removes an `agl/` prefix, and drops branches that start with `sandbox/` or `m/`.
4. For each remaining branch, runs `git checkout <branch>` in the repository, then reads the date of the last commit (`git log -1`) and of a root commit (`git rev-list --max-parents=0 HEAD`). It prints a "Release Commit Timeline" table with the first commit, last commit, and duration in days per branch.
5. Prints the last commit dates, and checks out the first branch again to print the project kick-off date.

The step that would write a Git log per release (`get_git_logs_for_each_release`) is commented out in `main()`, with the comment "Not really working that part. By 27th changed instead to bash scripts".

## Options

| Option | Meaning | Default |
|---|---|---|
| `input_dir` | The local Git repository to process. Required. If it is not a folder, the tool stops with "Input directory does not exist" and exit code 1. If it is a folder but not a Git repository, the tool logs "Not a git repository" and exits with code 1. | none (required) |
| `-h`, `--help` | Show the help message and exit. | |
| `--releases [RELEASE ...]` | Meant to process only the listed releases. When it is given with at least one name, the tool does nothing after checking that `input_dir` is a Git repository: all the work is in the branch that runs when `--releases` is not given. | not set (all branches) |
| `--verbose`, `-v` | Log level: none gives warnings only, `-v` gives info messages, `-vv` (or more) gives debug messages and also prints the branch list after each cleaning step. | `0` |

## Examples

These examples were not run when writing this page. They come from the code and the help text. Run them on a clone you do not mind changing, because the tool checks out branches in it.

Print the commit timeline of every remote branch of a local clone:

```
./scrap_repo_repositories_logs.py path/to/local/repository
```

The same, with info messages:

```
./scrap_repo_repositories_logs.py path/to/local/repository -v
```

## Notes and limitations

- Experimental and unfinished. `--releases` only turns the processing off. There is no dry-run mode: the tool always checks out every branch, so run it on a clone you do not mind changing.
- The tool changes the repository: it runs `git checkout` for every branch, so the repository is left on the first branch of the list. Do not run it on a repository with uncommitted work.
- The tool does not clone or fetch. It works only with the remote branches the local clone already knows.
- If a checkout fails, the error is printed and the tool goes on with the next command, so the dates come from whatever is checked out.
- If a commit date cannot be read, the timeline step stops the tool with exit code 1.
- The branch cleaning (`agl/`, `sandbox/`, `m/`) is specific to one project.
- The unused per-release log step needs the external `repo` tool in your `PATH`.

[Back to the README](../../README.md#executable-toolsscripts)
