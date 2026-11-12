# solo_contributors.py

`solo_contributors.py` reads a raw Git log and counts, per study period, the developers who only touched files that no other developer touched in that period. These developers have no co-edit, so they do not appear in a co-editing network built by `scrapLog.py`. Use it to see how many developers a co-editing network leaves out.

## Run it

From the repository root:

```
./solo_contributors.py --log <raw git log> [options]
```

After `pip install -e .` the same tool is available as the console command `solo-contributors`:

```
solo-contributors --log <raw git log> [options]
```

## Input

The same raw Git log that `scrapLog.py` reads, made with `git log --pretty=format:"==%an;%ae;%ad==" --name-only`:

```
==Name;email;timestamp==
path/to/file1
path/to/file2
==Name2;email2;timestamp==
...
```

- A header line must match `==name;email;timestamp==`. Every other non-blank line after a header is a file of that commit. Lines before the first header are ignored.
- The timestamp is read as an email-style date (the Git default `Thu Mar 28 04:29:52 2024 -0700`) or as `%Y-%m-%d %H:%M:%S %z`.
- A developer is `Name <email>`, with the email in lower case. With `--by-email`, the developer is the lower-case email only.
- The file is read as UTF-8; invalid bytes are replaced.

The study periods are fixed in the code (`PERIODS` in `scraplog/analysis/solo_contributors.py`), in UTC:

| Period | From | To |
|---|---|---|
| `pre` | 2019-09-01 | 2022-08-31 |
| `washout` | 2022-09-01 | 2023-01-31 |
| `post` | 2023-02-01 | 2026-01-31 |

Commits outside these dates, or with a timestamp that cannot be read, are not counted in any period.

## Output

A summary on standard output. For each period it shows:

- developers in total, split into collaborative (visible: touched at least one co-edited file) and solo-only (invisible: touched only files nobody else touched);
- files in total, split into co-edited (more than one developer) and solo-edited (exactly one developer).

A period without commits shows "no commits in window". The project label is `--project`, or the log file name without its extension.

Optionally, it also prints the solo-only developers of each period (`--list-developers`) and every solo-edited file with its developer (`--list-files`), and writes two CSV files (`--csv`) next to the log file: `<log>_solo_summary.csv` and `<log>_solo_files.csv`, where `<log>` is the log file name without its extension.

## Options

| Option | Meaning | Default |
|---|---|---|
| `-h`, `--help` | Show the help message and exit. | |
| `--version` | Show the program name and the ScrapLogGit2Net version, then exit. | |
| `--log LOG` | The raw Git log to read. Required. If no commit is parsed, the tool prints "ERROR: no commits parsed from LOG" and exits with code 1. | none (required) |
| `--project PROJECT` | Project label printed in the summary and written to the CSV files. | the log file name without its extension |
| `--by-email` | Identify developers by email only, instead of `Name <email>`. One person who used several names with the same email then counts once. | off |
| `--list-developers` | Print the solo-only developers of each period. | off |
| `--list-files` | Print every solo-edited file with its developer, per period. | off |
| `--csv` | Write `<log>_solo_summary.csv` and `<log>_solo_files.csv` in the folder of the log file. | off |

## Examples

Count solo-only developers in the TensorFlow log (January to March 2024). In the `post` period the summary shows 279 developers, of whom 256 are collaborative and 23 are solo-only, and 8466 files, of which 5151 are solo-edited:

```
./solo_contributors.py --log test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024.IN --project TensorFlow
```

Identify developers by email only, on a small test log where no file is co-edited (3 developers, all solo-only):

```
./solo_contributors.py --log test-data/TensorFlow/tensorFlowGitLog-3-commits-0-edges.IN --by-email
```

List the solo-only developers and solo-edited files of each period, and write the two CSV files next to the log (`test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024_solo_summary.csv` and `..._solo_files.csv`):

```
./solo_contributors.py --log test-data/TensorFlow/tensorFlowGitLog-first-trimester-2024.IN --project TensorFlow --list-developers --list-files --csv
```

## Notes and limitations

- The study periods are fixed in the code. To use other periods, edit `PERIODS`.
- The counts are per period. A developer can be solo-only in one period and collaborative in another.
- Developers are not filtered: bots and other emails count like everyone else. There is no equivalent of the `-fe` or `-ff` filters of `scrapLog.py`.
- With `--csv`, the CSV files are written next to the log file, not in the current directory.

[Back to the README](../../README.md#executable-toolsscripts)
