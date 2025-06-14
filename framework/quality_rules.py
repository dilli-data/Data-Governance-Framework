import great_expectations as ge
from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.data_context import DataContext
from great_expectations.dataset import PandasDataset
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StudentRecordsValidator:
    def __init__(self, data_path=None, context_path=None):
        """
        Initialize the validator with optional data path and context path.
        
        Args:
            data_path (str): Path to the CSV file containing student records
            context_path (str): Path to the Great Expectations context directory
        """
        self.data_path = data_path
        self.context_path = context_path or os.path.join(os.path.dirname(__file__), "great_expectations")
        
        # Initialize Great Expectations context
        try:
            self.context = DataContext(self.context_path)
        except Exception as e:
            logger.warning(f"Could not load existing context: {e}")
            self.context = DataContext.create(self.context_path)
    
    def validate_student_records(self, data_path=None):
        """
        Validate student records using Great Expectations.
        
        Args:
            data_path (str): Optional path to override the data file
            
        Returns:
            dict: Validation results
        """
        data_path = data_path or self.data_path
        if not data_path:
            raise ValueError("No data path provided")
        
        # Read the CSV file
        df = pd.read_csv(data_path)
        dataset = PandasDataset(df)
        
        # Define expectations
        expectations = [
            # GPA validation
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_be_between",
                kwargs={
                    "column": "gpa",
                    "min_value": 0.0,
                    "max_value": 4.0,
                    "parse_strings_as_datetimes": False
                }
            ),
            
            # Student ID format validation
            ExpectationConfiguration(
                expectation_type="expect_column_value_lengths_to_be_between",
                kwargs={
                    "column": "student_id",
                    "min_value": 6,
                    "max_value": 10
                }
            ),
            
            # Student ID alphanumeric validation
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_match_regex",
                kwargs={
                    "column": "student_id",
                    "regex": "^[A-Za-z0-9]+$"
                }
            ),
            
            # Required columns validation
            ExpectationConfiguration(
                expectation_type="expect_table_columns_to_match_ordered_list",
                kwargs={
                    "column_list": [
                        "student_id", "first_name", "last_name", "email",
                        "date_of_birth", "ssn", "gpa", "enrollment_status",
                        "department", "major", "enrollment_date", "graduation_date"
                    ]
                }
            ),
            
            # Email format validation
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_match_regex",
                kwargs={
                    "column": "email",
                    "regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                }
            ),
            
            # SSN format validation
            ExpectationConfiguration(
                expectation_type="expect_column_values_to_match_regex",
                kwargs={
                    "column": "ssn",
                    "regex": r"^\d{3}-\d{2}-\d{4}$"
                }
            )
        ]
        
        # Add expectations to dataset
        for expectation in expectations:
            dataset.add_expectation(expectation)
        
        # Run validation
        validation_result = dataset.validate()
        
        # Log results
        if validation_result.success:
            logger.info("All validations passed successfully!")
        else:
            logger.warning("Some validations failed:")
            for result in validation_result.results:
                if not result.success:
                    logger.warning(f"Failed expectation: {result.expectation_config.expectation_type}")
                    logger.warning(f"Column: {result.expectation_config.kwargs.get('column', 'N/A')}")
                    logger.warning(f"Details: {result.result}")
        
        return {
            "success": validation_result.success,
            "results": validation_result.results,
            "statistics": validation_result.statistics
        }

def validate_student_data(data_path):
    """
    Convenience function to validate student data.
    This function can be called from deploy_lake_formation_policies.py.
    
    Args:
        data_path (str): Path to the student records CSV file
        
    Returns:
        dict: Validation results
    """
    validator = StudentRecordsValidator(data_path=data_path)
    return validator.validate_student_records()

if __name__ == "__main__":
    # Example usage
    sample_data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "examples",
        "higher_ed",
        "student_records_sample.csv"
    )
    
    results = validate_student_data(sample_data_path)
    print(f"Validation successful: {results['success']}") 