"""cmerate: data pipeline and forecast verification for CME occurrence rates.

Modules
-------
config    load config/config.toml and resolve paths
cdaw      parse the SOHO/LASCO CDAW universal CME list (text version)
ssn       read the SILSO monthly sunspot number (V2.0)
coverage  monthly observing coverage from the official LASCO/C2 data-gap lists
tables    monthly and annual count tables
numbers   export every number quoted in the manuscript (JSON + LaTeX macros)
features  information available at an issue date: predictors, targets, analogue
rolling   rolling-origin design: test issues and training sets
scores    verification scores for count forecasts (CRPS, PIT, coverage, ...)
"""

__version__ = "0.1.0"
