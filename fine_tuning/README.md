# Synthetic Dataset Generator

A Python script that generates synthetic SQL question-query pairs for building energy standards databases using Large Language Models (LLMs).

## Overview

`generate_synthetic_dataset.py` analyzes existing question-query examples and uses an LLM to generate new, similar examples that are validated against the actual database. This helps expand training datasets for SQL-to-natural language models.

## Features

- **Pattern Analysis**: Analyzes existing examples to understand query patterns, table usage, and complexity distributions
- **Smart Generation**: Uses LLM with guided prompts based on database schema and existing patterns
- **Batch Validation**: Efficiently validates generated queries against the actual database using batch processing
- **Result Verification**: Ensures generated queries not only have valid syntax but also return meaningful results
- **Flexible Matching**: Emphasizes LIKE operators and broad filters to avoid overly specific queries that return no results

## Configuration

Edit these constants at the top of the script:

```python
EXISTING_CSV = "building_std_queries.csv"        # Input CSV with existing examples
OUTPUT_CSV = "updated_building_queries.csv"      # Output CSV with all examples
SQLITE_DB = "openstudio_standards.db"            # SQLite database path
TARGET_COUNT = 1000                              # Total examples desired
```

## Usage

```bash
cd fine_tuning/
python generate_synthetic_dataset.py
```

## Input Format

The input CSV should have columns:
- `question`: Natural language question
- `answer`: Corresponding SQL query

## Output

The script generates:
1. **Expanded CSV**: Contains original + new validated examples
2. **Pattern Analysis**: Console output showing query complexity distribution and common patterns
3. **Progress Updates**: Real-time feedback on generation and validation success rates

## Key Optimizations

### Batch Validation
- Opens database connection once per batch (10 queries) instead of per query
- Significantly faster than individual query validation

### Smart Query Generation
- Prefers simple single-table queries over complex joins
- Uses flexible matching with LIKE operators (e.g., `building_type LIKE '%4A%'`)
- Avoids overly specific filter combinations
- Focuses on practical, real-world questions

### Result Quality
- Validates both syntax AND result existence
- Filters out queries that return no rows
- Reports success rates for each generation batch

## Example Generated Queries

```sql
-- Simple filtering with flexible matching
SELECT * FROM envelope_requirements_90_1 
WHERE climate_zone LIKE '%4A%' AND building_type LIKE '%Office%';

-- Aggregation with meaningful results
SELECT building_type, AVG(maximum_u_factor) 
FROM envelope_requirements_90_1 
WHERE intended_surface_type LIKE '%Wall%' 
GROUP BY building_type;
```

## Dependencies

- `sqlite3`: Database operations
- `langchain_ollama`: LLM integration
- `csv`, `json`, `re`: Data processing
- Standard library modules

## Performance Notes

- LLM generation is the primary bottleneck (network/model dependent)
- Database validation is optimized with batch processing
- Typical generation: ~10-30 seconds per 10-query batch
- Success rates vary but typically 60-80% of generated queries are valid and return results