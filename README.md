# erozym
An e-tutoring website built on flask with SQLAlchemy

## Local setup and checks

The pinned Flask/Werkzeug versions require Python 3.9 or newer. Python 3.11 and 3.12 were verified locally.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python -B -m unittest discover -s tests -v
python -m flask --app main run
```

The checked-in app currently renders templates; its SQLAlchemy import is commented out. The declared ORM packages are retained and tested separately with in-memory SQLite.

See [DEPENDENCY_REVIEW.md](DEPENDENCY_REVIEW.md) for CVE applicability, extension compatibility, test results and verification limits.
