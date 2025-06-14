with source as (
    select * from {{ source('higher_ed_data', 'student_records') }}
),

renamed as (
    select
        student_id,
        first_name,
        last_name,
        email,
        date_of_birth,
        ssn,
        gpa,
        enrollment_status,
        department,
        major,
        enrollment_date,
        graduation_date,
        -- Add any additional transformations here
        current_timestamp as dbt_updated_at
    from source
)

select * from renamed 