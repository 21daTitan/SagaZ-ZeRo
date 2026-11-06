"""Read-only tools exposed over authenticated MCP."""
from sagaz.attribution import credits
from sagaz.catalog import skills
from sagaz.cti import summary as cti_summary, search as cti_search

BUILTINS = {
    'sagaz_status': credits,
    'sagaz_skills': skills,
    'sagaz_cti_summary': cti_summary,
    'sagaz_cti_search': cti_search,
}
