# Ontology Design Guide

*For Building Energy Standards Table Retrieval*

## Purpose

We are building an ontology to classify database tables containing building energy standards data (e.g., ASHRAE 90.1, IECC).

The ontology is used to:

1. Interpret natural language queries.
2. Match those queries to the correct database table.
3. Improve table ranking before SQL generation.

---

# How the Ontology Is Used

Each table in the database is assigned a structured descriptor (a set of semantic attributes).

When a user asks a question:

1. An LLM extracts ontology attributes from the query.
2. We compare the query attributes to table descriptors.
3. We rank tables using weighted matching.
4. The best table is passed to SQL generation.

So the ontology must:

* Be predictable enough for an LLM to extract reliably.
* Be discriminative enough to distinguish tables.
* Avoid unnecessary overlap between dimensions.

---

# Design Constraints

## 1. It Must Be Retrieval-Oriented

This ontology is not a knowledge graph.

It does not need to represent:

* Full regulatory logic
* Code exceptions
* Hierarchical legal structure

It only needs to help answer:

> “Which table should answer this query?”

---

## 2. Dimensions Should Be Independent

Each attribute (dimension) should represent a distinct axis of meaning.

Avoid:

* Overlapping concepts across dimensions.
* Encoding the same idea in multiple places.
* Mixing equipment type, regulatory role, and domain in one category.

---

## 3. It Must Work With LLM Extraction

The ontology must be clear enough that categories are intuitive.

Ambiguous or overly granular categories will reduce extraction reliability.

---

## 4. It Must Disambiguate Similar Tables

If two tables are often confused, the ontology should help separate them.

Example differences might include:

* Prescriptive vs performance path
* Requirement vs reference data
* Equipment type
* Standard year

---

# What Makes a Good Ontology Here

A good ontology will:

* Cleanly partition the database tables.
* Reduce ranking noise.
* Improve first-pass table selection.
* (Maybe) Reflect how engineers mentally organize the standards.