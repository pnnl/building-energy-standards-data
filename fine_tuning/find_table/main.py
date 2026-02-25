from fine_tuning.find_table.lookup_pipeline import QueryPipeline


def main():
    query = "What climate zones are included in the IECC envelope requirements dataset?"
    # query = "What is the maximum permitted assembly U-value for a residential exterior mass wall in Climate Zone 3A according to ASHRAE 90.1-2004?"

    with QueryPipeline() as pipeline:
        result = pipeline.run(query)
        print(f"Result:\n{result}")


if __name__ == "__main__":
    main()
