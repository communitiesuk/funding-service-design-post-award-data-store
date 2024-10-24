CREATE OR REPLACE FUNCTION anonymise_with_lorem_ipsum(
    table_name TEXT,
    column_name TEXT,
    data_blob_key TEXT
) RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    query TEXT;
    count_query TEXT;
    pre_update_count INTEGER;
BEGIN
    RAISE NOTICE 'Anonymising table: %, data_blob key: %, with lorem ipsum.', UPPER(table_name), UPPER(data_blob_key);
    count_query := format(
        'SELECT COUNT(*) FROM %I WHERE %I->>%L IS NOT NULL',
        table_name, column_name, data_blob_key
    );
    EXECUTE count_query INTO pre_update_count;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    query := format(
        'UPDATE %I SET %I = jsonb_set(%I, %L, to_jsonb(anon.lorem_ipsum(characters := length(%I->>%L)))) WHERE %I->>%L IS NOT NULL',
        table_name, column_name, column_name, format('{%s}', data_blob_key), column_name, data_blob_key, column_name, data_blob_key
    );
    EXECUTE query;
    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'UPDATED % ROWS', row_count;
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Unique violation error occurred during % update. Skipping conflicting values.', table_name;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION anonymise_column_with_lorem_ipsum(
    table_name TEXT,
    column_name TEXT
) RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
BEGIN
    RAISE NOTICE 'Anonymising column "%" in table "%".', column_name, table_name;

    EXECUTE format(
        'UPDATE %I SET %I = (anon.lorem_ipsum(characters := 30) || ''-'' || gen_random_uuid()) WHERE %I IS NOT NULL',
        table_name, column_name, column_name
    );

    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'Updated % rows in column "%".', row_count, column_name;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION anonymise_postcode_in_column(
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



CREATE OR REPLACE FUNCTION anonymise_postcode_in_data_blob(
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



CREATE OR REPLACE FUNCTION anonymise_region(
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



CREATE OR REPLACE FUNCTION anonymise_int_value_with_random_range(
    table_name TEXT,
    data_blob_key TEXT,
    start_int INTEGER,
    end_int INTEGER
) RETURNS VOID AS $$
DECLARE
    row_count INTEGER;
    query TEXT;
    count_query TEXT;
    pre_update_count INTEGER;
BEGIN
    RAISE NOTICE 'Anonymising table: %, data_blob key: %, with random integer between % and %.', UPPER(table_name), UPPER(data_blob_key), start_int, end_int;

    count_query := format(
        'SELECT COUNT(*) FROM %I WHERE data_blob->>%L IS NOT NULL',
        table_name, data_blob_key
    );
    EXECUTE count_query INTO pre_update_count;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    query := format(
        'UPDATE %I SET data_blob = jsonb_set(
            data_blob,
            %L,
            to_jsonb(anon.random_int_between(%s, %s))
        ) WHERE data_blob->>%L ~ ''^[0-9]+$''',
        table_name, '{' || data_blob_key || '}', start_int, end_int, data_blob_key
    );
    EXECUTE query;

    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'UPDATED % ROWS', row_count;

EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Unique violation error occurred during % update. Skipping conflicting values.', table_name;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION anonymise_email_in_column(
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



CREATE OR REPLACE FUNCTION anonymise_name_in_data_blob(
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



CREATE OR REPLACE FUNCTION anonymise_risk_register_table() RETURNS VOID AS $$
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



CREATE OR REPLACE FUNCTION anonymise_place_detail_table() RETURNS VOID AS $$
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
    PERFORM anonymise_with_lorem_ipsum('funding', 'data_blob', 'state');
    PERFORM anonymise_with_lorem_ipsum('funding', 'data_blob', 'funding_source');
    PERFORM anonymise_with_lorem_ipsum('funding', 'data_blob', 'spend_type');
    PERFORM anonymise_with_lorem_ipsum('funding', 'data_blob', 'funding_source');
    PERFORM anonymise_with_lorem_ipsum('funding', 'data_blob', 'funding_category');
    PERFORM anonymise_with_lorem_ipsum('funding', 'data_blob', 'secured');
    PERFORM anonymise_int_value_with_random_range('funding', 'spend_for_reporting_period', 100, 2000000);

    PERFORM anonymise_with_lorem_ipsum('funding_comment', 'data_blob', 'comment');

    PERFORM anonymise_with_lorem_ipsum('funding_question', 'data_blob', 'question');
    PERFORM anonymise_with_lorem_ipsum('funding_question', 'data_blob', 'indicator');
    PERFORM anonymise_with_lorem_ipsum('funding_question', 'data_blob', 'response');
    PERFORM anonymise_with_lorem_ipsum('funding_question', 'data_blob', 'guidance_notes');

    PERFORM anonymise_with_lorem_ipsum('outcome_data', 'data_blob', 'state');
    PERFORM anonymise_with_lorem_ipsum('outcome_data', 'data_blob', 'higher_frequency');
    PERFORM anonymise_with_lorem_ipsum('outcome_data', 'data_blob', 'geography_indicator');
    PERFORM anonymise_with_lorem_ipsum('outcome_data', 'data_blob', 'unit_of_measurement');
    PERFORM anonymise_int_value_with_random_range('outcome_data', 'amount', 100, 2000000);


    PERFORM anonymise_column_with_lorem_ipsum('outcome_dim','outcome_name');

    PERFORM anonymise_with_lorem_ipsum('output_data', 'data_blob', 'state');
    PERFORM anonymise_with_lorem_ipsum('output_data', 'data_blob', 'unit_of_measurement');
    PERFORM anonymise_int_value_with_random_range('output_data', 'amount', 100, 2000000);
    PERFORM anonymise_with_lorem_ipsum('output_data', 'data_blob', 'additional_information');

    PERFORM anonymise_column_with_lorem_ipsum('output_dim','output_name');

    PERFORM anonymise_with_lorem_ipsum('private_investment', 'data_blob', 'additional_comments');
    PERFORM anonymise_int_value_with_random_range('private_investment', 'townsfund_funding', 100, 2000000);
    PERFORM anonymise_int_value_with_random_range('private_investment', 'total_project_value', 100, 2000000);
    PERFORM anonymise_int_value_with_random_range('private_investment', 'private_sector_funding_secured', 100, 2000000);
    PERFORM anonymise_int_value_with_random_range('private_investment', 'private_sector_funding_required', 100, 2000000);
--
    PERFORM anonymise_with_lorem_ipsum('programme_funding_management', 'data_blob', 'state');
    PERFORM anonymise_with_lorem_ipsum('programme_funding_management', 'data_blob', 'payment_type');
    PERFORM anonymise_int_value_with_random_range('programme_funding_management', 'spend_for_reporting_period', 100, 2000000);

    PERFORM anonymise_with_lorem_ipsum('programme_progress', 'data_blob', 'answer');
    PERFORM anonymise_with_lorem_ipsum('programme_progress', 'data_blob', 'question');

    PERFORM anonymise_postcode_in_column('project_dim', 'postcodes');
    PERFORM anonymise_postcode_in_data_blob('project_dim', 'locations');
    PERFORM anonymise_with_lorem_ipsum('project_dim', 'data_blob', 'gis_provided');
    PERFORM anonymise_with_lorem_ipsum('project_dim', 'data_blob', 'location_multiplicity');
    PERFORM anonymise_with_lorem_ipsum('project_dim', 'data_blob', 'primary_intervention_theme');

    PERFORM anonymise_with_lorem_ipsum('project_progress', 'data_blob', 'commentary');
    PERFORM anonymise_with_lorem_ipsum('project_progress', 'data_blob', 'important_milestone');
    PERFORM anonymise_with_lorem_ipsum('project_progress', 'data_blob', 'leading_factor_of_delay');
    PERFORM anonymise_with_lorem_ipsum('project_progress', 'data_blob', 'delivery_status');
    PERFORM anonymise_with_lorem_ipsum('project_progress', 'data_blob', 'delivery_stage');
    PERFORM anonymise_with_lorem_ipsum('project_progress', 'data_blob', 'adjustment_request_status');
    PERFORM anonymise_int_value_with_random_range('project_progress', 'risk_rag', 1, 5);
    PERFORM anonymise_int_value_with_random_range('project_progress', 'spend_rag', 1, 5);
    PERFORM anonymise_int_value_with_random_range('project_progress', 'delivery_rag', 1, 5);

    PERFORM anonymise_with_lorem_ipsum('project_finance_change', 'data_blob', 'state');
    PERFORM anonymise_int_value_with_random_range('project_finance_change', 'amount_moved', 100, 2000000);
    PERFORM anonymise_with_lorem_ipsum('project_finance_change', 'data_blob', 'changes_made');
    PERFORM anonymise_with_lorem_ipsum('project_finance_change', 'data_blob', 'reasons_for_change');
    PERFORM anonymise_with_lorem_ipsum('project_finance_change', 'data_blob', 'project_funding_moved_to');
    PERFORM anonymise_with_lorem_ipsum('project_finance_change', 'data_blob', 'project_funding_moved_from');
    PERFORM anonymise_with_lorem_ipsum('project_finance_change', 'data_blob', 'intervention_theme_moved_to');
    PERFORM anonymise_with_lorem_ipsum('project_finance_change', 'data_blob', 'intervention_theme_moved_from');
    PERFORM anonymise_with_lorem_ipsum('project_finance_change', 'data_blob', 'reporting_period_change_takes_place');

    PERFORM anonymise_email_in_column('submission_dim', 'submitting_user_email');
    PERFORM anonymise_name_in_data_blob('submission_dim', 'sign_off_name');

    PERFORM anonymise_risk_register_table();

    PERFORM anonymise_place_detail_table();

END $$;
