"""cmerate: data pipeline and forecast verification for CME occurrence rates.

Modules
-------
config    load config/config.toml and resolve paths
cdaw      parse the SOHO/LASCO CDAW universal CME list (text version)
ssn       read the SILSO monthly sunspot number (V2.0)
coverage  per-month observing-coverage proxy from gaps in the catalog
tables    monthly and annual count tables
numbers   export every number quoted in the manuscript (JSON + LaTeX macros)
"""

__version__ = "0.1.0"
