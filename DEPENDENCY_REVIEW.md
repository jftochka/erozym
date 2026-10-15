# Dependency security review — 2026-10-15

This review concerns the checked-in application and its Python dependencies. Deployment, actual traffic, operating system, reverse proxies and production use are unknown.

## Selected versions and compatibility

| Package | Previous | Proposed | Reason |
| --- | --- | --- | --- |
| Flask | 2.2.2 | 3.1.3 | Includes permanent-session and keys-only session cache-header fixes. |
| Werkzeug | 2.2.2 | 3.1.9 | Includes multipart, cookie, debugger and current Windows static-path fixes. |
| Jinja2 | 3.1.2 | 3.1.6 | Includes xmlattr, template-filename and sandbox fixes. |
| itsdangerous | 2.1.2 | 2.2.0 | Required by Flask 3.1.3. |
| blinker | not previously required | 1.9.0 | Required by Flask 3.1.3; pinned explicitly. |

Flask and Werkzeug now require Python >=3.9. Local verification used CPython 3.11.17 and 3.12.14 on Linux. Python 3.9, 3.10, other interpreters and native Windows were not executed. A deployment using Python 3.7 or 3.8 must first move to a compatible interpreter.

No changes to application Python source or HTML templates are required for these upgrades. Existing route, method and rendering behavior is preserved in the local checks below. No authentication, cache, form or template-sandbox configuration is introduced.

