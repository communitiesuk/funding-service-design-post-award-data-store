
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

    -- RAISE NOTICE 'Executing query: %', query;

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
    RAISE NOTICE 'UPDATED % ROWS', row_count;
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

    query := format(
        'UPDATE %I SET %I = anon.fake_city_in_country(''United Kingdom'') || '' Council'' WHERE %I IS NOT NULL',
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
BEGIN
    RAISE NOTICE 'Anonymising table: %, data_blob key: %, with random integer data adjusted by -% and +% percentages.', UPPER(table_name), UPPER(data_blob_key), negative_percentage, positive_percentage;

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
            to_jsonb(
                (data_blob->>%L)::INTEGER +
                FLOOR((data_blob->>%L)::INTEGER * ((random() * (%s - %s)) + %s) / 100)
            )
        ) WHERE data_blob->>%L IS NOT NULL',
        table_name, '{' || data_blob_key || '}', data_blob_key, data_blob_key, positive_percentage, negative_percentage, negative_percentage, data_blob_key
    );
    EXECUTE query;

    GET DIAGNOSTICS row_count = ROW_COUNT;
    RAISE NOTICE 'UPDATED % ROWS', row_count;
EXCEPTION WHEN unique_violation THEN
    RAISE NOTICE 'Unique violation error occurred during % update. Skipping conflicting values.', table_name;
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
BEGIN
    RAISE NOTICE 'Anonymising multiple DATA_BLOB keys in RISK_REGISTER table';

    SELECT COUNT(*) INTO pre_update_count FROM risk_register WHERE data_blob IS NOT NULL;
    RAISE NOTICE 'Number of rows to be updated: %', pre_update_count;

    BEGIN
        UPDATE risk_register
        SET data_blob = jsonb_set(
            jsonb_set(
                jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                data_blob,
                                '{full_desc}',
                                to_jsonb(anon.lorem_ipsum(words := 20))
                            ),
                            '{risk_name}',
                            to_jsonb(anon.lorem_ipsum(characters := 20))
                        ),
                        '{short_desc}',
                        to_jsonb(anon.lorem_ipsum(words := 6))
                    ),
                    '{mitigations}',
                    to_jsonb(anon.lorem_ipsum(words := 10))
                ),
                '{consequences}',
                to_jsonb(anon.lorem_ipsum(words := 5))
            ),
            '{risk_owner_role}',
            to_jsonb(anon.lorem_ipsum(words := 3))
        )
        WHERE data_blob IS NOT NULL;

        GET DIAGNOSTICS row_count = ROW_COUNT;
        RAISE NOTICE 'UPDATED % ROWS', row_count;
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'Unique violation error occurred during risk_register detailed descriptions update. Skipping conflicting values.';
    END;
END;
$$ LANGUAGE plpgsql;



-- PLACE_DETAIL TABLE: Anonymise Name, Email and Telephone in data_blob column
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
    PERFORM anonymize_with_lorem_ipsum('funding'::TEXT, 'data_blob'::TEXT, 'funding_source'::TEXT);   --- TAKES TOO LONG

    PERFORM anonymize_with_lorem_ipsum('funding_comment'::TEXT, 'data_blob'::TEXT, 'comment'::TEXT);
    PERFORM anonymize_with_lorem_ipsum('private_investment'::TEXT, 'data_blob'::TEXT, 'additional_comments'::TEXT);
    PERFORM anonymize_with_lorem_ipsum('programme_progress'::TEXT, 'data_blob'::TEXT, 'answer'::TEXT);

    PERFORM anonymize_postcode_in_column('project_dim', 'postcodes');

    PERFORM anonymize_postcode_in_data_blob('project_dim', 'locations');

    PERFORM anonymize_region('programme_dim', 'programme_name');
    PERFORM anonymize_region('organisation_dim', 'organisation_name');
    PERFORM anonymize_region('project_dim', 'project_name');

    PERFORM anonymize_int_value_with_percentage_range('outcome_data', 'amount', -20, 20);

    PERFORM anonymize_email_in_column('submission_dim', 'submitting_user_email');

    PERFORM anonymize_name_in_data_blob('submission_dim', 'sign_off_name');

    PERFORM anonymize_risk_register_table();

    PERFORM anonymize_place_detail_table();

END $$;
