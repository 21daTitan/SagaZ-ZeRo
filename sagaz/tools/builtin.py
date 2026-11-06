"""Read-only tools exposed over authenticated MCP."""
from sagaz.attribution import credits
from sagaz.catalog import skills

BUILTINS = {
    'sagaz_status': credits,
    'sagaz_skills': skills,
}
