```mermaid
graph TD
    subgraph "Data Sources & Ingestion"
        DS1[Raw Data Sources] --> S3R[S3 Raw Zone]
        DS2[RDS Databases] --> S3R
        S3R --> GLUE[AWS Glue ETL]
        GLUE --> S3C[S3 Curated Zone]
    end

    subgraph "Data Governance & Access Control"
        LF[Lake Formation]
        IAM[IAM Roles]
        GC[Glue Catalog]
        
        S3C --> LF
        LF --> GC
        IAM --> LF
        LF --> IAM
        
        subgraph "Access Control Flow"
            direction TB
            A1[User Request] --> A2[IAM Verification]
            A2 --> A3[Lake Formation Check]
            A3 --> A4[Apply RLS/Column Masking]
            A4 --> A5[Return Filtered Data]
        end
    end

    subgraph "Data Transformation"
        S3C --> DBT[dbt Models]
        DBT --> STG[Staging Layer]
        STG --> INT[Intermediate Layer]
        INT --> MART[Mart Layer]
    end

    subgraph "Analytics & Visualization"
        MART --> ATH[Athena]
        MART --> RS[Redshift]
        
        subgraph "Athena Access"
            direction TB
            ATH1[Query] --> ATH2[LF Check]
            ATH2 --> ATH3[Apply Security]
            ATH3 --> ATH4[Results]
        end
        
        subgraph "Redshift Access"
            direction TB
            RS1[Query] --> RS2[LF Check]
            RS2 --> RS3[Apply Security]
            RS3 --> RS4[Results]
        end
        
        ATH --> QS[QuickSight]
        RS --> QS
        
        subgraph "QuickSight Access"
            direction TB
            QS1[Dashboard] --> QS2[LF Check]
            QS2 --> QS3[Apply Security]
            QS3 --> QS4[View]
        end
    end

    subgraph "Data Quality & Monitoring"
        GE[Great Expectations] --> S3R
        GE --> S3C
        CW[CloudWatch] --> GLUE
        CW --> LF
        CW --> ATH
        CW --> RS
        CW --> QS
    end

    %% Styling
    classDef aws fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:white;
    classDef service fill:#232F3E,stroke:#FF9900,stroke-width:2px,color:white;
    classDef flow fill:#666666,stroke:#FF9900,stroke-width:1px,color:white;
    classDef storage fill:#232F3E,stroke:#FF9900,stroke-width:2px,color:white;
    
    class DS1,DS2,GLUE,LF,GC,ATH,RS,QS,CW aws;
    class IAM,GE,DBT service;
    class A1,A2,A3,A4,A5,ATH1,ATH2,ATH3,ATH4,RS1,RS2,RS3,RS4,QS1,QS2,QS3,QS4 flow;
    class S3R,S3C,STG,INT,MART storage;
```

## Architecture Components

### 1. Data Sources & Ingestion
- Raw data sources (CSV, JSON, etc.)
- RDS databases
- S3 Raw Zone for landing data
- AWS Glue ETL for data processing
- S3 Curated Zone for processed data

### 2. Data Governance & Access Control
- Lake Formation for centralized access control
- IAM roles for authentication
- Glue Catalog for metadata management
- Access control flow:
  1. User request
  2. IAM verification
  3. Lake Formation permission check
  4. Apply row-level security/column masking
  5. Return filtered data

### 3. Data Transformation
- dbt models for data transformation
- Staging layer for raw data
- Intermediate layer for transformations
- Mart layer for analytics-ready data

### 4. Analytics & Visualization
- Athena for interactive SQL queries
- Redshift for data warehousing
- QuickSight for visualization
- Each service has its own access control flow

### 5. Data Quality & Monitoring
- Great Expectations for data quality
- CloudWatch for monitoring
- End-to-end observability

## Access Control Flow

### 1. User Authentication
- IAM roles define user permissions
- Lake Formation manages data access
- Consistent permission model across services

### 2. Data Access
- Row-level security filters data
- Column masking protects sensitive data
- Access policies are service-agnostic

### 3. Service-Specific Controls
- Athena: Query-level access control
- Redshift: Table and column-level security
- QuickSight: Dashboard and visualization access

### 4. Monitoring & Audit
- CloudWatch for real-time monitoring
- Access logs for audit trails
- Compliance reporting 
- Configurable per column 