#!/usr/bin/env bash
# Gate A #78 — local exact-old + descendant-only Git experiment.
# Destructive only to a temporary directory. Never contacts GitHub.
set -euo pipefail
umask 077
root=$(mktemp -d)
trap 'rm -rf "$root"' EXIT
export HOME="$root/home" XDG_CONFIG_HOME="$root/xdg" GIT_CONFIG_NOSYSTEM=1
mkdir -p "$HOME" "$XDG_CONFIG_HOME"
repo="$root/src"
remote="$root/remote.git"
mkdir -p "$repo"
git -C "$root" init -q -b main src
cd "$repo"
git config user.name 'Test Runner'
git config user.email 'test-runner@example.invalid'
git config commit.gpgsign false
printf 'P\n' > state
git add state
git commit -qm P
P=$(git rev-parse HEAD)
printf 'T\n' >> state
git commit -qam T
T=$(git rev-parse HEAD)
printf 'V\n' >> state
git commit -qam V
V=$(git rev-parse HEAD)
git init -q --bare "$remote"
git push -q "$remote" "$P:refs/heads/main"
git --git-dir="$remote" config receive.denyNonFastForwards true
git --git-dir="$remote" config receive.denyDeletes true

check_tip() {
  local got
  got=$(git --git-dir="$remote" rev-parse refs/heads/main)
  [[ "$got" == "$1" ]] || {
    printf 'FAIL current=%s expected=%s\n' "$got" "$1"
    exit 1
  }
}
push_exact() {
  local expect="$1" candidate="$2"
  git -c push.default=nothing push --porcelain \
    "--force-with-lease=refs/heads/main:$expect" \
    "$remote" "$candidate:refs/heads/main"
}

push_exact "$P" "$T" > "$root/c1.log" 2>&1
check_tip "$T"
printf 'PASS C1 expected P -> T fast-forward\n'

if push_exact "$P" "$V" > "$root/c2.log" 2>&1; then
  echo 'FAIL C2 stale predecessor accepted'; exit 1
fi
check_tip "$T"
grep -q 'stale info' "$root/c2.log"
printf 'PASS C2 stale P rejected, even though T ancestor V\n'

push_exact "$T" "$V" > "$root/c3.log" 2>&1
check_tip "$V"
printf 'PASS C3 expected T -> V fast-forward\n'

if push_exact "$V" "$P" > "$root/c4.log" 2>&1; then
  echo 'FAIL C4 non-FF accepted'; exit 1
fi
check_tip "$V"
grep -q -e 'denying non-fast-forward' -e 'denied' "$root/c4.log"
printf 'PASS C4 non-FF rejected by configured receiver protection\n'
printf 'SOURCE_GIT_VERSION=%s\n' "$(git --version)"
printf 'RESULT=LOCAL_ONLY_FOUR_CASES_PASS\n'
