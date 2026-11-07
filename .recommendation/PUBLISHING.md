# Recoverable publication protocol v1

This execution protocol applies to music, English, news/YouTube/Reddit, and Journal. It does not change candidate counts, source verification, permanent deduplication, editorial requirements or storefront rules in policy.json. Repository structure checks are NOT live-source QA.

## Journal support (2026-11-04)

Journal now uses the same publication and recovery tools. For new dates use `project: journal`, `operation_id: journal:YYYY-MM-DD`, `schema_version: 1` in the plan and standard bundle envelope, and `owner/repo:path` payload keys. `targets_for('journal', day)` supplies the daily note, Index.md and append-only journal.jsonl, all in stage 1. Exposures are ordered lowercase `doi:10.…` IDs. Keep source observations and subsequent QA in separate run receipts.

The original November 2–4 `journal-frozen-v1` records are supported by a strict adapter. It verifies their original plan and envelope digests, exact target hashes, evidence identities and payloads without rewriting any original bytes. Never migrate or replace those PREPARED files. Preserve their original digests during retries. The November 4 format-only corrections to their published notes are recorded separately under transaction-corrections; never replay an old payload over corrected text or user Notes.

`python3 scripts/validate_journal.py --base-ref FULL_ANCESTOR_SHA` checks all Journal notes, index coverage, DOI/title/version identities and byte-prefix preservation. The global integrity workflow also runs these checks. A normal issue contains 2–4 papers; one paper requires a substantive `## 数量说明` explaining the quality shortfall. If no paper qualifies, record the reason in run evidence rather than manufacturing a successful issue. These checks do not certify scientific correctness, source access or full-paper reading.

For reliable Markdown rendering, write list labels as `- **问题与观测：** DrBphP …`: exactly one ordinary space after the closing `**`, including before Chinese text. Do not use `- **问题与观测：**DrBphP …`. Keep blank lines around paragraphs and lists. Inspect rendered output for visible Markdown markers before reporting completion. The new-note and current-note checks reject this label-spacing defect; immutable historical bundles retain their original content.

## One date, one frozen publication

Use Asia/Shanghai for the business date. The operation is `music:YYYY-MM-DD`, `english:YYYY-MM-DD`, `news-youtube-reddit:YYYY-MM-DD`, or `journal:YYYY-MM-DD`. Before selection, read policy, permanent history, current dated files, and ALL records under `.recommendation/transactions/`. Resources reserved in any earlier PREPARED bundle are also permanently excluded, even when that operation never completed. Never remove a reservation or exposure to improve QA statistics.

If today's bundle exists, repair it; do not select new resources. If dated content exists without a bundle, adopt that existing selection in a clearly labelled `mode: adopt_existing` bundle. This is not evidence of the original candidate pool or pre-publication checks. Recover the union of known exposures first. Never change another day's original plan or rewrite a failed selection into a new success.

For a NEW date, complete current-date source/identity/semantic checks and build all final payloads before publishing or showing the selection. Persist the actual candidate IDs/URLs, actual verification observations and timestamps in the run evidence; do not invent candidate counts, semantics or accessibility evidence. Historic source failures and pre-policy formatting/repeat findings remain recorded as backlog, not a reason to delete history or indefinitely block unrelated future dates. Missing history, changed permanent data or inconsistent music mirrors DO block publication.

## Durable PREPARED bundle

Use `scripts/publication_bundle.py` and `scripts/publication_recovery.py`. The immutable record is `.recommendation/transactions/PROJECT/YYYY-MM-DD.json`. It contains `schema_version`, `plan`, `payloads`, `plan_sha256`, `bundle_sha256`. `payloads` maps `owner/repo:path` to the COMPLETE UTF-8 target text, not just a hash. This makes a retry recoverable after the original execution loses its working memory.

The plan is version 1 with project, date, operation_id, ordered exposed_resource_ids and targets. Every target includes repository, path, explicit base_sha (null only for confirmed absence), target_sha (Git blob SHA), and stage. Hash bytes with `publication_recovery.blob_sha`; never guess hashes. `publication_bundle.targets_for(project, day)` defines the exact files and stage numbers. English uses three weekday notes plus history, or one Saturday/Sunday note plus history. Discovery uses three notes plus two histories. Music uses manifest+state in music-daily (stage 1), then mirrored manifest+state+note in the vault (stage 2). QA is a later receipt, not part of a circular self-certifying payload.

