import subprocess

from sqlalchemy import text

from data_store.db import db


def anonymizer():
    db.session.execute(text("CREATE EXTENSION IF NOT EXISTS anon CASCADE;"))
    db.session.execute(text("ALTER DATABASE data_store SET session_preload_libraries = 'anon';"))
    db.session.execute(text("SELECT anon.init();"))

    db.session.execute(text("""
        CREATE OR REPLACE FUNCTION anonymize_name() RETURNS TEXT AS $$
        BEGIN
            RETURN anon.fake_first_name() || ' ' || anon.fake_last_name();
        END;
        $$ LANGUAGE plpgsql;
        """))

    db.session.execute(text("""
        CREATE OR REPLACE FUNCTION anonymize_email() RETURNS TEXT AS $$
        BEGIN
            RETURN anon.fake_email();
        END;
        $$ LANGUAGE plpgsql;
        """))

    db.session.execute(text("""
        CREATE OR REPLACE FUNCTION anonymize_telephone() RETURNS TEXT AS $$
        BEGIN
            RETURN anon.random_phone('+44');
        END;
        $$ LANGUAGE plpgsql;
        """))

    db.session.execute(text("""
        CREATE OR REPLACE FUNCTION anonymize_organization() RETURNS TEXT AS $$
        BEGIN 
         RETURN anon.fake_company();
        END;
        $$ Language plpgsql;      
    """))

    db.session.execute(text("""
        CREATE or REPLACE FUNCTION anonymize_sign_off_name() RETURNS TEXT AS $$
        BEGIN
         RETURN anon.fake_first_name() || ' ' || anon.fake_last_name();
        END;
        $$
        Language plpgsql;
        """))

    # Anonymize data
    db.session.execute(text("""
        UPDATE place_detail
         SET data_blob = jsonb_set(
             data_blob,
             '{answer}',  -- JSON path to the value to update
             CASE
                 WHEN data_blob->>'indicator' = 'Name' THEN to_jsonb(anonymize_name())
                 WHEN data_blob->>'indicator' = 'Email' THEN to_jsonb(anonymize_email())
                 WHEN data_blob->>'indicator' = 'Telephone' THEN to_jsonb(anonymize_telephone())
                 WHEN data_blob->>'indicator'= 'Organisation Name' THEN to_jsonb(anonymize_organization())
                 WHEN data_blob->>'question'= 'Organisation name' THEN to_jsonb(anonymize_organization())
                 ELSE data_blob->'answer'
             END
         )
         WHERE data_blob->>'indicator' IN ('Name', 'Email', 'Telephone','Organisation Name') OR data_blob->>'question' = 'Organisation name';
          """))
    db.session.execute(text("""
         UPDATE submission_dim
            SET data_blob = jsonb_set(
                data_blob,
                '{sign_off_name}', --JSON path to the value to update
                to_jsonb(anonymize_sign_off_name())
            )
            WHERE data_blob->>'sign_off_name' IS NOT NULL; 
            """))

    db.session.commit()

    # dump the file
    try:
        result = subprocess.run([
            'pg_dump',
            '-U', 'postgres',
            '-h', 'localhost',
            '-p', '5432',
            '-F', 'c',
            '-b',
            '-v',
            '-f', 'anonomyize.sql',
            'data_store'
        ], check=True, capture_output=True)
        print("Dump completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        print(f"stderr: {e.stderr.decode()}")
