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

Use this policy to select worktrees, create temporary branches, and clean up
completed branch work without depending on machine-specific paths or directory
names.

Treat [AGENTS.md](../../AGENTS.md) as the authority for repository execution
guardrails and this document as the detailed worktree procedure. Treat Git refs
and Git worktree metadata as the authority for current branch and worktree
state. Do not maintain a second inventory in documentation.

This policy affects repository governance only. It creates no TURNLOCK product
semantics, architecture commitment, formal-verification claim, or qualification
evidence.

## Resolve worktree roles mechanically

Run the following command before creating, switching, removing, or repurposing a
branch or worktree:

```bash
git worktree list --porcelain
```

Resolve the roles from that output:

1. Treat the first worktree record as Git's primary worktree.
2. Treat the unique non-bare record whose `branch` value is exactly
   `refs/heads/main` as the dedicated main worktree.
3. Resolve paths from the records. Never infer a role from a path basename,
   sibling-directory convention, user-specific path, or remembered session
   state.

Fail closed and request operator action when:

- the primary worktree is absent, bare, locked, or prunable;
- no worktree or more than one worktree declares `refs/heads/main`;
- the dedicated main worktree is bare, locked, or prunable;
- the primary and dedicated main roles resolve to the same worktree before
  temporary branch work;
- any worktree record is malformed or its role cannot be determined uniquely.

Do not resolve duplicate or ambiguous roles by declaration order, path sorting,
or agent preference.

## Preserve role separation

Reserve the dedicated main worktree for:

- synchronizing and inspecting `main`;
- clean-main validation;
- integration verification;
- publication preparation and post-publication verification.

Never create or check out a temporary development branch in the dedicated main
worktree.

Use the primary worktree as the default workspace for temporary development
branches when its safety gates pass. Create an additional linked worktree only
when the task requires isolation or concurrent work and the operation is
explicitly authorized. Do not allow an additional worktree to replace the
stable main role.

## Apply the worktree safety gates

Before switching, repurposing, synchronizing, or removing a worktree, require
this command to exit successfully and produce no output:

```bash
git -C <worktree-path> status --porcelain=v2 --untracked-files=all
```

Treat staged, unstaged, and untracked content as dirty state. Do not rely on
color, human-oriented status formatting, or configuration-dependent aliases.

Ignored content is outside this ordinary cleanliness result. Before removing a
worktree, inspect it explicitly with:

```bash
git -C <worktree-path> status \
  --porcelain=v2 \
  --untracked-files=all \
  --ignored=matching
```

Preserve ignored content that must survive. Remove a worktree containing ignored
content only after the operator explicitly authorizes discarding or separately
preserving the reported paths.

Resolve operation-state paths with:

```bash
git -C <worktree-path> rev-parse --git-path <state-name>
```

Require all of the following operation states to be absent before proceeding:

- `MERGE_HEAD`;
- `CHERRY_PICK_HEAD`;
- `REVERT_HEAD`;
- `rebase-merge`;
- `rebase-apply`;
- `BISECT_LOG`;
- `sequencer`.

Stop when Git reports another active operation or an unexpected administrative
state, even when the worktree status is otherwise clean.

Before switching the primary worktree away from its current branch or detached
commit, record the current ref and commit identity. Preserve a branch or another
reachable ref for every commit that must survive the switch.

## Synchronize main safely

Apply the cleanliness and operation-state gates to the dedicated main worktree.
Re-read the remote `main` ref before relying on local integration state. Update
the local remote-tracking ref through an authorized fetch mechanism, then
advance local `main` through the dedicated main worktree and only by
fast-forward unless separate repository authority explicitly permits another
operation.

After advancing `main`, verify the dedicated worktree's `HEAD`, index, files,
and status against the intended main commit. Do not update the branch ref behind
that worktree through an external ref mutation.

Do not treat a stale local `main`, stale remote-tracking ref, or remembered SHA
as current remote state. Do not rewrite `main` to simplify worktree cleanup.

## Remove temporary worktrees and branches

Never remove the primary worktree or the dedicated main worktree as part of
routine cleanup.

For every temporary worktree:

1. Reapply the cleanliness, ignored-content, and operation-state gates.
2. Record its current branch, if any, and exact `HEAD` commit.
3. For a detached `HEAD`, prove that the commit is reachable from a retained
   ref, create an explicitly authorized durable ref, or obtain explicit operator
   authorization to discard the exact reported uncontained commit.
4. Remove only the worktree. Preserve any branch ref until branch deletion is
   independently authorized and verified.
5. Re-run `git worktree list --porcelain` and confirm that both persistent roles
   remain valid.

Before deleting a temporary branch, prove that its exact tip is reachable from
the exact current `main` commit. Use Git ancestry when both exact objects are
available locally, or use the authoritative remote comparison API when local
refs are stale. Do not infer integration from equal file content, branch names,
Pull Request state, or a previous comparison.

If reachability cannot be proved, preserve the branch. Delete an uncontained
branch only after the operator receives the exact uncontained commit identity
and explicitly authorizes that destructive outcome.

After reachability proof, delete a local ref only with an atomic expected-old
object identity and only after confirming that no worktree checks it out. Delete
a remote ref only through a mechanism that atomically conditions deletion on
its expected old object identity. Stop and request operator action when the
available remote API cannot provide that condition; an immediate re-read alone
does not close the race.

## Verify the resulting topology

After every worktree or branch lifecycle operation:

1. Run `git worktree list --porcelain` again.
2. Enumerate local branches and their upstreams.
3. Read remote branch refs from the remote authority.
4. Confirm that the primary and dedicated main worktrees remain distinct,
   present, unlocked, and non-prunable.
5. Confirm that every retained worktree passes the cleanliness and
   operation-state gates.

Report the observed state from Git. Do not copy the current paths, branch list,
or commit identities into maintained repository documentation.
