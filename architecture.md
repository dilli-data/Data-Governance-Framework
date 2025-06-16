```mermaid
graph TD
    subgraph "Data Sources"
        S3[S3 Buckets]
        RDS[RDS Databases]
    end

    subgraph "Data Lake"
        LF[Lake Formation]
        GC[Glue Catalog]
        S3 --> LF
        RDS --> LF
        LF --> GC
    end

    subgraph "Access Control"
        IAM[IAM Roles]
        LF --> IAM
        IAM --> LF
    end

    subgraph "Analytics Services"
        A[Athena]
        R[Redshift]
        Q[QuickSight]
        
        subgraph "Athena Access Flow"
            A1[User Query] --> A2[Lake Formation Check]
            A2 --> A3[Apply RLS/Column Masking]
            A3 --> A4[Return Filtered Data]
        end
        
        subgraph "Redshift Access Flow"
            R1[User Query] --> R2[IAM Verification]
            R2 --> R3[Lake Formation Check]
            R3 --> R4[Apply RLS/Column Masking]
            R4 --> R5[Return Filtered Data]
        end
        
        subgraph "QuickSight Access Flow"
            Q1[User Access] --> Q2[IAM Verification]
            Q2 --> Q3[Lake Formation Check]
            Q3 --> Q4[Apply RLS/Column Masking]
            Q4 --> Q5[Show Filtered Dashboard]
        end
    end

    subgraph "Data Quality"
        GE[Great Expectations]
        GE --> S3
    end

    subgraph "Data Transformation"
        DBT[dbt]
        DBT --> R
    end

    %% Access Control Connections
    IAM --> A
    IAM --> R
    IAM --> Q
    
    %% Data Flow
    GC --> A
    GC --> R
    R --> Q
    A --> Q

    %% Styling
    classDef aws fill:#FF9900,stroke:#232F3E,stroke-width:2px,color:white;
    classDef service fill:#232F3E,stroke:#FF9900,stroke-width:2px,color:white;
    classDef flow fill:#666666,stroke:#FF9900,stroke-width:1px,color:white;
    
    class S3,RDS,LF,GC,A,R,Q aws;
    class IAM,GE,DBT service;
    class A1,A2,A3,A4,R1,R2,R3,R4,R5,Q1,Q2,Q3,Q4,Q5 flow;
```

## Access Control Flow Explanation

### 1. Athena Access Control
1. User submits a query through Athena
2. Query is intercepted by Lake Formation
3. Lake Formation checks:
   - User's IAM role
   - Table/column permissions
   - Row-level security policies
   - Column masking rules
4. If authorized, query proceeds with applied restrictions
5. Results are returned to user with appropriate data masking

### 2. Redshift Access Control
1. User connects to Redshift
2. Authentication through IAM role
3. Lake Formation checks permissions
4. Row-level security policies are applied
5. Column masking is enforced
6. Filtered data is returned to user

### 3. QuickSight Access Control
1. User accesses QuickSight dashboard
2. IAM role is verified
3. Lake Formation permissions are checked
4. Row-level security and column masking are applied
5. User sees only authorized data in dashboard

## Key Components

### Lake Formation
- Central access control point
- Manages permissions for all data access
- Enforces row-level security
- Applies column masking
- Integrates with IAM roles

### IAM Roles
- Defines user permissions
- Maps to Lake Formation access levels
- Controls service access
- Manages authentication

### Row-Level Security
- Filters data based on user attributes
- Applied at query time
- Consistent across all services
- Managed through Lake Formation

### Column Masking
- Protects sensitive data
- Applied dynamically
- Consistent across services
- Configurable per column 