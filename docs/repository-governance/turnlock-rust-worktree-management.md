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

Use this policy to preserve the user-owned repository checkout, create isolated
agent task worktrees, publish task commits, and remove successfully published
task worktrees.

Treat [AGENTS.md](../../AGENTS.md) as the authority for repository execution
guardrails and this document as the detailed worktree procedure. Treat Git refs,
remote-tracking refs, and Git worktree metadata as authority for repository and
worktree state. Do not maintain a second inventory in documentation.

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
TASK_WORKTREE =
one temporary detached linked worktree created from freshly fetched origin/main
```

`PERSISTENT_CHECKOUT` is not a task workspace. It contains the user's normal
checked-out project files and may normally remain on:

```text
refs/heads/main
```

There is no operational role for a:

```text
dedicated main worktree
primary development worktree
permanent detached worktree
permanent integration worktree
```

A path name never creates such a role. No permanent agent worktree exists.

## Persistent-checkout boundary

Treat the persistent checkout as user-owned state. Never use it for:

```text
task edits
task commits
temporary implementation files
validation virtual environments
generated task artifacts
rebases
merges
publication preparation
```

Do not modify or clean the persistent checkout to prepare an agent task.

Tracked edits, untracked files, and ignored files in the persistent checkout do
not block task creation or task execution. Never stash, clean, reset, restore,
checkout, switch, merge, rebase, or commit the persistent checkout merely to
prepare a task.

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
  <UNIQUE_TASK_WORKTREE> \
  origin/main
```

Place the task path outside the persistent checkout. The recommended parent is:

```text
/Users/neelo/Developper/Projects/.turnlock-rust-worktrees/
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

Do not require a temporary task branch.

## Task isolation

One task owns one worktree. Perform every task edit, commit, validation,
validation-environment creation, generated-task-artifact creation,
reconciliation, and publication-preparation operation inside that task worktree.

Multiple task worktrees may coexist concurrently. Their existence and state do
not block another task.

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

Only publication to `refs/heads/main` is serialized.

## Detached commits

Create task commits directly on detached `HEAD`. The task worktree retains the
detached commit chain before publication.

Do not remove an unpublished task worktree merely because its `HEAD` is
detached.

## Validation

Create all task-specific validation environments and generated validation state
inside the task worktree. Run every task-required validation there.

Do not create task validation state in the persistent checkout.

## Pre-publication synchronization

Immediately before publication, fetch again:

```bash
git -C <PERSISTENT_CHECKOUT> fetch origin
```

Let:

```text
CURRENT_MAIN = origin/main
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

When automatic continuation is authorized, replay only:

```text
TASK_BASE..HEAD
```

onto current `origin/main`. Create no merge commit unless separate authority
explicitly requires one.

If a conflict, authority change, source-guard failure, or ambiguity appears:

```text
STOP
preserve the task worktree
```

After successful replay, set:

```text
TASK_BASE = CURRENT_MAIN
```

Then rerun complete task validation.

## Publication

Require current `origin/main` to be an ancestor of task `HEAD`.

Publish only:

```bash
git push origin HEAD:refs/heads/main
```

Use an ordinary fast-forward push only. Never force-push `main`, use
force-with-lease to rewrite `main`, delete `main`, or push another task's
commit.

If another task advances `main` and publication is rejected:

```text
fetch again
re-evaluate task guards
reconcile the current task when permitted
rerun complete validation
retry an ordinary fast-forward push
```

## Post-publication proof

After successful publication, fetch `origin/main` again and require:

```text
task HEAD is ancestor-or-equal to current origin/main
```

Remote `main` may already contain later concurrent commits. Equality is not
required.

## Successful task-worktree cleanup

After publication reachability is proven, require the current task worktree to
contain no:

```text
tracked modifications
untracked non-ignored files
active Git operation
```

Task-generated ignored content may be deleted as disposable task
infrastructure.

Remove exactly that temporary task worktree. Then run:

```bash
git -C <PERSISTENT_CHECKOUT> worktree prune
```

Verify that its worktree record disappeared. Never remove the persistent
checkout.

## Failed-task preservation

If publication fails or task `HEAD` is not proven retained:

```text
DO NOT REMOVE THE TASK WORKTREE
```

Report:

```text
path
TASK_BASE
HEAD
reason
```

Never discard it automatically. No other agent may remove it merely because it
looks stale.

## Persistent-checkout synchronization

Do not require the persistent checkout to advance after every agent
publication.

Synchronize it only when it is completely clean and operation-free, using:

```bash
git -C <PERSISTENT_CHECKOUT> fetch origin
git -C <PERSISTENT_CHECKOUT> merge --ff-only origin/main
```

If user state is present, do not modify it and report that local `main` remains
behind until the user chooses to synchronize.

## Normal topology

When no task is active:

```text
turnlock-rust/
    normal non-bare repository
    main checked out

no temporary task worktrees
```

During N parallel tasks:

```text
turnlock-rust/
    normal user checkout

.turnlock-rust-worktrees/
    task-1/
    task-2/
    ...
    task-N/
```

After all successful task worktrees are removed:

```text
turnlock-rust/
```

remains as the permanent user checkout.
