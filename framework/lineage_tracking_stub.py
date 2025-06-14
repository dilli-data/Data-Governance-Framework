import boto3
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class LineageType(Enum):
    TABLE = "TABLE"
    JOB = "JOB"
    DATASET = "DATASET"

@dataclass
class LineageNode:
    id: str
    type: LineageType
    name: str
    description: Optional[str] = None
    properties: Optional[Dict] = None

@dataclass
class LineageEdge:
    source_id: str
    target_id: str
    edge_type: str
    properties: Optional[Dict] = None

class LineageTracker:
    def __init__(self):
        self.glue_client = boto3.client('glue')
        self.s3_client = boto3.client('s3')
        self.lineage_bucket = 'data-lineage-bucket'
        
    def track_table_lineage(self, 
                          source_table: str,
                          target_table: str,
                          job_name: str,
                          transformation_details: Dict):
        """Track lineage between source and target tables"""
        try:
            # Create lineage nodes
            source_node = LineageNode(
                id=f"table_{source_table}",
                type=LineageType.TABLE,
                name=source_table
            )
            
            target_node = LineageNode(
                id=f"table_{target_table}",
                type=LineageType.TABLE,
                name=target_table
            )
            
            job_node = LineageNode(
                id=f"job_{job_name}",
                type=LineageType.JOB,
                name=job_name,
                properties=transformation_details
            )
            
            # Create lineage edges
            edges = [
                LineageEdge(
                    source_id=source_node.id,
                    target_id=job_node.id,
                    edge_type="READ"
                ),
                LineageEdge(
                    source_id=job_node.id,
                    target_id=target_node.id,
                    edge_type="WRITE"
                )
            ]
            
            # Save lineage information
            self._save_lineage({
                'nodes': [source_node, target_node, job_node],
                'edges': edges,
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            print(f"Error tracking table lineage: {str(e)}")
            raise
    
    def track_dataset_lineage(self,
                            source_dataset: str,
                            target_dataset: str,
                            transformation_type: str,
                            properties: Dict):
        """Track lineage between datasets"""
        try:
            source_node = LineageNode(
                id=f"dataset_{source_dataset}",
                type=LineageType.DATASET,
                name=source_dataset
            )
            
            target_node = LineageNode(
                id=f"dataset_{target_dataset}",
                type=LineageType.DATASET,
                name=target_dataset
            )
            
            edge = LineageEdge(
                source_id=source_node.id,
                target_id=target_node.id,
                edge_type=transformation_type,
                properties=properties
            )
            
            self._save_lineage({
                'nodes': [source_node, target_node],
                'edges': [edge],
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            print(f"Error tracking dataset lineage: {str(e)}")
            raise
    
    def _save_lineage(self, lineage_data: Dict):
        """Save lineage information to S3"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            key = f"lineage/{timestamp}.json"
            
            self.s3_client.put_object(
                Bucket=self.lineage_bucket,
                Key=key,
                Body=json.dumps(lineage_data, indent=2)
            )
            
        except Exception as e:
            print(f"Error saving lineage data: {str(e)}")
            raise
    
    def get_lineage(self, entity_id: str) -> Dict:
        """Retrieve lineage information for an entity"""
        try:
            # List all lineage files
            response = self.s3_client.list_objects_v2(
                Bucket=self.lineage_bucket,
                Prefix='lineage/'
            )
            
            lineage_data = []
            for obj in response.get('Contents', []):
                file_content = self.s3_client.get_object(
                    Bucket=self.lineage_bucket,
                    Key=obj['Key']
                )
                
                data = json.loads(file_content['Body'].read())
                
                # Filter for relevant nodes and edges
                relevant_nodes = [
                    node for node in data['nodes']
                    if node['id'] == entity_id or
                    any(edge['source_id'] == entity_id or edge['target_id'] == entity_id
                        for edge in data['edges'])
                ]
                
                relevant_edges = [
                    edge for edge in data['edges']
                    if edge['source_id'] == entity_id or edge['target_id'] == entity_id
                ]
                
                if relevant_nodes or relevant_edges:
                    lineage_data.append({
                        'nodes': relevant_nodes,
                        'edges': relevant_edges,
                        'timestamp': data['timestamp']
                    })
            
            return {
                'entity_id': entity_id,
                'lineage': lineage_data
            }
            
        except Exception as e:
            print(f"Error retrieving lineage data: {str(e)}")
            raise

def main():
    # Example usage
    tracker = LineageTracker()
    
    # Track table lineage
    tracker.track_table_lineage(
        source_table='raw_student_records',
        target_table='curated_student_records',
        job_name='student_records_etl',
        transformation_details={
            'transformation_type': 'ETL',
            'columns_transformed': ['gpa', 'enrollment_status'],
            'quality_checks_applied': True
        }
    )
    
    # Track dataset lineage
    tracker.track_dataset_lineage(
        source_dataset='student_enrollment',
        target_dataset='student_analytics',
        transformation_type='AGGREGATION',
        properties={
            'aggregation_type': 'AVG',
            'group_by': ['department', 'semester'],
            'metrics': ['gpa']
        }
    )
    
    # Retrieve lineage
    lineage = tracker.get_lineage('table_curated_student_records')
    print(json.dumps(lineage, indent=2))

if __name__ == "__main__":
    main() 