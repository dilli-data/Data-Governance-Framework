# Higher Education Analytics dbt Project

This dbt project transforms student records data from AWS S3/Glue Catalog into analytics-ready models.

## Project Structure

```
models/
├── staging/
│   └── stg_student_records.sql      # Initial staging of raw student records
├── intermediate/
│   └── int_department_metrics.sql   # Department-level aggregations
└── marts/
    └── mart_student_analytics.sql   # Final analytics-ready model
```

## Models

### Staging
- `stg_student_records`: Initial staging of raw student records with basic transformations

### Intermediate
- `int_department_metrics`: Department-level metrics including:
  - Total students
  - Average GPA
  - Min/Max GPA
  - Active/Graduated student counts

### Marts
- `mart_student_analytics`: Final analytics-ready model with:
  - Student information
  - Department metrics
  - GPA performance indicators

## Data Tests

The project includes several data quality tests:
- Uniqueness of student_id
- Not-null checks on required fields
- GPA range validation (0.0 to 4.0)
- Enrollment status validation
- Email format validation

## Setup

1. Install dbt and required packages:
```bash
pip install dbt-athena
dbt deps
```

2. Configure your AWS credentials:
```bash
aws configure
```

3. Update `profiles.yml` with your AWS settings:
- S3 staging directory
- Region
- Work group
- Database name

4. Run the project:
```bash
# Run all models
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

## Dependencies

- dbt-athena
- dbt-utils
- AWS Athena
- AWS Glue Catalog
- AWS S3

## Notes

- The project uses AWS Athena as the query engine
- All models are materialized as tables in the marts schema
- Staging and intermediate models are materialized as views
- Data quality tests are run automatically during `dbt test` 