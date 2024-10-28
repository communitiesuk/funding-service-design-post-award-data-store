-- Updating project start/end dates for Heritage Assets project as previously start date was later than end date
UPDATE
    project_progress pp
SET
    start_date = '2023-10-22 00:00:00',
    end_date = '2024-09-24 00:00:00'
FROM
    project_dim pd
    JOIN programme_junction pj ON pd.programme_junction_id = pj.id
    JOIN submission_dim sd ON pj.submission_id = sd.id
WHERE
    pp.project_id = pd.id
    AND sd.submission_id = 'S-R02-117'
    AND pd.project_name = 'Heritage Assets'
    AND pp.start_date = '2022-10-22 00:00:00'
    AND pp.end_date = '2022-09-23 00:00:00';
