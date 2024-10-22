CREATE OR REPLACE FUNCTION anonymize_with_lorem_ipsum(
    table_name TEXT,
    column_name TEXT,
    data_blob_key TEXT
) RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    query TEXT;
    count_query TEXT;
    pre_update_count INTEGER;
    table_specific_condition TEXT := '';
BEGIN
    RAISE NOTICE 'Anonymising table: %, data_blob key: %, with lorem ipsum.', UPPER(table_name), UPPER(data_blob_key);

    IF table_name = 'project_progress' THEN
        table_specific_condition := ' AND start_date < end_date';  -- Apply this condition only for the 'project_progress' table
END IF;

    count_query := format(
        'SELECT COUNT(*) FROM %I WHERE %I->>%L IS NOT NULL %s',
        table_name, column_name, data_blob_key, table_specific_condition
    );
    EXECUTE count_query INTO pre_update_count;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    query := format(
        'UPDATE %I SET %I = jsonb_set(%I, %L, to_jsonb(anon.lorem_ipsum(characters := length(%I->>%L)))) WHERE %I->>%L IS NOT NULL %s',
        table_name, column_name, column_name, format('{%s}', data_blob_key), column_name, data_blob_key, column_name, data_blob_key, table_specific_condition
    );
    EXECUTE query;

    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'UPDATED % ROWS
    ', row_count;
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Unique violation error occurred during % update. Skipping conflicting values.
    ', table_name;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION anonymize_postcode_in_column(
    table_name TEXT,
    column_name TEXT
) RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    count_query TEXT;
    pre_update_count INTEGER;
BEGIN
    RAISE NOTICE 'Anonymising table: %, column: % with random postcode.', UPPER(table_name), UPPER(column_name);

    count_query := format(
        'SELECT COUNT(*) FROM %I WHERE %I IS NOT NULL',
        table_name, column_name
    );
    EXECUTE count_query INTO pre_update_count;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    EXECUTE format(
        'UPDATE %I SET %I = ARRAY[''SW1 '' || anon.random_zip()] WHERE %I IS NOT NULL',
        table_name, column_name, column_name
    );

    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'UPDATED % ROWS
    ', row_count;
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Unique violation error occurred during % update. Skipping conflicting values.
    ', table_name;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION anonymize_postcode_in_data_blob(
    table_name TEXT,
    data_blob_key TEXT
) RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    count_query TEXT;
    pre_update_count INTEGER;
BEGIN
    RAISE NOTICE 'Anonymising table: %, data_blob key: % with random postcode.', UPPER(table_name), UPPER(data_blob_key);

    count_query := format(
        'SELECT COUNT(*) FROM %I WHERE data_blob->>%L IS NOT NULL',
        table_name, data_blob_key
    );
    EXECUTE count_query INTO pre_update_count;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    EXECUTE format(
        'UPDATE %I SET data_blob = jsonb_set(data_blob, %L, to_jsonb(''SW2 '' || anon.random_zip())) WHERE data_blob->>%L IS NOT NULL',
        table_name, '{' || data_blob_key || '}', data_blob_key
    );

    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'UPDATED % ROWS
    ', row_count;
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Unique violation error occurred during % update. Skipping conflicting values.
    ', table_name;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION anonymize_region(
    table_name TEXT,
    column_name TEXT
) RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    query TEXT;
    count_query TEXT;
    pre_update_count INTEGER;
