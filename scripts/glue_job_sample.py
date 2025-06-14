import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *
import boto3
import json
import yaml

# Initialize Glue context
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'config_path'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Load configuration
def load_config(config_path):
    s3_client = boto3.client('s3')
    bucket = config_path.split('/')[2]
    key = '/'.join(config_path.split('/')[3:])
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return yaml.safe_load(response['Body'].read())

config = load_config(args['config_path'])

# Define schema for student records
student_schema = StructType([
    StructField("student_id", StringType(), False),
    StructField("first_name", StringType(), True),
    StructField("last_name", StringType(), True),
    StructField("email", StringType(), True),
    StructField("date_of_birth", StringType(), True),
    StructField("ssn", StringType(), True),
    StructField("gpa", DoubleType(), True),
    StructField("enrollment_status", StringType(), True),
    StructField("department", StringType(), True),
    StructField("major", StringType(), True),
    StructField("enrollment_date", StringType(), True),
    StructField("graduation_date", StringType(), True)
])

# Read raw data
raw_data = spark.read.format("csv") \
    .option("header", "true") \
    .schema(student_schema) \
    .load("s3://data-lake/raw/student_records/")

# Apply data quality rules
def apply_quality_rules(df, rules):
    for rule in rules:
        if rule['type'] == 'numeric':
            df = df.filter(
                (col(rule['field']).isNull() & lit(rule['null_allowed'])) |
                (col(rule['field']).isNotNull() & 
                 (col(rule['field']) >= rule['min_value']) & 
                 (col(rule['field']) <= rule['max_value']))
            )
        elif rule['type'] == 'categorical':
            df = df.filter(
                (col(rule['field']).isNull() & lit(rule['null_allowed'])) |
                (col(rule['field']).isNotNull() & 
                 col(rule['field']).isin(rule['allowed_values']))
            )
        elif rule['type'] == 'pattern':
            df = df.filter(
                (col(rule['field']).isNull() & lit(rule['null_allowed'])) |
                (col(rule['field']).isNotNull() & 
                 col(rule['field']).rlike(rule['pattern']))
            )
    return df

# Apply data quality rules
quality_rules = config['quality_rules']['student_records']
cleaned_data = apply_quality_rules(raw_data, quality_rules)

# Apply data masking
def mask_sensitive_data(df, masking_rules):
    for rule in masking_rules:
        if rule['masking_type'] == 'HASH':
            df = df.withColumn(
                rule['field'],
                sha2(col(rule['field']), 256)
            )
        elif rule['masking_type'] == 'MASK_ALL':
            df = df.withColumn(
                rule['field'],
                lit('********')
            )
    return df

# Apply data masking
masking_rules = config['masking_rules']
masked_data = mask_sensitive_data(cleaned_data, masking_rules)

# Add governance tags
def add_governance_tags(df, classification_rules):
    # Add PII tags
    for field in classification_rules['sensitive_fields']:
        if field in df.columns:
            df = df.withColumn(
                f"{field}_tag",
                lit("PII")
            )
    
    # Add data quality tags
    for rule in quality_rules:
        df = df.withColumn(
            f"{rule['field']}_quality_tag",
            when(
                (col(rule['field']).isNull() & lit(rule['null_allowed'])) |
                (col(rule['field']).isNotNull() & 
                 (col(rule['field']) >= rule.get('min_value', 0)) & 
                 (col(rule['field']) <= rule.get('max_value', 999999))),
                "PASS"
            ).otherwise("FAIL")
        )
    
    return df

# Add governance tags
tagged_data = add_governance_tags(masked_data, config['classification_rules'])

# Convert to DynamicFrame
dynamic_frame = DynamicFrame.fromDF(tagged_data, glueContext, "tagged_data")

# Write to curated zone with partitioning
glueContext.write_dynamic_frame.from_options(
    frame=dynamic_frame,
    connection_type="s3",
    connection_options={
        "path": "s3://data-lake/curated/student_records/",
        "partitionKeys": ["department", "enrollment_status"]
    },
    format="parquet"
)

# Track lineage
def track_lineage(source_table, target_table, transformation_details):
    lineage_tracker = boto3.client('lakeformation')
    lineage_tracker.create_data_cells_filter(
        TableData={
            'DatabaseName': config['settings']['default_database'],
            'TableName': target_table,
            'Name': f"{source_table}_to_{target_table}",
            'RowFilter': {
                'FilterExpression': transformation_details
            }
        }
    )

# Track lineage
track_lineage(
    'raw_student_records',
    'curated_student_records',
    json.dumps({
        'transformation_type': 'ETL',
        'quality_checks_applied': True,
        'masking_applied': True,
        'governance_tags_added': True
    })
)

job.commit() 