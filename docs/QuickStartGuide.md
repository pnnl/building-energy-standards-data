## Quick Start Guide
Please note that if you have installed the database with `pip` you will need to add `import building_energy_standards_data` at the beginning of the code snippets shown below. Otherwise, if you are running the following code snippets from a clone of the repository, make sure to run them from the root directory.

Also, if installing the database using `pip`, one should use `create_database()` in place of `create_openstudio_standards_database_from_json()` or `create_openstudio_standards_database_from_csv()`.
### Create the Database
```python
import sqlite3
from building_energy_standards_data.applications.database_maintenance import create_openstudio_standards_database_from_json

conn = sqlite3.connect('openstudio_standards.db')
create_openstudio_standards_database_from_json(conn)
conn.close()
```

This code will generate an `openstudio_standards_database.sql` file in the same file directory. The database can be opened using a software such as [DB Browser for SQLite](https://sqlitebrowser.org/).
### Export the Database Data
```python
from building_energy_standards_data.applications.database_maintenance import export_openstudio_standards_database_to_json
conn = sqlite3.connect('openstudio_standards.db')
export_openstudio_standards_database_to_json(conn, save_dir='./building_energy_standards_data/database_files/')
```
Assuming that `openstudio_standards.db` is a valid SQLite database name, the code above will export the content of the database tables to JSON files located in `./database_files/`. Because data tables are typically easier to read, parse, and modify in a spreadsheet format, the data tables can also be exported to CSV files. The code block below shows an example of how one can do so.
```python
from building_energy_standards_data.applications.database_maintenance import export_openstudio_standards_database_to_csv
conn = sqlite3.connect('openstudio_standards.db')
export_openstudio_standards_database_to_csv(conn, save_dir='./building_energy_standards_data/database_files/')
```
### Modifying the Database
The database data can be updated by modifying the JSON files directly, or the exported CSV files and then be regenerated using the following code block.
```python
import sqlite3
from building_energy_standards_data.applications.database_maintenance import create_openstudio_standards_database_from_csv

conn = sqlite3.connect('openstudio_standards.db')
create_openstudio_standards_database_from_csv(conn)
conn.close()
```
New tables can be added to the database, but they have to first be defined programmatically first. A new file should be created in `./database_tables`. Each file defines the "schema" of a table and how it relates to other tables. The content of the new file can be adapted from an existing file. A JSON or CSV file containing the initial data to populate the database should be added to `./database_files` and added to the `__init__.py` file located in `./database_tables`.

### Logging
Logs can be generated when running some of the previously mentioned code by using the following lines first.
```python
import logging
logging.getLogger().setLevel(logging.INFO)
```
### Generate OpenStudio-Standards Data
The following code block can be used to generate the non-space type related data needed by Openstudio-Standards to operate for several versions of ASHRAE Standard 90.1. The function will export the JSON files in the right directory.
```python
import sqlite3
conn = sqlite3.connect('openstudio_standards.db')
from building_energy_standards_data.applications.create_openstudio_standards_json import create_openstudio_standards_data_json_ashrae_90_1
for t in ["2004", "2007", "2010", "2013", "2016", "2019"]:
    create_openstudio_standards_data_json_ashrae_90_1(conn=conn, version_90_1=t, osstd_repository_path="./")
conn.close()
```
The following code block can be used to generate the space type related data needed by Openstudio-Standards to operate for several versions of ASHRAE Standard 90.1. The function will export the JSON files in the right directory.
```python
import sqlite3
conn = sqlite3.connect('openstudio_standards.db')
from building_energy_standards_data.applications.create_openstudio_standards_json import create_openstudio_standards_space_data_json_ashrae_90_1
for t in ["2004", "2007", "2010", "2013", "2016", "2019"]:
    create_openstudio_standards_space_data_json_ashrae_90_1(conn=conn, version_90_1=t, osstd_repository_path="./")
conn.close()
```
