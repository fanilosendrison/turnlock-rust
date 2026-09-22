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

Use this policy to operate the permanent bare repository, create isolated task
worktrees, publish task commits, and remove successfully published worktrees.

Treat [AGENTS.md](../../AGENTS.md) as the authority for repository execution
guardrails and this document as the detailed worktree procedure. Treat Git refs,
remote-tracking refs, and Git worktree metadata as authority for repository and
worktree state. Do not maintain a second inventory in documentation.

This policy affects repository governance only. It creates no TURNLOCK product
semantics, architecture commitment, formal-verification claim, or qualification
evidence.

## Permanent repository

Define:

```text
BARE_REPOSITORY =
the permanent local bare Git repository for turnlock-rust
```

The bare repository contains:

```text
objects
refs
origin remote configuration
worktree administration metadata
```

It contains no checked-out project files and is not itself a task workspace.

The normal permanent local branch set contains exactly:

```text
refs/heads/main
```

Do not rely on local `main` being as fresh as remote state. Fetch remote
publication authority as:

```text
refs/remotes/origin/main
```

## No permanent worktree roles

There is no operational role for a:

```text
primary worktree
dedicated main worktree
integration worktree
permanent detached worktree
```

A path name never creates a worktree role. Maintain zero permanent worktrees.

## Task creation

Before every task, run:

```bash
git --git-dir=<BARE_REPOSITORY> fetch origin
```

Record exactly:

```text
TASK_BASE = refs/remotes/origin/main
```

Create one unique detached task worktree:

```bash
git --git-dir=<BARE_REPOSITORY> worktree add \
  --detach \
  <UNIQUE_TASK_PATH> \
  refs/remotes/origin/main
```

Require:

```text
detached HEAD
HEAD == TASK_BASE
clean
operation-free
```

Operation-free means no active:

```text
MERGE_HEAD
CHERRY_PICK_HEAD
REVERT_HEAD
rebase-merge
rebase-apply
BISECT_LOG
sequencer
```

Do not create a task branch by default. Never check out `main` in a task
worktree.

## Task isolation

One task owns one worktree. Write only within the current task's worktree.

Never:

```text
edit another task worktree
switch another task worktree
clean another task worktree
stash another task worktree
reset another task worktree
remove another task worktree
require another task worktree to be clean
```

Treat other active worktrees as normal parallel activity. Their existence does
not block task creation or execution.

## Detached commits

Create task commits directly on detached `HEAD` when needed. The task worktree
retains the detached commit chain before publication.

Do not remove an unpublished task worktree merely because its `HEAD` is
detached.

## Validation

Create all task-specific validation environments and generated validation state
inside the task worktree. No permanent checked-out repository exists to
pollute.

Run every task-required validation from the current task worktree.

## Pre-publication synchronization

Immediately before publication, run:

```bash
git --git-dir=<BARE_REPOSITORY> fetch origin
```

Let:

```text
CURRENT_MAIN = refs/remotes/origin/main
```

If:

```text
CURRENT_MAIN == TASK_BASE
```

continue after final validation.

If:

```text
CURRENT_MAIN != TASK_BASE
```

re-evaluate the exact semantic, source, and blob guards specified by the task.

When automatic continuation is authorized, replay only the current task commit
range:

```text
TASK_BASE..HEAD
```

onto `CURRENT_MAIN`. Use detached-HEAD rebase or cherry-pick mechanics selected
by the task, but create no merge commit unless separate authority explicitly
requires one.

If a conflict, authority change, source-guard failure, or ambiguity appears:

```text
STOP
preserve the task worktree
```

After successful replay:

```text
TASK_BASE = CURRENT_MAIN
```

Then rerun complete task validation.

## Publication

Require:

```text
CURRENT_MAIN is ancestor of task HEAD
```

Publish only:

```bash
git push origin HEAD:refs/heads/main
```

Use an ordinary fast-forward push only.

Never:

```text
force
force-with-lease to rewrite main
delete main
push another task's commit
```

If another task advances `main` and the push is rejected:

```text
fetch again
re-evaluate guards
reconcile the current task when permitted
revalidate
retry an ordinary fast-forward push
```

## Post-publication proof

After successful push, run:

```bash
git --git-dir=<BARE_REPOSITORY> fetch origin
```

Require:

```text
task HEAD is ancestor-or-equal to
refs/remotes/origin/main
```

Remote `main` may already contain later concurrent commits. Equality is not
required.

## Local main branch

Retain:

```text
refs/heads/main
```

as the single ordinary permanent local branch in the bare repository.

Treat local `main` as convenience/local state, not publication authority. After
a successful fetch, fast-forward local `main` to current remote `main` only
when:

```text
local main is ancestor-or-equal to remote main
```

No worktree checks out `main`, so update it without requiring a worktree. Never
rewrite local `main` backwards or sideways.

A stale local `main` does not block task creation because every task starts from
fresh `refs/remotes/origin/main`.

## Successful worktree cleanup

After publication reachability is proven, require the current task's own
worktree to contain no:

```text
staged tracked changes
unstaged tracked changes
untracked non-ignored files
active Git operation
```

Delete task-generated ignored content only when it is disposable task
infrastructure.

Remove exactly the current task's worktree. Then run:

```bash
git --git-dir=<BARE_REPOSITORY> worktree prune
```

Verify that the worktree record disappeared. Do not inspect or modify another
task worktree as a cleanup prerequisite.

## Failed task preservation

If publication did not succeed, or task `HEAD` is not proven reachable from a
retained ref:

```text
DO NOT REMOVE THE WORKTREE
```

Report:

```text
task path
TASK_BASE
task HEAD
publication state
reason cleanup was refused
```

No other agent may delete it merely because it looks stale.

## Normal topology

When no tasks run:

```text
permanent bare repository
+
zero non-bare worktrees
```

When N tasks run:

```text
permanent bare repository
+
N temporary detached worktrees
```

After one successful task:

```text
N := N - 1
```

No worktree survives because of a permanent role.
