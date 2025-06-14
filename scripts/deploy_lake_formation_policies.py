import boto3
import yaml
import json
import argparse
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LakeFormationPolicyDeployer:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.lake_formation = boto3.client('lakeformation')
        self.iam = boto3.client('iam')
        
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def create_database(self, database_config: Dict):
        """Create a database in Lake Formation"""
        try:
            self.lake_formation.create_database(
                DatabaseInput={
                    'Name': database_config['name'],
                    'Description': database_config.get('description', ''),
                    'LocationUri': database_config.get('location', '')
                }
            )
            logger.info(f"Created database: {database_config['name']}")
        except Exception as e:
            logger.error(f"Error creating database {database_config['name']}: {str(e)}")
            raise
    
    def grant_database_permissions(self, database_config: Dict):
        """Grant database-level permissions"""
        try:
            for permission in database_config.get('permissions', []):
                self.lake_formation.grant_permissions(
                    Principal={
                        'DataLakePrincipalIdentifier': f"arn:aws:iam::{self.iam.get_user()['User']['Arn'].split(':')[4]}:role/{permission['role']}"
                    },
                    Resource={
                        'Database': {
                            'Name': database_config['name']
                        }
                    },
                    Permissions=permission['access'].split(','),
                    PermissionsWithGrantOption=[]
                )
                logger.info(f"Granted {permission['access']} permissions on database {database_config['name']} to role {permission['role']}")
        except Exception as e:
            logger.error(f"Error granting database permissions: {str(e)}")
            raise
    
    def create_table_permissions(self, table_config: Dict):
        """Create table-level permissions"""
        try:
            for column in table_config.get('columns', []):
                for access in column.get('access', []):
                    self.lake_formation.grant_permissions(
                        Principal={
                            'DataLakePrincipalIdentifier': f"arn:aws:iam::{self.iam.get_user()['User']['Arn'].split(':')[4]}:role/{access['role']}"
                        },
                        Resource={
                            'Table': {
                                'DatabaseName': table_config['database'],
                                'Name': table_config['name'],
                                'TableWildcard': {}
                            }
                        },
                        Permissions=['SELECT'],
                        PermissionsWithGrantOption=[],
                        ColumnWildcard={
                            'ExcludedColumnNames': [col['name'] for col in table_config['columns'] if col['name'] != column['name']]
                        }
                    )
                    logger.info(f"Granted {access['level']} access on column {column['name']} to role {access['role']}")
        except Exception as e:
            logger.error(f"Error creating table permissions: {str(e)}")
            raise
    
    def create_row_filters(self, filter_config: Dict):
        """Create row-level filters"""
        try:
            for filter_def in filter_config:
                self.lake_formation.create_data_cells_filter(
                    TableData={
                        'DatabaseName': filter_def['tables'][0],
                        'TableName': filter_def['tables'][0],
                        'Name': filter_def['name'],
                        'RowFilter': {
                            'FilterExpression': filter_def['filter_expression']
                        }
                    }
                )
                
                for role in filter_def['roles']:
                    self.lake_formation.grant_permissions(
                        Principal={
                            'DataLakePrincipalIdentifier': f"arn:aws:iam::{self.iam.get_user()['User']['Arn'].split(':')[4]}:role/{role}"
                        },
                        Resource={
                            'Table': {
                                'DatabaseName': filter_def['tables'][0],
                                'Name': filter_def['tables'][0],
                                'TableWildcard': {}
                            }
                        },
                        Permissions=['SELECT'],
                        PermissionsWithGrantOption=[],
                        DataCellsFilter={
                            'DatabaseName': filter_def['tables'][0],
                            'TableName': filter_def['tables'][0],
                            'Name': filter_def['name']
                        }
                    )
                logger.info(f"Created row filter {filter_def['name']} for roles {filter_def['roles']}")
        except Exception as e:
            logger.error(f"Error creating row filters: {str(e)}")
            raise
    
    def create_column_filters(self, filter_config: Dict):
        """Create column-level filters"""
        try:
            for filter_def in filter_config:
                for column in filter_def['columns']:
                    for role in filter_def['roles']:
                        self.lake_formation.grant_permissions(
                            Principal={
                                'DataLakePrincipalIdentifier': f"arn:aws:iam::{self.iam.get_user()['User']['Arn'].split(':')[4]}:role/{role}"
                            },
                            Resource={
                                'Table': {
                                    'DatabaseName': self.config['settings']['default_database'],
                                    'Name': self.config['settings']['default_database'],
                                    'TableWildcard': {}
                                }
                            },
                            Permissions=['SELECT'],
                            PermissionsWithGrantOption=[],
                            ColumnWildcard={
                                'ExcludedColumnNames': [column]
                            }
                        )
                logger.info(f"Created column filter for columns {filter_def['columns']} for roles {filter_def['roles']}")
        except Exception as e:
            logger.error(f"Error creating column filters: {str(e)}")
            raise
    
    def deploy(self):
        """Deploy all Lake Formation policies"""
        try:
            # Create databases
            for database in self.config.get('databases', []):
                self.create_database(database)
                self.grant_database_permissions(database)
            
            # Create table permissions
            for table in self.config.get('tables', []):
                self.create_table_permissions(table)
            
            # Create row filters
            if 'row_filters' in self.config:
                self.create_row_filters(self.config['row_filters'])
            
            # Create column filters
            if 'column_filters' in self.config:
                self.create_column_filters(self.config['column_filters'])
            
            logger.info("Successfully deployed all Lake Formation policies")
            
        except Exception as e:
            logger.error(f"Error deploying Lake Formation policies: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Deploy Lake Formation policies')
    parser.add_argument('--config', required=True, help='Path to the policy configuration file')
    args = parser.parse_args()
    
    deployer = LakeFormationPolicyDeployer(args.config)
    deployer.deploy()

if __name__ == "__main__":
    main() 