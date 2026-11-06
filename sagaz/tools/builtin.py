"""Read-only tools exposed over authenticated MCP."""
from sagaz.attribution import credits
from sagaz.catalog import skills
from sagaz.cti import search, summary


def _no_arguments(arguments, function):
    if arguments:
        raise ValueError("No arguments accepted for this tool")
    return function()


def _cti_search(arguments):
    if not isinstance(arguments, dict) or set(arguments) - {"q", "limit"}:
        raise ValueError("Invalid CTI search arguments")
    return search(arguments.get("q"), arguments.get("limit", 20))


def _status(arguments):
    return _no_arguments(arguments, credits)


def _skills(arguments):
    return _no_arguments(arguments, skills)


def _cti_summary(arguments):
    return _no_arguments(arguments, summary)

BUILTINS = {
    'sagaz_status': _status,
    'sagaz_skills': _skills,
    'sagaz_cti_summary': _cti_summary,
    'sagaz_cti_search': _cti_search,
}
