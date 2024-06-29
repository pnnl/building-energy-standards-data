![Tests](https://github.com/pnnl/building-energy-standards-data/actions/workflows/openstudio_standards_database.yml/badge.svg)

# Building Energy Standards Data
This repository hosts a database of building energy standards data to be used in building energy simulation applications. Data includes essential and tabulatable prescriptive building energy code requirements (e.g., minimum equipment efficiency or minimum opaque surface thermal performance requirement) and other space type related assumptions (e.g., maximum lighting power allowance) that can be used to create building energy models.

Note that not all prescriptive requirements are included in the database as building energy codes and standards include many exceptions to certain requirements which makes the creation of practical data table difficult. Users of the database are encouraged to leverage knowledge of the codes along with the data tables.

The database covers data related to ASHRAE Standard 90.1-2004 through 2022, ASHRAE Standard 62.1-1999 through 2022, and the International Energy Conservation Code (IECC) 2006 through 2021. It also includes specific data tables for the Performance Rating Method of ASHRAE Standard 90.1 (Appendix G). The structure of the database is documented [here](/docs/Structure.md).

The database is the main data source for the [openstudio-standards](https://github.com/NREL/openstudio-standards) Ruby gem and supersedes its original [database](https://drive.google.com/drive/folders/1x7yEU4jnKw-gskLBih8IopStwl0KAMEi).

This repository includes the database as well as Python APIs that can be used to build, query, edit, and export the database to formats such as SQLite, CSV and JSON.

# Accessing the Database
## Locally
The database can be accessed by either cloning this repository or by installing it using `pip` by running `pip install building-energy-standards-data`. To get started with the database, a quick start guide is provided [here](/docs/QuickStartGuide.md).

## Webservices
Forthcoming!

# Contributing
Developer documentation, notes, and contribution guidelines are located [here](/docs/DeveloperNotes.md).

# Potential Future Enhancements
- Input validation to the functions used to generate/export the database and the OpenStudio-Standards data
- Command line interface to perform the generation/export/modification
