from fine_tuning.find_table.lookup_pipeline import QueryPipeline

def main():
    query = "Which space types have the highest lighting power densities in the 2016 ASHRAE 90.1 standard, and what are their control requirements?"

    with QueryPipeline() as pipeline:
        result = pipeline.run(query)
        print(f"Result:\n{result}")


if __name__ == "__main__":
    main()