# Disclosure review — 19 October 2026

## Result and scope

No confirmed credentials, private platform material, internal server paths or customer records were identified in the reviewed publication content. This is a bounded disclosure review, not a guarantee that every sensitive fact can be detected or a legal/security certification.

Reviewed baseline: `c94e96b55be9abf3613bcb11cd794dd64a2f87ea`. The review covered:

- All 16 commits and 188 distinct file blobs reachable through the advertised branch and pull-request references, including deleted/older file versions, commit messages, identities and historical paths. No tags, Git LFS pointers or submodules were present.
- All 18 existing Actions runs, their 18 downloadable log archives, job/check metadata and annotations. Every run had one attempt. Earlier failures remain part of the record.
- Both merged pull requests, their descriptions, reviews and comments, and repository metadata. No separate issues, wiki, discussions, release assets, deployments or uploaded attachments were present in the inspected surfaces.
- The compiled browser preview, source/report fixtures and documentation. The preview remains a local mock-up; the Python tool and its evidence contracts are authoritative.

Gitleaks 8.30.1, obtained from its official release and verified against the release checksum, reported no secret findings in the Git history or the retained publication payloads. A separate content/path scan and contextual review checked private project/host identifiers, local paths, network addresses, credential markers and contact details. Example rejection URLs, ignore-file patterns and third-party attribution were inspected as context, not automatically treated as leaks. Authentication-only response fields from the administrative API are excluded from retained inventories and are not repository content.

## Cleanup and evidence preservation

Two redundant branches were deleted only after verifying that their exact tips were ancestors of `main` and their pull requests had been merged. Remote deletion used the expected tip as a concurrency guard.

| Removed branch | Preserved tip, reachable from `main` |
| --- | --- |
| `feat/standalone-showcase` | `a5dfddc116bc7d6f84c3b3fb6e4abae803f086da` |
| `fix/publication-status-20261019` | `073592d78fbe90f4d7decf0da55108abcb751e76` |

No commit was rewritten, squashed or removed. No workflow run or log was deleted for presentation purposes. There were **zero Actions artifacts and zero release assets** to delete. Historical review and license records retain their original dates and scope; current terms are in [LICENSE.md](../LICENSE.md) and [project status](PROJECT_STATUS.md).

A verified Git bundle of all captured references, log archives, metadata inventories, SHA-256 manifests and cleanup records are retained privately by the owner, outside this repository. Their presence is a preservation measure, not independent attestation or a public archive service. The pre-cleanup bundle SHA-256 is `29effe4ea4d0f68b87094497f0a906d5602efaa968896ca56db881a5c85d768e`. Raw audit inventories and logs are deliberately not copied into the showcase.

The following referenced historical checks and the successful baseline check remain available on GitHub and were archived for the review:

- [Run 38695576295](https://github.com/dr-opoku/resqmonitor/actions/runs/38695576295).
- [Run 38711055134](https://github.com/dr-opoku/resqmonitor/actions/runs/38711055134).
- [Run 39323580238](https://github.com/dr-opoku/resqmonitor/actions/runs/39323580238).

The final link above checks the baseline identified here. Later documentation commits have their own Actions results; do not treat a historical green run as verification of an arbitrary future revision.

## Contacts and publication boundary

Author identities and professional contact details remain in Git history, the license and the owner-supplied legal pages; third-party author contacts remain in attribution notices. A public repository exposes those records as well as old branches' merged commits and pull-request history. Removing a branch does not conceal its commits. Private audit backups must not be attached to a release or copied into the site.

The repository remains private. This preparation does not change visibility, grant new use rights, publish a package or deploy the preview. Public source availability does not mean open-source licensing: the [Noncommercial Local Use License 1.1.0](../LICENSE.md) and separately identified third-party terms remain unchanged.

Before changing repository visibility, confirm the intended public contact details and inspect the newest `main` Actions result. A separate website deployment still requires reconciliation of the supplied legal/privacy pages with its actual operator and host, correct origin/base-path handling, complete frontend dependency provenance and browser verification. Those hosting limits do not imply that the Python reference ran through the frontend.

This review covers accessible repository records at the stated baseline. It cannot inspect records already deleted or inaccessible before capture, GitHub internal retention/caches, future changes or material never committed or uploaded. Hashes and archived logs establish consistency of retained bytes; they do not authenticate every claim or reconstruct the historical model execution.
