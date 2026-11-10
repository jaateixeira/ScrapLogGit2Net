#!/usr/bin/env bash
# Rebuilds the synthetic project of the running example (5 developers, 3 companies, 9 commits)
# and writes its git log in the format ScrapLogGit2Net expects. Usage: ./make_toy_log.sh [outdir]
set -euo pipefail
out="${1:-toy}"; rm -rf "$out"; mkdir -p "$out/repo"; cd "$out/repo"; git init -q
commit() {  # name email date message files...
  n="$1"; e="$2"; d="$3"; m="$4"; shift 4
  for f in "$@"; do mkdir -p "$(dirname "$f")"; echo "// $m by $n ($d)" >> "$f"; git add "$f"; done
  GIT_AUTHOR_NAME="$n" GIT_AUTHOR_EMAIL="$e" GIT_AUTHOR_DATE="$d" \
  GIT_COMMITTER_NAME="$n" GIT_COMMITTER_EMAIL="$e" GIT_COMMITTER_DATE="$d" git commit -q -m "$m"
}
commit Ana  ana@alpha.com  "2024-01-03T10:00:00+0000" "start scheduler and memory" core/scheduler.c core/memory.c
commit Bob  bob@alpha.com  "2024-01-08T10:00:00+0000" "fix scheduler"              core/scheduler.c
commit Cleo cleo@beta.org  "2024-01-15T10:00:00+0000" "scheduler hook and driver"  core/scheduler.c net/driver.c
commit Dan  dan@beta.org   "2024-01-22T10:00:00+0000" "driver fix"                 net/driver.c
commit Eli  eli@gamma.io   "2024-02-02T10:00:00+0000" "driver docs"                net/driver.c docs/guide.md
commit Bob  bob@alpha.com  "2024-02-12T10:00:00+0000" "guide update"               docs/guide.md
commit Ana  ana@alpha.com  "2024-02-20T10:00:00+0000" "memory tuning"              core/memory.c
commit Eli  eli@gamma.io   "2024-03-05T10:00:00+0000" "add tests"                  tests/test_core.c
commit Dan  dan@beta.org   "2024-03-11T10:00:00+0000" "driver cleanup"             net/driver.c
git log --pretty=format:"==%an;%ae;%ad==" --name-only > ../toy.IN
echo "wrote $out/toy.IN"
