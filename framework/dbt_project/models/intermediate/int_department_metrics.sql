with student_records as (
    select * from {{ ref('stg_student_records') }}
),

department_metrics as (
    select
        department,
        count(distinct student_id) as total_students,
        avg(gpa) as avg_gpa,
        min(gpa) as min_gpa,
        max(gpa) as max_gpa,
        count(case when enrollment_status = 'ACTIVE' then 1 end) as active_students,
        count(case when enrollment_status = 'GRADUATED' then 1 end) as graduated_students,
        current_timestamp as dbt_updated_at
    from student_records
    group by department
)

select * from department_metrics 