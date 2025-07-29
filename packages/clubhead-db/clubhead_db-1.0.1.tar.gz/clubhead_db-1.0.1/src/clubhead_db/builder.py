import sys
from . import data_processor
from . import label_merger

# --- Configuration ---
# Select the steops from the pipeline you wish to run
PIPELINE_STEPS = [
    data_processor.main,
    label_merger.main
]
# -------------------

def main():
    """Runs all steps in the data preparation pipeline."""
    print("--- Starting Data Preparation Pipeline ---")

    for step_function in PIPELINE_STEPS:
        print("\n" + "="*80)
        print(f"--- Running Step: {step_function.__module__}")
        print("="*80 + "\n")
        try:
            step_function()
            print(f"\nStatus: Step finished successfully.")
        except Exception as e:
            print(f"An error occurred while running the step: {e}")
            print("\nPipeline stopped due to an error in the previous step.")
            sys.exit(1)

    print("\n--- Data Preparation Pipeline Finished ---")
    print("The 'frames' directory is now ready with images and corresponding labels.")

if __name__ == '__main__':
    main()
