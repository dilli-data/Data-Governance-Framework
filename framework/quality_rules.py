import great_expectations as ge
from great_expectations.dataset import PandasDataset
from typing import Dict, List, Optional
import json
import boto3
import yaml

class DataQualityValidator:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.s3_client = boto3.client('s3')
        self.expectation_suite = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load quality rules configuration"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def create_expectation_suite(self, suite_name: str):
        """Create a new expectation suite"""
        context = ge.get_context()
        self.expectation_suite = context.create_expectation_suite(
            suite_name,
            overwrite_existing=True
        )
    
    def add_numeric_rule(self, column: str, min_value: Optional[float] = None, 
                        max_value: Optional[float] = None, null_allowed: bool = False):
        """Add numeric validation rules"""
        if not self.expectation_suite:
            raise ValueError("Create expectation suite first")
            
        if not null_allowed:
            self.expectation_suite.add_expectation(
                ge.expect_column_values_to_not_be_null(column)
            )
            
        if min_value is not None:
            self.expectation_suite.add_expectation(
                ge.expect_column_values_to_be_between(
                    column,
                    min_value=min_value,
                    max_value=max_value
                )
            )
    
    def add_categorical_rule(self, column: str, allowed_values: List[str], 
                           null_allowed: bool = False):
        """Add categorical validation rules"""
        if not self.expectation_suite:
            raise ValueError("Create expectation suite first")
            
        if not null_allowed:
            self.expectation_suite.add_expectation(
                ge.expect_column_values_to_not_be_null(column)
            )
            
        self.expectation_suite.add_expectation(
            ge.expect_column_values_to_be_in_set(
                column,
                value_set=allowed_values
            )
        )
    
    def add_pattern_rule(self, column: str, pattern: str, null_allowed: bool = False):
        """Add pattern matching validation rules"""
        if not self.expectation_suite:
            raise ValueError("Create expectation suite first")
            
        if not null_allowed:
            self.expectation_suite.add_expectation(
                ge.expect_column_values_to_not_be_null(column)
            )
            
        self.expectation_suite.add_expectation(
            ge.expect_column_values_to_match_regex(
                column,
                regex=pattern
            )
        )
    
    def validate_data(self, data: PandasDataset) -> Dict:
        """Run validation on the dataset"""
        if not self.expectation_suite:
            raise ValueError("Create expectation suite first")
            
        validation_result = data.validate(
            expectation_suite=self.expectation_suite,
            result_format="COMPLETE"
        )
        
        return {
            'success': validation_result.success,
            'statistics': validation_result.statistics,
            'results': [
                {
                    'expectation_type': result.expectation_config.expectation_type,
                    'success': result.success,
                    'column': result.expectation_config.kwargs.get('column'),
                    'message': result.message
                }
                for result in validation_result.results
            ]
        }
    
    def save_validation_results(self, results: Dict, bucket: str, key: str):
        """Save validation results to S3"""
        self.s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(results, indent=2)
        )

def main():
    # Example usage for Higher Education data
    validator = DataQualityValidator('configs/higher_ed_config.yaml')
    
    # Create expectation suite
    validator.create_expectation_suite('student_records_quality')
    
    # Add rules for GPA
    validator.add_numeric_rule(
        column='gpa',
        min_value=0.0,
        max_value=4.0,
        null_allowed=False
    )
    
    # Add rules for enrollment status
    validator.add_categorical_rule(
        column='enrollment_status',
        allowed_values=['ACTIVE', 'INACTIVE', 'GRADUATED', 'WITHDRAWN'],
        null_allowed=False
    )
    
    # Add rules for student ID
    validator.add_pattern_rule(
        column='student_id',
        pattern=r'^[A-Z]{2}\d{8}$',
        null_allowed=False
    )
    
    # Example validation
    sample_data = {
        'gpa': [3.85, 4.0, 2.5, None],
        'enrollment_status': ['ACTIVE', 'GRADUATED', 'INVALID', 'ACTIVE'],
        'student_id': ['AB12345678', 'CD87654321', 'INVALID', 'EF12345678']
    }
    
    dataset = PandasDataset(sample_data)
    results = validator.validate_data(dataset)
    
    # Save results
    validator.save_validation_results(
        results,
        bucket='data-quality-results',
        key='student_records/validation_20240315.json'
    )

if __name__ == "__main__":
    main() 