Create the bundle locally with `publication_bundle.freeze(plan, payloads)`. Call `check_baselines(bundle, verified_original_texts)` before writing; null is allowed only after repository/branch accessibility and file absence are established. Do not pass API errors as empty files. Preserve old JSONL bytes and all music state values. An existing unmarked Markdown note can only be left byte-identical automatically. In marked notes only the AUTO block can change; frontmatter and all text outside it remain unchanged. Escalate unmarked note edits for review rather than overriding this guard.

Create the PREPARED file exactly once using the connector; read it back and verify its blob SHA, both digests and exact payloads before touching publications. Save its creation commit and original bundle digest in a separate execution receipt. If it already exists, retrieve its original creation version and digest from Git history. A retry must not recompute a new baseline or digest and then overwrite the original record.

## Apply only missing stages

Obtain fresh observations for every target: verified `ok` plus SHA, or `missing` with confirmed=true. Failed/partial reads remain `error`/unverified. Run:

```bash
python3 scripts/publication_bundle.py persisted-bundle.json \
  --observations fresh-observations.json --expected-bundle-digest ORIGINAL_PREPARED_DIGEST
```

`blocked` means no mutation. `artifacts_match` means no-op; it is NOT content QA. `ready_to_resume` permits ONLY the earliest next_stage. Use the exact frozen payloads. Prefer one ordinary Git commit per repository/stage: read the current commit and actual tree SHA; create_tree(base_tree_sha=tree SHA) with the planned files; create_commit(parent=current head); re-read head; update_ref(force=false). A commit SHA is NOT a base tree SHA. If unrelated files changed, rebase only after proving every target still equals its frozen baseline/target. Never force update. A divergent target is a conflict requiring review, not permission to overwrite manual content.

If Git-data writes are unavailable, serial Contents API updates may be used with fresh matching blob SHAs and the same persisted bundle. A confirmed matching target is no-op. Read back after each mutation; a transport failure may have happened after a successful commit. Missing or uncertain responses never justify a fresh recommendation. After each stage record real commit and observed target hashes in `.recommendation/transaction-runs/PROJECT/DATE/ATTEMPT.json` (unique timestamp/attempt). Never rewrite PREPARED. A crash before recording a stage is recovered from current target hashes, not guessed from the last response.

403: distinguish permission denial from limit/abuse signals when exposed. 409: reread/reconcile. 422: inspect payload/schema/ref; do not repeat unchanged. 429/5xx/transport: obey retry metadata and reread before a bounded retry. Do not create replacement tasks, clear state, change security settings, or permanently disable tasks to hide a transient failure. Stop this attempt, record real failure, and let the next scheduled attempt perform the same preflight. Platform-level automatic pauses cannot be controlled by this protocol.

## Verify before success

Read back all artifacts and history. Verify fresh selections against the ORIGINAL pre-selection history, not the history just updated by this operation. On adoption/repair, an ID reserved by this SAME operation is expected; an ID used by an earlier unrelated operation is still forbidden. Run repository validators and bundle/journal checks in an authorized code environment. Inspect CI for the exact tested code/data version; never substitute an unrelated green run.

For music also run the cross-repository snapshot check below or the existing two-checkout consistency checker. Require exactly five matching ordered CN song IDs, album/version metadata, complete appreciation, state union coverage and byte-equal manifests/states. After ALL applicable CURRENT-publication checks pass, create/update `.recommendation/runs/DATE-PROJECT.json` with source observations, actual candidate counts, rejection results, structural/history results, bundle digest, commit/readback evidence and cross-repo status. Read the receipt back. Never label `content_qa=not_evaluated` as full success, or claim device sync/notifications were tested by GitHub checks.

## Credential-free cross-private-repository health check

Use the existing authorized GitHub connector, not a borrowed/extracted token. For BOTH default branches: read head_before; fetch that commit to obtain the real root tree SHA; fetch complete NON-recursive trees by their SHA. Follow only paths needed for music-daily `recommendations/` and `state/tracks.json`, and vault `Music/Daily/manifests/`, `Music/Daily/state/tracks.json`, and dated music notes. Store the raw tree objects under trees[tree_sha]. Then re-read head_after. If either head changed, collect a fresh snapshot once; persistent movement or incomplete responses is UNVERIFIED, never passed.

