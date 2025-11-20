from fine_tuning.data_processing import augment, add_context

EXCEL_FILE = "fine_tuning/dataset/raw/building_std_queries.xlsx"
CONTEXT_OUTPUT_FILE = "fine_tuning/dataset/processed/questions_with_context.csv"
DB_FILE = "openstudio_standards.db"
AUGMENT_OUTPUT_FILE = "fine_tuning/dataset/final/augmented_questions_with_context.csv"

if __name__ == "__main__":
    add_context(EXCEL_FILE, DB_FILE, CONTEXT_OUTPUT_FILE)
    augment(CONTEXT_OUTPUT_FILE, AUGMENT_OUTPUT_FILE)
