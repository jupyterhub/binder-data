import nox

# Use uv as the default backend for all sessions
nox.options.default_venv_backend = "uv"


@nox.session(name="docs")
def docs(session):
    """Build the documentation."""
    session.install("-r", "requirements.txt")
    session.install("mystmd")
    session.cd("analysis")
    session.run("myst", "build", "--html", "--execute", "-d")


@nox.session(name="docs-live")
def docs_live(session):
    """Build and serve the documentation with live reload."""
    session.install("-r", "requirements.txt")
    session.install("mystmd")
    session.cd("analysis")
    session.run("myst", "start", "--execute")