Upstream release references: [Flask](https://flask.palletsprojects.com/en/stable/changes/), [Werkzeug](https://werkzeug.palletsprojects.com/en/stable/changes/), [Jinja](https://jinja.palletsprojects.com/en/stable/changes/).

## CVE applicability

All entries below matched the original pinned versions. "No path found" describes this repository's inspected source, not a claim that the library is safe or that unseen deployment code cannot change the result.

| Package / CVE | First relevant fixed release | Application applicability |
| --- | --- | --- |
| Flask [CVE-2023-30861](https://github.com/pallets/flask/security/advisories/GHSA-m2qf-hxjv-5gpq) | 2.2.5 / 2.3.2 | No path found: no secret key or permanent-session workflow. Exploitation additionally requires a caching proxy with the advisory's cookie/cache behavior. Proxy state is unknown. |
| Flask [CVE-2026-27205](https://github.com/pallets/flask/security/advisories/GHSA-68rp-wp8r-4726) | 3.1.3 | No path found: application and templates do not inspect session keys or length. |
| Werkzeug [CVE-2023-25577](https://github.com/pallets/werkzeug/security/advisories/GHSA-xg9f-g7g7-2323) | 2.2.3 | No multipart parser sink found. Registered views render templates and do not access request.form, request.files or request.data. |
| Werkzeug [CVE-2023-46136](https://github.com/pallets/werkzeug/security/advisories/GHSA-hrfv-mqp8-q5rw) | 2.3.8 / 3.0.1 | No multipart parser sink found. |
| Werkzeug [CVE-2024-49767](https://github.com/pallets/werkzeug/security/advisories/GHSA-q34m-jh98-gwm2) | 3.0.6 | No multipart parser sink found. |
| Werkzeug [CVE-2023-23934](https://github.com/pallets/werkzeug/security/advisories/GHSA-px8h-6qxv-m22q) | 2.2.3 | No authentication/cookie decision found. Exploitation needs additional browser and adjacent-subdomain conditions. |
| Werkzeug [CVE-2024-34069](https://github.com/pallets/werkzeug/security/advisories/GHSA-2g68-c3qc-8985) | 3.0.3 | Debugger not enabled by checked-in application configuration. External launch flags/environment remain unknown. |
| Werkzeug [CVE-2024-49766](https://github.com/pallets/werkzeug/security/advisories/GHSA-f9vj-2wh5-fj8j) | 3.0.6 | Conditional: built-in static route is reachable; vulnerable safe_join behavior requires Windows and Python <3.11. Deployment platform is unknown. |
| Werkzeug [CVE-2025-66221](https://github.com/pallets/werkzeug/security/advisories/GHSA-hgf8-39gv-g3f2) | 3.1.4 | Conditional: built-in static route uses send_from_directory/safe_join. Windows device-name behavior is relevant only on Windows. |
| Werkzeug [CVE-2026-21860](https://github.com/pallets/werkzeug/security/advisories/GHSA-87hc-h4r5-73f7) | 3.1.5 | Same Windows static-route condition, including extensions/trailing spaces. |
| Werkzeug [CVE-2026-27199](https://github.com/pallets/werkzeug/security/advisories/GHSA-29vq-49wr-vm6x) | 3.1.6 | Same Windows static-route condition, including multi-segment paths. |
| Werkzeug [CVE-2026-102598](https://github.com/pallets/werkzeug/security/advisories/GHSA-g6x2-hccm-hh4m) | 3.1.9 | Conditional Windows/NTFS static-route issue involving device names with empty ADS markers. |
| Jinja [CVE-2024-22195](https://github.com/pallets/jinja/security/advisories/GHSA-h5c8-rqwp-cp95) | 3.1.3 | No path found: no xmlattr filter or attacker-controlled attribute keys. |
| Jinja [CVE-2024-34064](https://github.com/pallets/jinja/security/advisories/GHSA-h75v-3vvj-5mfj) | 3.1.4 | No path found: no xmlattr filter or attacker-controlled attribute keys. |
| Jinja [CVE-2024-56201](https://github.com/pallets/jinja/security/advisories/GHSA-gmj6-6f8f-6699) | 3.1.5 | No path found: no attacker control of template source and filename. |
| Jinja [CVE-2024-56326](https://github.com/pallets/jinja/security/advisories/GHSA-q2x7-8rv6-6q7h) | 3.1.5 | No path found: no untrusted template execution or sandbox workflow. |
| Jinja [CVE-2025-27516](https://github.com/pallets/jinja/security/advisories/GHSA-cpwx-vrp4-4pq7) | 3.1.6 | No path found: no untrusted template execution or sandbox workflow. |

The two applications use trusted literal template names, inheritance and blocks. Source tracing included the entire Python application and all active templates. Default Flask static-file serving remains an affected boundary even though neither application explicitly imports send_from_directory.


## Repository evidence and confirmed results

- Base revision: 88d7d329e43eb8a40102c2af2e22ee4db841316f (2023-01-11).
- main.py:1-72 contains the application; there are fourteen registered HTML routes and Flask's built-in static route. The request import is unused. Templates contain no user-data expressions, xmlattr usage or session operations.
- main.py:2,7-11 imports and initializes Flask-Assets. **Reproduced compatibility failure:** Flask-Assets 2.0 imports the removed Flask _request_ctx_stack and prevents application import on Flask 3. Flask-Assets is therefore raised to 2.1.0; existing Environment and Bundle initialization and template rendering pass.
- greenlet is raised from 2.0.1 to 3.1.1 to provide Python 3.12 wheels. Installing the original complete requirements on this Linux Python 3.12 environment failed while trying to build old greenlet, with missing clang++; the original full requirements installed successfully on Python 3.11. This is a packaging/build result, not a demonstrated Python API failure.
- Flask-SQLAlchemy 3.0.2, SQLAlchemy 1.4.23, webassets 2.0, click 8.1.3 and MarkupSafe 2.1.1 are retained. No application ORM code is active, so no SQLAlchemy 2 migration is needed. A separate SQLite in-memory create/insert/commit/read/drop test confirms the retained ORM packages can work with the updated Flask/greenlet.
- The registered js_all bundle refers to missing jquery.js/base.js/widgets.js inputs, but no template uses an assets tag. Templates directly link static files. The dormant bundle was not built or activated, and no claim is made that its pre-existing inputs work.
- The /404 route continues to return its template with HTTP 200. Unknown paths continue to return HTTP 404.
- Six application test methods cover all fourteen page GET/HEAD responses, POST rejection, ignored multipart GET bodies, all template compilation, static CSS/ETag behavior, missing pages and encoded/unencoded static traversal.
- **Confirmed:** 15/15 tests pass on Python 3.11.17 and 3.12.14 using the twelve runtime pins in requirements.txt. One additional test covers the in-memory ORM round trip.
- **Confirmed:** syntax compilation and installed dependency metadata checks pass.
- **Confirmed:** a pre/post comparison of 59 HTTP checks found identical status codes, content types, HTML/body SHA-256 values and Set-Cookie observations, wherever recorded. This included GET/HEAD/OPTIONS/POST for fourteen pages, two error paths and one static CSS file.
- **Confirmed:** pip-audit 2.10.1 returned zero known vulnerability records for the twelve proposed runtime pins as of 2026-10-15. The original pins returned 33 advisory records representing **17 distinct CVE IDs**; duplicate advisory rows/aliases were deduplicated. These are independent audit results, not a claimed export/count of GitHub Dependabot alerts.

Changes are limited to requirements.txt, tests/test_app.py, tests/test_dependency_security.py, tests/test_optional_database.py, README.md and this review.

## Dependency-boundary regression tests

The tests use local probe applications and in-memory requests; they do not add application endpoints or expose a server.

- Permanent-session refresh must send Vary: Cookie.
- Session membership and length reads must send Vary: Cookie.
- 1,001 multipart fields and 1,001 multipart file parts must be rejected; ordinary field/file parsing must still work.
- A nameless cookie cannot shadow a valid __Host- cookie.
- xmlattr rejects space, slash, greater-than and equals delimiters in keys, while escaping a legitimate value.
- Sandbox attribute-filter and indirect str.format calls must block unsafe attribute traversal while allowing ordinary formatting.
- The Windows branch of safe_join rejects device-name variants, including nested paths and empty ADS markers. The test emulates Windows path functions without opening a device; it is not a native Windows execution test.

On the original full requirements under Python 3.11, these probes produced 17 failing assertions/subtests in seven test methods. This reproduced library-level behavior, not exploitation of either application. On the proposed requirements, all eight dependency test methods pass. Individual exploit reproducers were not run for every advisory; for example, slow-parser performance, the debugger, UNC access and malicious template filenames were assessed from source/advisories and dependency version inventory.

## Commands

From the repository root, in a fresh virtual environment using a compatible Python:

```sh
python -m pip install -r requirements.txt
python -m pip check
python -B -m unittest discover -s tests -v
```

For a dated advisory inventory, install pip-audit in a separate tooling environment and run:

```sh
pip-audit -r requirements.txt --no-deps --disable-pip --progress-spinner off
```

The audit command above checks the pinned requirements without resolving omitted transitive packages. In the verified Linux Python 3.11/3.12 environments, the runtime package inventory matches these pins. Platform/interpreter-specific transitive packages on other environments need their own inventory audit.

## Verification limits

No pre-existing tests or CI configuration were found. The added unittest suite was run locally; no hosted CI result is claimed.

No live deployment, traffic, reverse-proxy configuration, external middleware, externally supplied template loader, real database, browser rendering, CDN resource availability, load test or native Windows runtime was verified. No evidence establishes that this repository currently runs in production. Merging or deploying the proposed branch is a separate action, and default-branch Dependabot alert closure is not claimed.
