import sys

from .validate_files import process_and_validate_files
from .llm_setup import get_api_key_model
from .generate_data import generate_synthetic_data
from .output import generate_output


def get_csv_data():

    # Process and validate files
    args = sys.argv[1:]
    config, reference_file, delimiter, yaml_filename, csv_filename = process_and_validate_files(args)

    # Choose whichever filename exists (for naming output)
    input_filename = csv_filename or yaml_filename or "output"
    print(input_filename)

    # Get Provider, API Key and Model
    provider, api_key, model = get_api_key_model()
    
    # Generate synthetic data
    df = generate_synthetic_data(config, reference_file, provider, api_key, model)
    
    # Save Synthetic data
    generate_output(df, input_filename, delimiter)

if __name__ == "__main__":
    get_csv_data()