BEGIN
    RAISE NOTICE 'Anonymising table: %, column_name: %, with random region in the UK.', UPPER(table_name), UPPER(column_name);

    count_query := format(
        'SELECT COUNT(*) FROM %I WHERE %I IS NOT NULL',
        table_name, column_name
    );
    EXECUTE count_query INTO pre_update_count;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    query := format(
        'UPDATE %I SET %I = anon.fake_city_in_country(''United Kingdom'') || '' '' || INITCAP(LEFT(regexp_replace(md5(random()::text), ''[^A-Za-z]'', '''', ''g''), 8)) || '' Council'' WHERE %I IS NOT NULL',
        table_name, column_name, column_name
    );
    EXECUTE query;

    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'UPDATED % ROWS
    ', row_count;
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Unique violation error occurred during % update. Skipping conflicting values.
    ', table_name;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION anonymize_int_value_with_percentage_range(
    table_name TEXT,
    data_blob_key TEXT,
    negative_percentage NUMERIC,
    positive_percentage NUMERIC
) RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    query TEXT;
    count_query TEXT;
    pre_update_count INTEGER;
    table_specific_condition TEXT := '';
BEGIN
    RAISE NOTICE 'Anonymising table: %, data_blob key: %, with random integer data adjusted by -% and +% percentages.', UPPER(table_name), UPPER(data_blob_key), negative_percentage, positive_percentage;

    IF table_name = 'project_progress' THEN
        table_specific_condition := ' AND start_date < end_date';
END IF;
    count_query := format(
        'SELECT COUNT(*) FROM %I WHERE data_blob->>%L IS NOT NULL %s',
        table_name, data_blob_key, table_specific_condition
    );

    EXECUTE count_query INTO pre_update_count;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    query := format(
        'UPDATE %I SET data_blob = jsonb_set(
            data_blob,
            %L,
            to_jsonb(
                (data_blob->>%L)::INTEGER +
                FLOOR((data_blob->>%L)::INTEGER * ((random() * (%s - %s)) + %s) / 100)
            )
        ) WHERE data_blob->>%L ~ ''^[0-9]+$'' %s',
        table_name, '{' || data_blob_key || '}', data_blob_key, data_blob_key, positive_percentage, negative_percentage, negative_percentage, data_blob_key, table_specific_condition
    );
    EXECUTE query;

    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'UPDATED % ROWS
    ', row_count;
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Unique violation error occurred during % update. Skipping conflicting values.'
    , table_name;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION anonymize_email_in_column(
    table_name TEXT,
    column_name TEXT
) RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    count_query TEXT;
    pre_update_count INTEGER;
BEGIN
    RAISE NOTICE 'Anonymising table: %, column: % with random email.', UPPER(table_name), UPPER(column_name);

    count_query := format(
        'SELECT COUNT(*) FROM %I WHERE %I IS NOT NULL',
        table_name, column_name
    );
    EXECUTE count_query INTO pre_update_count;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    EXECUTE format(
        'UPDATE %I SET %I = anon.fake_email() WHERE %I IS NOT NULL',
        table_name, column_name, column_name
    );

    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'UPDATED % ROWS
    ', row_count;
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Unique violation error occurred during % update. Skipping conflicting values.
    ', table_name;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION anonymize_name_in_data_blob(
    table_name TEXT,
    data_blob_key TEXT
) RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    count_query TEXT;
    pre_update_count INTEGER;
    query TEXT;
BEGIN
    RAISE NOTICE 'Anonymising table: %, data_blob key: % with random name.', UPPER(table_name), UPPER(data_blob_key);

    count_query := format(
        'SELECT COUNT(*) FROM %I WHERE data_blob->>%L IS NOT NULL',
        table_name, data_blob_key
    );
    EXECUTE count_query INTO pre_update_count;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    query := format(
        'UPDATE %I SET data_blob = jsonb_set(data_blob, %L, to_jsonb(anon.fake_last_name() || '' '' || anon.fake_last_name())) WHERE data_blob->>%L IS NOT NULL',
        table_name, '{' || data_blob_key || '}', data_blob_key
    );
    EXECUTE query;

    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'UPDATED % ROWS
    ', row_count;
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Unique violation error occurred during % update. Skipping conflicting values.
    ', table_name;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION anonymize_risk_register_table() RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    pre_update_count INTEGER;
    new_values JSONB;
BEGIN
    RAISE NOTICE 'Anonymising multiple DATA_BLOB keys in RISK_REGISTER table';

    SELECT COUNT(*) INTO pre_update_count FROM risk_register WHERE data_blob IS NOT NULL;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    BEGIN
        new_values := jsonb_build_object(
            'full_desc', substring(anon.lorem_ipsum(words := 50) from 1 for 200),
            'risk_name', substring(anon.lorem_ipsum(words := 10) from 1 for 50),
            'short_desc', substring(anon.lorem_ipsum(words := 20) from 1 for 100),
            'mitigations', substring(anon.lorem_ipsum(words := 30) from 1 for 150),
            'consequences', substring(anon.lorem_ipsum(words := 30) from 1 for 150),
            'risk_owner_role', substring(anon.lorem_ipsum(words := 5) from 1 for 50)
        );

        UPDATE risk_register
        SET data_blob = data_blob || new_values
        WHERE data_blob IS NOT NULL;

        GET DIAGNOSTICS row_count = ROW_COUNT;
        RAISE NOTICE 'UPDATED % ROWS', row_count;
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'Unique violation error occurred during risk_register detailed descriptions update. Skipping conflicting values.';
    END;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION anonymize_place_detail_table() RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    pre_update_count INTEGER;
BEGIN
    RAISE NOTICE 'PLACE_DETAIL table: anonymising Name, Email and Telephone keys with fake data in DATA_BLOB column';

    SELECT COUNT(*) INTO pre_update_count FROM place_detail WHERE data_blob IS NOT NULL;
    RAISE NOTICE 'Number of rows to be checked: %', pre_update_count;

    BEGIN
        UPDATE place_detail
        SET data_blob = jsonb_set(
            data_blob,
            '{answer}',
            COALESCE(
                CASE
                    WHEN data_blob->>'indicator' = 'Name' THEN to_jsonb(anon.fake_last_name() || ' ' || anon.fake_last_name())
                    WHEN data_blob->>'indicator' IN ('Email', 'Contact email') THEN to_jsonb(anon.fake_email())
                    WHEN data_blob->>'indicator' = 'Telephone' THEN to_jsonb(anon.random_phone('+44'))
                    ELSE data_blob->'answer'
                END,
                data_blob->'answer'
            )
        )
        WHERE data_blob IS NOT NULL
        AND (data_blob->>'indicator' IN ('Name', 'Email', 'Contact email', 'Telephone'));

        GET DIAGNOSTICS row_count = ROW_COUNT;
        RAISE NOTICE 'UPDATED % ROWS', row_count;
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'Unique violation error occurred during place_detail update. Skipping conflicting values.';
    END;
END;
$$ LANGUAGE plpgsql;




DO $$
BEGIN
    PERFORM anonymize_with_lorem_ipsum('funding', 'data_blob', 'funding_source');
    PERFORM anonymize_with_lorem_ipsum('funding', 'data_blob', 'spend_type');

    PERFORM anonymize_with_lorem_ipsum('funding_comment', 'data_blob', 'comment');

    PERFORM anonymize_with_lorem_ipsum('funding_question', 'data_blob', 'question');
    PERFORM anonymize_with_lorem_ipsum('funding_question', 'data_blob', 'indicator');
    PERFORM anonymize_with_lorem_ipsum('funding_question', 'data_blob', 'response');
    PERFORM anonymize_with_lorem_ipsum('funding_question', 'data_blob', 'guidance_notes');

    PERFORM anonymize_int_value_with_percentage_range('outcome_data', 'amount', -20, 20);
    PERFORM anonymize_int_value_with_percentage_range('output_data', 'amount', -20, 20);
    PERFORM anonymize_with_lorem_ipsum('output_data', 'data_blob', 'additional_information');

    PERFORM anonymize_with_lorem_ipsum('private_investment', 'data_blob', 'additional_comments');
    PERFORM anonymize_int_value_with_percentage_range('private_investment', 'townsfund_funding', -20, 20);
    PERFORM anonymize_int_value_with_percentage_range('private_investment', 'total_project_value', -20, 20);

    PERFORM anonymize_with_lorem_ipsum('programme_funding_management', 'data_blob', 'payment_type');

    PERFORM anonymize_with_lorem_ipsum('programme_progress', 'data_blob', 'answer');

    PERFORM anonymize_with_lorem_ipsum('project_progress', 'data_blob', 'commentary');
    PERFORM anonymize_with_lorem_ipsum('project_progress', 'data_blob', 'important_milestone');
    PERFORM anonymize_with_lorem_ipsum('project_progress', 'data_blob', 'leading_factor_of_delay');
    PERFORM anonymize_with_lorem_ipsum('project_progress', 'data_blob', 'delivery_status');
    PERFORM anonymize_with_lorem_ipsum('project_progress', 'data_blob', 'delivery_stage');
    PERFORM anonymize_with_lorem_ipsum('project_progress', 'data_blob', 'adjustment_request_status');
    PERFORM anonymize_int_value_with_percentage_range('project_progress', 'risk_rag', -20, 20);
    PERFORM anonymize_int_value_with_percentage_range('project_progress', 'spend_rag', -20, 20);
    PERFORM anonymize_int_value_with_percentage_range('project_progress', 'delivery_rag', -20, 20);

    PERFORM anonymize_postcode_in_column('project_dim', 'postcodes');
    PERFORM anonymize_postcode_in_data_blob('project_dim', 'locations');

    PERFORM anonymize_with_lorem_ipsum('project_finance_change', 'data_blob', 'changes_made');
    PERFORM anonymize_with_lorem_ipsum('project_finance_change', 'data_blob', 'reasons_for_change');
    PERFORM anonymize_with_lorem_ipsum('project_finance_change', 'data_blob', 'project_funding_moved_to');
    PERFORM anonymize_with_lorem_ipsum('project_finance_change', 'data_blob', 'project_funding_moved_from');
    PERFORM anonymize_with_lorem_ipsum('project_finance_change', 'data_blob', 'intervention_theme_moved_to');
    PERFORM anonymize_with_lorem_ipsum('project_finance_change', 'data_blob', 'intervention_theme_moved_from');
    PERFORM anonymize_with_lorem_ipsum('project_finance_change', 'data_blob', 'reporting_period_change_takes_place');

    PERFORM anonymize_email_in_column('submission_dim', 'submitting_user_email');
    PERFORM anonymize_name_in_data_blob('submission_dim', 'sign_off_name');

    PERFORM anonymize_risk_register_table();

    PERFORM anonymize_place_detail_table();

END $$;
