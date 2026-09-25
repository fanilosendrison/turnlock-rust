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

Create task commits directly on detached `HEAD`. The task worktree retains the
detached commit chain before publication. Do not remove an unpublished task
worktree merely because its `HEAD` is detached.

## Pre-publication synchronization

Immediately before publication, fetch again:

```bash
git -C <PERSISTENT_CHECKOUT> fetch origin
```

Let:

```text
CURRENT_MAIN = origin/main
```

If `CURRENT_MAIN == TASK_BASE`, continue after final validation.

If `CURRENT_MAIN != TASK_BASE`, re-evaluate the exact semantic, source, and blob
guards specified by the task. When automatic continuation is authorized, replay
only `TASK_BASE..HEAD` onto current `origin/main`. Create no merge commit unless
separate authority explicitly requires one.

If a conflict, authority change, source-guard failure, or ambiguity appears:

```text
STOP
preserve the task worktree
```

After successful replay, set `TASK_BASE = CURRENT_MAIN`, then rerun complete
task validation.

## Publication

Require current `origin/main` to be an ancestor of task `HEAD`.

Publish only:

```bash
git push origin HEAD:refs/heads/main
```

Use an ordinary fast-forward push only. Never force-push `main`, use
force-with-lease to rewrite `main`, delete `main`, or push another task's
commit.

If another task advances `main` and publication is rejected, fetch again,
re-evaluate the current task's guards, reconcile when permitted, rerun complete
validation, and retry an ordinary fast-forward push.

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
