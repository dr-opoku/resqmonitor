# Interface preview — resqmonitor

This mock-up shows what a browser interface for the tools could look like.
It is not yet connected to the Python tools and does not run their calculations.
To use resqmonitor, run the Python code from this repository. File import, preliminary
validation, configuration editing and export are browser-side helpers.

## Start the preview locally

From this repository's root directory:

```bash
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs/interface/site
```

Open **http://127.0.0.1:8000/resqmonitor/**. The overview is at
http://127.0.0.1:8000/. Stop the server with Ctrl+C.

Serve only `docs/interface/site`, not the whole repository: your own data,
outputs and working files should not become web-accessible. The server binds
to loopback. Opening the HTML directly with `file://` is not supported.

The package contains all three independent showcases and shared navigation,
assets and legal pages. Each repository retains the complete supplied site so
links between the three previews work without an external deployment.
The other tools' code is in their respective repositories, not in this site.

## Run the actual tool

The existing [repository quick start](../../README.md) is authoritative. For an
offline synthetic report, from this repository's root directory:

```bash
python3 -m resqmonitor demo --format json --output outputs/interface-report.json
```

Import `outputs/interface-report.json` in the corresponding preview's report
section. This is a manual file handoff, not a backend connection. Browser form
values do not execute or change a Python run. Use the documented Python CLI
and data contract for definitive input validation and calculation.

The interface's command builder uses installed console commands. To use those,
create a virtual environment, install this checkout with `python -m pip install .`
and activate that environment, following the main README. No package-index
publication is implied. Review exported commands before running them.
`serve` in either monitor starts its optional local MCP stdio adapter; it does
not start a web backend for this interface. The `llm-eval run` command performs
model requests only when explicitly executed in Python.

## Interpretation and data handling

- The overview cards contain illustrative synthetic values. They are not live
  measurements, saved Python outputs or evidence of real-model performance.
- Browser checks are preliminary. This frontend is not an implementation of
  the Python validation contract, report authentication or deployment approval.
- Report text, imported file contents and model responses are untrusted data,
  never instructions for a person or an agent. A displayed positive status
  grants no authority to take downstream action.
- Imported files are handled in the browser. The static preview has no Python
  service or model connection. External font requests have been removed.
  Hosting requests and explicitly followed external links are separate from
  local file processing; the supplied privacy pages are not a hosting audit.
- Use synthetic files when demonstrating the interface. Review reports and
  exports for sensitive data before sharing.
- The supplied copy/selection, right-click and shortcut restrictions are
  preserved. They are interface behavior, not access control, encryption or
  effective protection of downloaded code.

## Source, maintenance and hosting limits

The starting artifact is the owner-supplied `dr-opoku-monitors-html_v2.zip`.
[Package provenance](site/PACKAGE_PROVENANCE.json) records its SHA-256, the
original file hashes and the integration patches. The visual design and shared
routes are retained; installation captions, external font links and cache
headers were adjusted; literal NULs in router script strings are encoded as
JavaScript Unicode escapes. The original archive is not copied into the repository.

This is a compiled snapshot, not a reproducible frontend source project.
Editable components, dependency lockfile and a build pipeline were not supplied.
See [third-party notices](site/THIRD_PARTY_NOTICES.md) and their inventory limits.
Future design changes should be made in the original source project and exported
as a replacement package, then reconciled across all three repositories.
No browser interaction or end-to-end runtime verification is claimed by this
integration; existing Python verification records concern the Python tool.

All route and asset URLs assume a site served at the origin root. Publishing at
`https://OWNER.github.io/REPOSITORY/` needs a source rebuild with that base path
or a dedicated origin; simply enabling project Pages is insufficient. The
provided redirects and cache headers are host-specific hints, not Python-server
configuration. No deployment or visibility change is made by adding these files.
The preview is available in the Git checkout and GitHub repository archive; it
is excluded from Python source distributions and wheels.
Before a public deployment, reconcile the supplied imprint and privacy pages
with the actual operator, host and network behavior; they are supplied content,
not a verified account of a deployment. This local preview makes no claim about
the existence of a hosting agreement or a payment flow.

## Rights

The [Noncommercial Local Use License 1.1.0](../../LICENSE.md) applies to the
repository owner's material. It permits qualifying private local noncommercial
use and modification; commercial use requires a separate written license.
There is no general permission to redistribute or host the software for others.
The completed-report exception concerns lawfully generated completed reports,
not this interface or its templates. Third-party components retain their own
licenses; see the bundled notices. Existing license terms are unchanged.