Snapshot JSON: schema_version=1, music and vault each contain head_before, head_after, commit (sha and tree.sha), and trees (SHA to raw nonrecursive API tree object). Run `python3 scripts/check_remote_music_snapshot.py snapshot.json`. It recomputes Git tree hashes so omitted/truncated entries cannot silently certify completeness. It compares ALL manifest dates/hashes, state hashes, and corresponding note existence. Full source/semantic history coverage still comes from the per-repository CI; HTTP accessibility and notifications are NOT proven by hash equality.

The daily health task is read-only: inspect pinned matching CI/workflow contents, transaction completion evidence and overdue attempts; notify on mismatch, incomplete/unknown checks or source-publication failures. Do not write history, generate recommendations, change policies or toggle other tasks. The GitHub repo-local CI remains separate and does not gain cross-private-repository privileges.

## Permanent music identity gate (2026-11-06 repair)

The incident registry `.recommendation/incidents/music-2026-11-06-714861225.json`
recognizes exactly the two original occurrences of `apple_music:cn:714861225`,
their original manifest bytes, the immutable bundle, and the failure receipt.
It is not permission to reuse that recording. November 6 remains failed and must
not receive a success QA receipt. The original selection and note remain in Git
and the unchanged PREPARED payloads; state values and PREPARED bytes are retained. Any evidence change, scope expansion or third reuse
is rejected. A subsequent unrelated day is not rejected merely because this
registered incident exists.

`scripts/music_identity.py` derives recording identity from provider, storefront
and numeric song ID, with canonical keys as an additional exclusion. It reads all
current manifests, dated notes, all HEAD-ancestor versions (including replaced or
deleted selections), and all immutable PREPARED payloads. Repeated snapshots are
provenance for one occurrence. A retired song remains excluded even if its date
was republished with different songs. Missing/deleted PREPARED files remain
reservations in Git history; rewritten PREPARED files block the gate. Shallow
clones and Git replacement refs are rejected. The index is derived, never a
replacement for permanent state. Its scope is available local Git ancestry, not
an assertion that unavailable external history was inspected.

Original missing IDs stay missing in the index. A separate
`legacy_identity_associations` entry may say
`resolved_by_recorded_later_evidence` only when direct-link records have the exact
same operation/date, position and canonical key, and their source blobs occur in
Git commits descending from a commit containing the original missing-ID blob.
Both commits and blobs are retained as evidence. All identities ever recorded
in that lineage remain excluded, including retired versions and numeric Apple
song IDs previously exposed in another storefront. Worktree-only candidates,
prior versions, different dates/positions/canonical keys do not close a gap.
This is a recorded lineage association, not a claim that the original search
link contained a particular recording ID. An original row without such evidence
still blocks the gate.

The five original 2026-09-04 search-link rows have these recorded associations;
the derived index retains all five original rows without inventing IDs. Six
other retired state keys are recovered from original Git versions of the
September 11 and September 26 notes. Current available history has no unresolved
lineage or unmapped permanent-state key. This does not certify unavailable
external history or replace actual source/content QA.

For a new music freeze call:

```python
freeze(plan, payloads, music_root=full_vault_checkout,
       mirror_snapshot=authorized_raw_tree_snapshot,
       expected_heads={"music": exact_music_commit, "vault": exact_vault_commit})
```

The snapshot uses the existing credential-free tree evidence format above. The
local Vault HEAD and all current manifest/state bytes must match those exact
versions. Candidate state must retain all baseline values. Missing evidence is
blocked. No extra credentials, permissions or cross-repository token are used.
For retries, `publication_bundle.py --observations ...` additionally requires
`--music-root`, `--mirror-snapshot`, `--music-head`, and `--vault-head`. It binds the
operation, original bundle digest, entire plan and exact payloads before allowing
same-operation reservations. The dedicated `music_identity.recovery_gate(...)`
checks every observation against complete hash-verified trees at the specified
heads. Each current target must be its frozen baseline or target. Untouched
manifest dates must still match across repositories, and original mirror
baselines must agree. Missing files require verified absence in complete parent
trees. Local Vault target bytes must also match the pinned evidence.

