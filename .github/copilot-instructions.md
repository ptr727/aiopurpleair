# Copilot Instructions

Repository-wide instructions for GitHub Copilot.

Read [AGENTS.md](../AGENTS.md) first. It routes every standing repository rule to its canonical
document. When performing code review, load and follow the `code-review` skill in
`.github/skills/code-review/SKILL.md`, then load every language, documentation, or workflow skill
that it selects for the changed files. GitHub Copilot reads these files from the pull request's
head branch, so review the instructions in that tree.

Do not duplicate rules from `AGENTS.md`, `GOVERNANCE.md`, `CODESTYLE.md`, or `WORKFLOW.md` here.
This file contains only Copilot-specific bootstrap and output requirements.

## Commit Messages and Pull Request Titles

Use an imperative subject of at most 72 characters with no trailing period. Use US English and
title case with lowercase short bind words. Do not add `Co-Authored-By:` unless requested. Do not
put a release-bump magnitude in the title. The full contract is in
[GOVERNANCE.md "Pull Request Title and Commit Message Conventions"](../GOVERNANCE.md#pull-request-title-and-commit-message-conventions).

## Reviewing Carried Fleet Content

Follow the fidelity declared for the file. A byte-locked reference to shared infrastructure that
this repository does not carry is intentional, not a broken link. Raise substantive defects in
canonical content, but locate the fix at its canonical source instead of proposing a local edit.

`.github/skills/` is generated from a shared source by a generator this repository does not carry,
so a defect in a skill is fixed in that source or in the generator and never in the copy. A defect
inside an include region, the text between the marker lines `<!-- include: <path> > <heading> -->`
and `<!-- /include -->` that every copy carries as its authored source does, is fixed at the
canonical heading that key names, since the region is generated from that heading's body and the
key's path resolves against the generating repository's root rather than this repository's copy of
the same file. Where that heading's body is itself a region, the fix sits one hop further, under
the heading its own key names. Post no review comment on a file under `.github/skills/`. When the
pull request changes the file the fix belongs in, comment on that file instead, and otherwise
state the finding in the review summary.

## GitHub Copilot Review Runbook

For every review:

1. Read the full pull request diff and count its changed files.
2. Follow `.github/skills/code-review/SKILL.md` and every skill it selects.
3. Publish every supported finding. Never suppress a finding or place it in a low-confidence or
   hidden findings block.
4. Use an inline comment when a changed line can anchor the finding. Use the review body only when
   no valid inline anchor exists.
5. End the review body with the exact machine-readable marker required by the `code-review` skill.

The review automation is `scripts/pr_review.py`. It is hub-hosted rather than carried here, so run
it from a checkout of the hub, the repository [AGENTS.md](../AGENTS.md) "Fleet Bootstrap" names,
passing `--repo ptr727/aiopurpleair`. [GOVERNANCE.md "Hub-Hosted Tooling"](../GOVERNANCE.md#hub-hosted-tooling)
states why a tool is reached rather than copied, and how to reach one.
Use its `status`, `wait`, `comment`, and `reply --resolve` commands instead of reconstructing
GraphQL queries or copying review identifiers by hand. Use `comment` for a suppressed-finding
answer in the pull request conversation. Its status gate verifies the current head, diff coverage,
output shape, inline threads, body-only findings, and required checks.

A formal review with no findings is complete only when it covers the current head and states full
diff coverage. A refusal, partial or absent coverage statement, unrecognized output shape,
unresolved thread, or body-only finding blocks the review loop. Re-run the loop after every fix
push. Never infer review completion from `mergeStateStatus: CLEAN`.

Review effort is user-controlled. The automation observes `Lite`, `Balanced`, or `Max`, including an inherited `Default (<level>)`, and never selects or changes the setting. Effort does not determine coverage or completion. A request can complete without a `copilot_work_started` event, so absence of that event is not a stalled-review verdict. When `wait` returns `PENDING` with `requested=yes`, report the state and rerun `wait` for another bounded interval by default. Do not clear the request automatically because it may be active. If the maintainer directs a retry, remove Copilot in the pull request UI, add it again, and rerun `wait`. This recovery replaces only the review request and never changes the effort setting.

**Editing a pull request description or title: use the REST API, not `gh pr edit`.** `gh pr edit --body`
or `--title` issues a GraphQL mutation that touches the deprecated Projects (classic) `projectCards`
field and fails before applying the change, and it fails silently, so the edit never lands while the
command reports success. A stale description is a real and recurring review finding, so verify the
edit took. Update through REST instead:

```sh
gh api -X PATCH repos/ptr727/aiopurpleair/pulls/<N> -F body=@body.md
gh api -X PATCH repos/ptr727/aiopurpleair/pulls/<N> -f title='...'
```

### Disproved Claims

**A disproof is proof about this repository, and the thread it was written in is not where the next round looks.** [GOVERNANCE.md "PR Review Etiquette"](../GOVERNANCE.md#pr-review-etiquette), which routes to the `pr-review-conduct` Skill, closes a false finding by disproving it in the thread, addressed to the reviewer so it does not raise the same thing again, and while the pull request is open that is the right place for it. Afterwards it is the wrong one. The pull request merges, the next round begins with no memory of the last, and the second occurrence reaches a maintainer with no way to tell it from a first. Each entry below is a claim that was tested against this repository and found false, kept so the proof is read rather than built twice.

**An entry names the claim, what was run or read to disprove it, the revision it was proved against, and what ends it.** A disproof is true of one tree at one revision, so an entry whose subject moves is deleted by the change that moves it rather than edited to look current, which is the same sweep the [GOVERNANCE.md "Documentation Style Conventions"](../GOVERNANCE.md#documentation-style-conventions) rule already requires of prose asserting a behavior that has changed underneath it. This is deliberately not a list to append to, since an entry outliving the code it was proved against becomes a reason not to check, and that is strictly worse than proving the claim a second time.

**The record answers a repeated claim and never dismisses a new one.** An entry is cited only where the revision it names is still what the tree carries, and the reply carries the proof re-read rather than a pointer to the entry, since a reviewer that cannot open this file learns nothing from being pointed at it. Judge a finding on its merits first and match it against this record second, because reading it the other way round is how a real finding gets closed by a stale proof.

**The entries are this repository's own.** Each names a file and a revision, so this repository records what it has proved for itself rather than carrying a proof about a tree it does not hold.

**This repository has recorded no entry yet.** The rules above are carried and the ledger is empty rather than absent, so the first disproof this repository earns is written here in the shape they describe, instead of being rebuilt in a later round.

## When in Doubt

Stop and report the uncertainty. Do not guess at an instruction, suppress a possible finding, or
claim coverage that the review did not perform. Where a rule looks wrong, missing, or out of date
rather than merely inconvenient, report that as the finding instead of working around it, so the
discrepancy reaches whoever maintains the rule rather than being absorbed silently here.
