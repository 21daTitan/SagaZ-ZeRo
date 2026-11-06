"""Permanent identification of the SagaZ project and upstream inspiration."""

UPSTREAM_NAME = "Evil Cassandra V3.1b"
UPSTREAM_AUTHOR = "Mörlsara"
UPSTREAM_HANDLE = "@DarkyHArry"
UPSTREAM_GROUP = "Code Nexus"
UPSTREAM_REPO = "https://github.com/DarkyHArry/cassandra-agent"
FORK_AUTHOR = "dSant"
FORK_HANDLE = "@21daTitan"
FORK_ORGANIZATION = "Systemia Solutions"
FORK_NAME = "SagaZ ZeRo"
FORK_VERSION = "3.7.0-zeRo"
PERSONA_LAYER = "HooLeeSheet"
ORIGIN_MARK = "Morlsara Code Nexus"


def credits():
    return {
        "name": FORK_NAME,
        "version": FORK_VERSION,
        "persona": PERSONA_LAYER,
        "author": FORK_AUTHOR,
        "organization": FORK_ORGANIZATION,
        "origin_mark": ORIGIN_MARK,
        "inspiration": {
            "project": UPSTREAM_NAME,
            "author": UPSTREAM_AUTHOR,
            "handle": UPSTREAM_HANDLE,
            "group": UPSTREAM_GROUP,
            "url": UPSTREAM_REPO,
        },
        "relationship": "Independent implementation inspired by Cassandra; no upstream code redistributed.",
    }


def machine_tag():
    """Permanent machine-readable identification without impersonating the upstream."""
    return f"sagaz-zero:{FORK_VERSION}:{FORK_HANDLE}:{ORIGIN_MARK}"


def attribution_trailer():
    return (f"{FORK_NAME} / {PERSONA_LAYER} by {FORK_AUTHOR} ({FORK_HANDLE}) "
            f"| inspired by {UPSTREAM_NAME} / {UPSTREAM_AUTHOR} / {UPSTREAM_GROUP} "
            f"| {UPSTREAM_REPO} | {ORIGIN_MARK}")


def verify():
    return all((UPSTREAM_AUTHOR == "Mörlsara", UPSTREAM_GROUP == "Code Nexus",
                UPSTREAM_REPO == "https://github.com/DarkyHArry/cassandra-agent",
                ORIGIN_MARK == "Morlsara Code Nexus", FORK_NAME == "SagaZ ZeRo",
                PERSONA_LAYER == "HooLeeSheet"))
