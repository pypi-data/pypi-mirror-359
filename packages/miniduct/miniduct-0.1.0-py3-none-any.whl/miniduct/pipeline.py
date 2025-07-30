import datetime


def get_base_name(name):
    return f"{name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

def run_pipeline(pipeline_name,
                 ingestion,
                 outputs=[],
                 name_template=get_base_name):
    """
    Function to run a pipeline with the given name, ingestion method, and outputs.

    :param name: Name of the pipeline.
    :param ingestion: Ingestion method to fetch data.
    :param outputs: List of output methods to process the data.
    :return: None
    """
    data = ingestion.get()
    print("Data fetched from ingestion:", data)
    
    for output in outputs:
        print(f"Processing output with {output.__class__.__name__}")
        output.write(data, file_name=name_template(pipeline_name))
