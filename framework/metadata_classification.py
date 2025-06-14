import boto3
import json
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class PrivacyLevel(Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"

@dataclass
class FieldClassification:
    field_name: str
    privacy_level: PrivacyLevel
    pii_type: Optional[str]
    masking_required: bool
    description: str

class MetadataClassifier:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.pii_patterns = self._load_pii_patterns()
        self.glue_client = boto3.client('glue')
        
    def _load_config(self, config_path: str) -> Dict:
        """Load industry-specific configuration"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _load_pii_patterns(self) -> Dict[str, str]:
        """Load regex patterns for PII detection"""
        return {
            'ssn': r'^\d{3}-?\d{2}-?\d{4}$',
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^\+?1?\d{9,15}$',
            'credit_card': r'^\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}$',
            'gpa': r'^[0-4]\.\d{2}$'
        }
    
    def classify_field(self, field_name: str, sample_values: List[str]) -> FieldClassification:
        """Classify a field based on its name and sample values"""
        # Check field name against known patterns
        field_name_lower = field_name.lower()
        
        # Default classification
        classification = FieldClassification(
            field_name=field_name,
            privacy_level=PrivacyLevel.INTERNAL,
            pii_type=None,
            masking_required=False,
            description="Standard field"
        )
        
        # Check for PII patterns in field name
        for pii_type, pattern in self.pii_patterns.items():
            if pii_type in field_name_lower:
                classification.pii_type = pii_type
                classification.privacy_level = PrivacyLevel.CONFIDENTIAL
                classification.masking_required = True
                classification.description = f"Contains {pii_type.upper()} information"
                break
        
        # Check sample values for PII patterns
        if not classification.pii_type:
            for value in sample_values:
                for pii_type, pattern in self.pii_patterns.items():
                    if re.match(pattern, str(value)):
                        classification.pii_type = pii_type
                        classification.privacy_level = PrivacyLevel.CONFIDENTIAL
                        classification.masking_required = True
                        classification.description = f"Contains {pii_type.upper()} information"
                        break
        
        # Apply industry-specific rules
        if field_name in self.config.get('sensitive_fields', []):
            classification.privacy_level = PrivacyLevel.RESTRICTED
            classification.masking_required = True
            classification.description = "Industry-specific sensitive field"
        
        return classification
    
    def apply_classification_to_glue_table(self, database: str, table: str, 
                                         classifications: List[FieldClassification]):
        """Apply classifications to a Glue table"""
        try:
            # Get current table
            table_response = self.glue_client.get_table(
                DatabaseName=database,
                Name=table
            )
            
            # Update table parameters with classifications
            parameters = table_response['Table'].get('Parameters', {})
            for classification in classifications:
                parameters[f'classification_{classification.field_name}'] = json.dumps({
                    'privacy_level': classification.privacy_level.value,
                    'pii_type': classification.pii_type,
                    'masking_required': classification.masking_required,
                    'description': classification.description
                })
            
            # Update table
            self.glue_client.update_table(
                DatabaseName=database,
                TableInput={
                    'Name': table,
                    'Parameters': parameters
                }
            )
            
        except Exception as e:
            print(f"Error applying classifications to Glue table: {str(e)}")
            raise

def main():
    # Example usage
    classifier = MetadataClassifier('configs/higher_ed_config.yaml')
    
    # Example field classification
    sample_values = ['3.85', '3.92', '4.00']
    classification = classifier.classify_field('student_gpa', sample_values)
    
    print(f"Field: {classification.field_name}")
    print(f"Privacy Level: {classification.privacy_level}")
    print(f"PII Type: {classification.pii_type}")
    print(f"Masking Required: {classification.masking_required}")
    print(f"Description: {classification.description}")

if __name__ == "__main__":
    main() 