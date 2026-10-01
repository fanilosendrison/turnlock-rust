---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "agent-directives"
domain: "turnlock-rust-repository-governance"
severity: "strict"
name: "Turnlock-Rust worktree management policy"
---

# Turnlock-Rust worktree management policy

## Purpose and authority

Use this policy to specialize the enclosing workspace's global Git
workspace-isolation rule for Turnlock-Rust.

Treat [AGENTS.md](../../AGENTS.md) as the authority for repository execution
guardrails. Treat the global operational implementation rules as authority for
generic task-worktree isolation, ownership, lifecycle, post-publication
persistent-checkout reconciliation, and cleanup. This document owns only the
Turnlock-Rust base, path namespace, detached mode, publication, synchronization,
and topology specializations.

Treat Git refs, remote-tracking refs, and Git worktree metadata as authority for
repository and worktree state. Do not maintain a second inventory in
documentation.

This policy affects repository governance only. It creates no TURNLOCK product
semantics, architecture commitment, formal-verification claim, or qualification
evidence.

## Repository roles

Define:

```text
PERSISTENT_CHECKOUT =
the normal user-owned non-bare turnlock-rust repository
```

Define:

```text
TASK_WORKTREE_ROOT =
$HOME/Developper/Projects/.worktrees/turnlock-rust
```

Define:

```text
TASK_WORKTREE =
TASK_WORKTREE_ROOT/<unique-task-id>
```

The persistent checkout normally has `refs/heads/main` checked out. It is task
infrastructure, not a task workspace.

There is no operational role for a dedicated main worktree, primary development
worktree, permanent detached worktree, or permanent integration worktree. A path
name never creates such a role. No permanent agent worktree exists.

## Persistent-checkout boundary

Apply the global persistent-checkout boundary. In particular, do not modify or
clean the persistent checkout to prepare a Turnlock-Rust task, and do not let
tracked edits, untracked files, or ignored user state there block task creation.

Fetching remote metadata and administering linked worktrees through the
persistent repository are not task-file edits.

## Task creation

Before every task, fetch current remote authority:

```bash
git -C <PERSISTENT_CHECKOUT> fetch origin
```

Record exactly:

```text
TASK_BASE = origin/main
```

Create one unique detached linked worktree:

```bash
git -C <PERSISTENT_CHECKOUT> worktree add \
  --detach \
  "$HOME/Developper/Projects/.worktrees/turnlock-rust/<unique-task-id>" \
  origin/main
```

Require:

```text
detached HEAD
HEAD == TASK_BASE
clean
operation-free
```

Operation-free means no active `MERGE_HEAD`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`,
`rebase-merge`, `rebase-apply`, `BISECT_LOG`, or `sequencer` state.

Do not require a temporary task branch.

## Task execution and validation

Apply the global task ownership and isolation rules. Perform all Turnlock-Rust
task writes, commits, validation-environment creation, generated-task-artifact
creation, reconciliation, validation, and publication preparation inside the
task worktree.

Run the repository's mandatory validation contract from [AGENTS.md](../../AGENTS.md)
inside that task worktree. Do not create task validation state in the persistent
checkout.

Only publication to `refs/heads/main` is serialized. Independent task worktrees
may otherwise coexist.

## Detached commits

Keep the task worktree on detached `HEAD`. The canonical installed
`git-commits-push` targeted invocation is the sole supported task
commit/publication mutator and may create one or more task commits directly on
that detached `HEAD`.

Do not create a temporary transport branch and do not use raw `git commit`,
`git commit-tree`, or `git push`.

If a targeted invocation creates task commits but publication does not complete,
preserve the task worktree and its detached commit chain for reconciliation and
retry. Do not remove the worktree merely because its `HEAD` is detached.

## Pre-publication synchronization

Immediately before targeted publication, fetch again:

```bash
git -C <PERSISTENT_CHECKOUT> fetch origin
```

Let:

```text
CURRENT_MAIN = origin/main
TASK_HEAD = exact current task-worktree HEAD
```

If `CURRENT_MAIN == TASK_BASE`, continue after final validation.

If `CURRENT_MAIN != TASK_BASE`, re-evaluate the exact semantic, source, and blob
guards specified by the task before changing the task worktree.

If `TASK_HEAD == TASK_BASE`, no task commit exists yet. Move only the current
detached task worktree to the exact current remote base:

```bash
git -C <TASK_WORKTREE> switch --detach <CURRENT_MAIN>
```

This operation may carry the task's uncommitted changes only when Git can do so
without overwriting them. Never force the switch, stash task state, discard
changes, or resolve a conflict automatically.

After a successful switch require:

```text
HEAD == CURRENT_MAIN
HEAD is detached
the intended task changes are still present
```

If Git refuses the switch or the intended task changes cannot be proven
preserved:

```text
STOP
preserve the task worktree
```

If `TASK_HEAD != TASK_BASE`, task commits already exist. Require the task
worktree to contain no additional tracked or untracked non-ignored changes and
no active Git operation, then replay only the current task commit range onto the
exact current remote base:

```bash
git -C <TASK_WORKTREE> rebase \
  --onto <CURRENT_MAIN> \
  <TASK_BASE> \
  <TASK_HEAD>
