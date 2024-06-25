# Database Structure and Covered Data
## Structure
The figure below shows an overview of the structure of the database and of the data management approach.
![Overview of the Database Structure](database_structure.png "Database Structure")
## Covered Data
As shown in the figure above, the database contains two types of data: space type data and non-space type related data. The space type related data is made of three distinct but interconnected levels.

- The first level, level 1, corresponds to a single data table that contains a list of space type names supported by OpenStudio-Standards and a mapping to different sub-space type names (such as lighting, ventilation, and equipment, etc.) that can be used to determine general modeling assumption for a space type for a specific building energy code version.
- The second level, level 2, is a collection of data tables that contains lists of sub-space type names and references to different code requirement values.
- The third and final level, level 3, is a collection of data tables that contains raw information from building energy codes, such as lighting power allowances and required ventilation rates.
The list of space type provided in the level 1 table is a concise yet exhaustive list of space type that can be used to model most commercial building spaces. Assumptions for these space types are contained in the level 2 and level 3 tables, however these tables contain additional information about more specific space type requirements (or less specific, e.g., through the building area method lighting power allowances).

This approach lends itself to customization, for example, the mapping of a particular space type name to sub-space type can be overwritten by changing the reference to the sub-space types (level 2) in the level 1 table. Another possible use of the database is to only access the level 3 data tables to get a direct access to the raw code information in a tabulated format which, again, contains more data than what is used to derive the modeling assumptions for the space types listed in the level 1 table.

The non-space type related data, contains all other data needed by OpenStudio-Standards, this includes constructions/materials tables, performance curves tables, minimum code required HVAC efficiency, system requirements, etc.

### Space Type Data
#### Space Type Names
The space type names list has been created using engineering judgment and the space type name list from the ASHRAE Standard 90.1 lighting building area and space-by-space tables. Space type names were either concatenated or simplified to be self-descriptive.
#### Lighting
Lighting assumptions for each space type comes from actual building energy code requirements. As the space type names referenced in each version of ASHRAE Standard 90.1 changes from one version to another, a mapping effort was conducted to reconcile the requirements for each space type for all versions of the code.
#### People density and Ventilation
The people density and ventilation data originate from values specified in ASHRAE Standard 62.1. Similarly to the lighting data, a mapping effort was conducted to reconcile the requirements for each space type for all versions of the code. While OpenStudio-Standards currently offers data for the 2004 version of 90.1 up to the 2019 version of 90.1, ventilation/people density values for some space type could not be found for all versions of 62.1. In this instance, if available, older values were used, all the way to 62.1-1999 when needed.
#### Equipment
The equipment assumptions are based on a plug-load values derived from a project led at the Pacific Northwest National Laboratory (PNNL) named *Development of Building-Space-Specific Loads for Performance Rating Methods*. Plug-load for each space type were determined using a bottom-up approach, see the figure below. Minimum, maximum, average, and median equipment power density values are provided (average values are currently used when exporting the data to the JSON files used by OpenStudio-Standards).

![Equipment Power Density Determination Using Plug-Load Data](plug_loads_methodology.png "Equipment Power Density Determination Using Plug-Load Data")
#### Schedules
The schedules used in the database were determined based on the PNNL led *Development of Building-Space-Specific Loads for Performance Rating Methods* project. The schedules were derived from the [SBEM-NCN database](https://www.ncm-pcdb.org.uk/sap/page.jsp?id=7), modifications were applied to make them perceived as more realistic such as reducing the occupancy fraction during the day (as space is very rarely fully occupied), or leave a very small fraction of the lights on at night.