A stage 1 commit followed by a crash can therefore resume stage 2 even while
mirrors differ at the frozen operation's paths. Partial Contents writes can
finish only the earliest incomplete stage; already matching targets are no-ops,
including lost responses. A changed later-stage target while an earlier stage is
incomplete is rejected. Any third-party target change or unrelated mirror
difference is rejected. The result has `status=passed_music_recovery_gate`,
`planner.next_stage`, and `allowed_writes` containing only that stage's remaining
targets. Its transition status is
`mirror_status=verified_frozen_transition_not_final_mirror_qa`, never a full
mirror-success claim. Once all targets match, the normal full mirror audit must
also pass. The separate `publication_gate` used before freeze and for final
publication checks still requires fully matching mirrors; the recovery result
cannot authorize Apple Music writes or substitute for content QA.

The in-process `music_identity.publication_gate(...)` returns schema version 1,
`status=passed_music_publication_gate`, operation, ordered identities,
`identity_index_sha256`, `plan_sha256`, `payloads_sha256`, both exact heads,
manifest blob map, state blob hash, and historical failed dates. It explicitly
returns `content_qa=not_evaluated` and `transport=not_evaluated`. Consumers must
recompute this gate from authorized inputs; copying its JSON is not a trusted
attestation and does not certify source quality or Apple Music writes.

The existing success QA receipt has `schema_version=1`, `project=music`, matching
`date`/`operation_id`, `status=passed_current_publication`, and nested
`bundle.bundle_sha256` / `bundle.plan_sha256`, plus actual source observations,
readbacks and `checks.mirror_check`. A downstream write gate must verify the
receipt from its pinned Vault revision, bind it to the exact original bundle and
matching mirror version, and check actual content/source QA independently.
`planner.status=artifacts_match` and `planner.content_qa=not_evaluated` alone are
never sufficient. This repair does not generate success receipts or wire a new
credential bridge into the external publisher.

`python3 scripts/check_daily_integrity.py --base-ref FULL_SHA` now independently
reports structural/history integrity, immutable bundle integrity and the full
music identity index. `check_publication_health.py` exposes the same aggregate.
Every component runs even if another fails; exit 1 means at least one component
failed or identity evidence is incomplete. Registered failed days are explicit
in `checks.integrity.historical_failed_publications`. Neither a passing local
check nor a matching mirror relabels them as content-QA success.


## Exact music duplicate withdrawal (user-authorized 2026-11-07)

The user authorized removing only the later November 6 occurrence of Apple Music
CN song `714861225` from the current recommendation. The November 6 manifest and
note now retain original positions 1, 2, 4, 5, in that order, without reselection
or renumbering. The four retained track objects and song sections remain exact;
the overview and listening instructions remove the withdrawn recommendation.
All text outside the note's AUTO block, including user Notes, is preserved.

`.recommendation/transaction-corrections/music/2026-11-06/withdraw-714861225.json`
binds the exact removed occurrence, first occurrence, original manifest/note,
corrected manifest/note, original PREPARED blob/digest and failure evidence.
`scripts/music_withdrawal.py` deterministically reconstructs the only permitted
correction from those original frozen bytes. All required fields must match;
the current manifest and AUTO content must match the derived correction. This
is the sole four-track/positions-[1,2,4,5] exception. It cannot authorize another
removal, replacement, changed retained track or a short playlist on another date.
Later manual text outside AUTO remains user-owned.

The original five-track PREPARED still verifies unchanged, but its publication
recovery is explicitly blocked after withdrawal so it cannot reintroduce the
removed occurrence. No success QA receipt is created for November 6. The failure
and every permanent state value remain intact, and the full Git/PREPARED index
continues to exclude the withdrawn recording. Corrected current mirrors must
match exactly across repositories before future music publication; normal new
dates still require five unique tracks and the existing source/content checks.

This correction changes no Journal/English/news/resource files, frozen bundles,
source rules, identities, recovery plans, task settings or workflows. Journal's
November 7 frozen issue can be inspected with its existing tools and fresh
baselines; this music correction does not itself publish it or authorize any
new non-music work.