```

Create no merge commit.

If the rebase conflicts, an authority guard changes, or any ambiguity appears:

```text
STOP
preserve the task worktree
```

After either successful reconciliation path, set:

```text
TASK_BASE = CURRENT_MAIN
```

Then re-evaluate all task guards and rerun complete repository validation before
publication.

## Publication

Require current `origin/main` to be ancestor-or-equal to the task worktree's
current `HEAD`.

Publish and create any still-uncommitted task commits only through the canonical
installed `git-commits-push` targeted mode:

```bash
"$HOME/.local/bin/git-commits-push" \
  --repository "/absolute/path/to/exact-task-worktree" \
  --push-remote origin \
  --push-ref refs/heads/main
```

At execution time, replace `/absolute/path/to/exact-task-worktree` with the
concrete canonical absolute task-worktree path as a literal shell-quoted static
argument. Do not pass a shell variable, command substitution, relative path, or
placeholder to the executable.

The targeted invocation owns the commit/publication mutation boundary. It must
remain bound to exactly:

```text
repository = exact current task worktree
remote = origin
destination = refs/heads/main
```

Do not use raw `git commit`, `git commit-tree`, or `git push`. Do not create a
temporary publication branch, configure an upstream, or persist
`push.default`, `branch.*.remote`, or `branch.*.merge` to make publication
possible.

`git-commits-push` is responsible for freezing the explicit remote destination,
creating the task commit or commits directly on detached `HEAD`, performing its
exact-SHA fast-forward publication checks, and verifying the resulting remote
destination.

If the explicit destination moves and `git-commits-push` refuses stale
publication, do not bypass it. Preserve the task worktree, fetch current
`origin/main`, apply the pre-publication synchronization procedure above,
re-evaluate the task guards, rerun complete validation, and retry the same
targeted invocation.

For any other publication failure:

```text
STOP
preserve the task worktree
```

Never force-push `main` and never publish another task's commit.

## Post-publication proof and cleanup

After successful publication, fetch `origin/main` again and require task `HEAD`
to be ancestor-or-equal to current `origin/main`. Remote `main` may already
contain later concurrent commits; equality is not required.

Complete any required validation of the exact published state before persistent
checkout reconciliation.

Then apply the global post-publication persistent-checkout reconciliation rule
before successful task-worktree cleanup.

After reconciliation succeeds or is safely skipped because its preconditions do
not hold, apply the global successful-task-worktree cleanup rule. Remove exactly
the published task worktree and run:

```bash
git -C <PERSISTENT_CHECKOUT> worktree prune
```

Verify that its worktree record disappeared. Never remove the persistent
checkout.

Preserve failed, interrupted, conflicted, or unpublished task worktrees under
the global preservation rule. Report the preserved worktree's path, `TASK_BASE`,
`HEAD`, and preservation reason so a later operator can recover it safely.

## Persistent-checkout synchronization

Apply the enclosing workspace's global post-publication persistent-checkout
reconciliation rule.

For Turnlock-Rust, specialize the generic rule as:

```text
EXPECTED_TARGET_BRANCH = main
REMOTE = origin
REMOTE_TARGET_REF = origin/main
```

After the required fresh fetch, capture the exact `origin/main` object identity.

If the normal persistent checkout has `main` checked out, is completely clean,
is operation-free, and its current `HEAD` is ancestor-or-equal to that captured
target object, fast-forward synchronization to that exact object is mandatory.

Use only:

```bash
git -C <PERSISTENT_CHECKOUT> merge --ff-only <CAPTURED_ORIGIN_MAIN_OID>
```

and verify afterward that persistent-checkout `HEAD` equals the captured target
OID.

If any generic synchronization precondition does not hold, preserve the
persistent checkout exactly as found and report its current branch, local
`HEAD`, captured `origin/main` OID, and the failed precondition.

Never stash, clean, reset, restore, switch, rebase, create a non-fast-forward
merge, or commit user state merely to synchronize the persistent checkout.

Turnlock-Rust adds no exception that permits a safely fast-forwardable
persistent checkout to remain stale.

## Normal topology

When no task is active and no failed, interrupted, conflicted, or unpublished
task worktree requires preservation:

```text
turnlock-rust/
    normal non-bare repository
    main checked out

.worktrees/
    turnlock-rust/
        no task worktrees
```

During parallel tasks:

```text
turnlock-rust/
    normal user checkout

.worktrees/
    turnlock-rust/
        <unique-task-id-1>/
        <unique-task-id-2>/
```

After all successful task worktrees are removed, `turnlock-rust/` remains as the
permanent user checkout. The shared `.worktrees/` root and empty repository
namespace may remain as task infrastructure.
