with student_records as (
    select * from {{ ref('stg_student_records') }}
),

department_metrics as (
    select * from {{ ref('int_department_metrics') }}
),

student_analytics as (
    select
        s.student_id,
        s.first_name,
        s.last_name,
        s.department,
        s.major,
        s.gpa,
        s.enrollment_status,
        d.avg_gpa as department_avg_gpa,
        d.total_students as department_total_students,
        d.active_students as department_active_students,
        d.graduated_students as department_graduated_students,
        case
            when s.gpa >= d.avg_gpa then 'Above Average'
            else 'Below Average'
        end as gpa_performance,
        current_timestamp as dbt_updated_at
    from student_records s
    left join department_metrics d
        on s.department = d.department
)

select * from student_analytics 