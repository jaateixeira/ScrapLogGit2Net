# deanonymize_github_users.py

`deanonymize_github_users.py` looks up developers who commit with a GitHub "noreply" e-mail address (`...@users.noreply.github.com`) and fills in their affiliation from their GitHub profile. It reads a GraphML network of individuals, queries the GitHub REST API for each noreply address, and writes a corrected copy of the network. Use it after `scrapLog.py` when many developers in a network have no real affiliation because they hide their e-mail on GitHub.

## Run it

From the repository root:

```bash
./deanonymize_github_users.py [--config CONFIG] [--skip-api-test] input [output]
```

After `pip install -e .` the same tool is available as a console command:

```bash
deanonymize-github-users [--config CONFIG] [--skip-api-test] input [output]
```

You need a GitHub personal access token (see [GitHub token](#github-token)).

## Input

- `input`: a GraphML file whose name ends in `.graphml` (any letter case, so `.graphML` works). Any other extension stops the tool with status 1. A missing file also stops it with status 1.
- The tool reads the `e-mail` and `affiliation` node attributes, as written by `scrapLog.py`.

### GitHub token

The token is looked up in this order:

1. The `GITHUB_TOKEN` environment variable. If it is set, nothing else is read.
2. The file given with `--config`.
3. A file named `config.ini` in the current working directory.

A config file must have this form:

```ini
[github]
token = <your token>
```

If no token is found, the tool prints the ways to provide one, points to `https://github.com/settings/tokens/`, and exits with status 1.

## Output

- The corrected network as GraphML. If you do not give `output`, the name is the input path with its extension replaced by `.out.graphml`, in the same directory. For example, `test-data/net.graphML` gives `test-data/net.out.graphml`. An existing file with that name is overwritten.
- The input file is not changed.
- A cache file `github_cache.sqlite` in the current working directory (see [Notes and limitations](#notes-and-limitations)).
- Terminal output: a line for every node checked, a table with the GitHub profile data of each user looked up, and each user's organizations.

### What is changed

Only nodes whose `e-mail` attribute contains `@users.noreply.github.com` are changed. For each such node:

1. The GitHub user name is taken from the address: the part between `+` and `@` (for `12345+octocat@users.noreply.github.com` this is `octocat`), or the part before `@` if there is no `+`.
2. The user's GitHub profile is fetched.
3. **Affiliation:** the `company` field of the profile is used. If the user is a public member of one or more GitHub organizations, the first organization's login is used instead. The value is converted to lower case and written to the `affiliation` attribute. If neither is found, `affiliation` is not changed.
4. **E-mail:** if the profile shows a public e-mail address, it replaces the noreply address in the `e-mail` attribute, the attribute that `scrapLog.py` writes and the other tools read. If not, `e-mail` is not changed.

If GitHub returns an error for a user (for example, the user does not exist), a warning is logged and the node is left unchanged.

## Options

| Option | Meaning | Default |
|---|---|---|
| `input` | Path to the input GraphML file. | required |
| `output` | Path to the output GraphML file. | `<input without extension>.out.graphml` |
| `-h`, `--help` | Show the help message and exit. | |
| `--config CONFIG` | Path to an INI file with a `[github]` section and a `token` key. Used only when `GITHUB_TOKEN` is not set. If the token is not found there, `config.ini` in the current directory is tried. | none (then `config.ini`) |
| `--skip-api-test` | Do not test the token before processing. Without this option, the tool first calls the GitHub API to check the token (it stops with status 1 if the token is invalid) and prints a table of your rate limits. | off (test runs) |

## Examples

These examples were not run while writing this page, because they call the GitHub API and need a token. Only `--help` was run (exit status 0).

Use a token from the environment and write the default output file (`test-data/5-pentagon-with-star.out.graphml`):

```bash
export GITHUB_TOKEN=<your token>
./deanonymize_github_users.py test-data/5-pentagon-with-star.graphML
```

Read the token from a config file and choose the output name:

```bash
./deanonymize_github_users.py --config my-config.ini test-data/5-pentagon-with-star.graphML deanonymized.graphml
```

Show the help text:

```bash
./deanonymize_github_users.py --help
```

## Notes and limitations

- **The token is not printed.** When it checks the configuration, the tool shows only the first 8 characters of the token followed by `...`. The HTTP cache (`github_cache.sqlite`) does not store the `Authorization` header by default.
- **Rate limits.** Each noreply user costs at least two API calls (profile and organizations). If GitHub reports that the rate limit is exceeded during processing, the tool sleeps for one hour and then tries again. A large network can take a long time.
- **Caching.** Results are kept in memory per e-mail address during a run, so each address is looked up once. HTTP responses from the `requests` library are also cached in `github_cache.sqlite` in the current working directory, and cached entries expire after one hour. This file is created on start-up, even when you run only `--help`.
- Only public profile data is used. Users who hide their e-mail, company or organization memberships stay unchanged.
- The first organization listed by GitHub is taken as the affiliation. It may not be the user's employer.
- The output is written as an undirected graph. Graph-level attributes of the input file are not copied.

[Back to the README](../../README.md#executable-toolsscripts)
