import subprocess

from sqlalchemy import text

from data_store.db import db


def setup_sanitiser():
    db.session.execute(text("CREATE EXTENSION IF NOT EXISTS anon CASCADE;"))
    db.session.execute(text("ALTER DATABASE data_store SET session_preload_libraries = 'anon';"))
    db.session.execute(text("SELECT anon.init();"))


def create_sanitisation_functions():
    """Create anonymization functions in PostgreSQL."""
    db.session.execute(
        text("""
        CREATE OR REPLACE FUNCTION anonymize_name() RETURNS TEXT AS $$
        BEGIN
            RETURN anon.fake_first_name() || ' ' || anon.fake_last_name();
        END;
        $$ LANGUAGE plpgsql;
        """)
    )

    db.session.execute(
        text("""
        CREATE OR REPLACE FUNCTION anonymize_email() RETURNS TEXT AS $$
        BEGIN
            RETURN anon.fake_email();
        END;
        $$ LANGUAGE plpgsql;
        """)
    )

    db.session.execute(
        text("""
        CREATE OR REPLACE FUNCTION anonymize_telephone() RETURNS TEXT AS $$
        BEGIN
            RETURN anon.random_phone('+44');
        END;
        $$ LANGUAGE plpgsql;
        """)
    )

    db.session.execute(
        text("""
        CREATE OR REPLACE FUNCTION anonymize_organization() RETURNS TEXT AS $$
        BEGIN
         RETURN anon.fake_company();
        END;
        $$ Language plpgsql;
        """)
    )

    db.session.execute(
        text("""
        CREATE or REPLACE FUNCTION anonymize_sign_off_name() RETURNS TEXT AS $$
        BEGIN
         RETURN anon.fake_first_name() || ' ' || anon.fake_last_name();
        END;
        $$
        Language plpgsql;
        """)
    )

    db.session.execute(
        text("""
        CREATE or REPLACE FUNCTION anonymize_post_Code() RETURNS TEXT[] AS $$
        DECLARE
         postcodes TEXT;
        BEGIN
         postcodes := ' SW' || ' ' || anon.fake_postcode();

         -- Return the postcode as a single-element array
         RETURN ARRAY[postcodes];
        END;
        $$
        Language plpgsql;
        """)
    )

    db.session.execute(
        text("""
        CREATE or REPLACE FUNCTION anonymize_progress_details() RETURNS TEXT AS $$
        BEGIN
         RETURN anon.random_string(20);
        END;
        $$
        Language plpgsql;
        """)
    )

    db.session.execute(
        text("""
        CREATE or REPLACE FUNCTION anonymize_risk_detail() RETURNS TEXT AS $$
        BEGIN
         RETURN anon.fake_first_name() || ' ' || anon.fake_last_name() || ' '|| 'Genral Manager';
        END;
        $$
        Language plpgsql;
        """)
    )


def apply_santisation():
    # Anonymize data
    db.session.execute(
        text("""
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
         WHERE data_blob->>'indicator' IN ('Name', 'Email', 'Telephone','Organisation Name') OR data_blob->>'question' ="Organisation name";
          """)
    )
    db.session.execute(
        text("""
         UPDATE submission_dim
            SET data_blob = jsonb_set(
                data_blob,
                '{sign_off_name}', --JSON path to the value to update
                to_jsonb(anonymize_sign_off_name())
            )
            WHERE data_blob->>'sign_off_name' IS NOT NULL;
            """)
    )

    db.session.execute(
        text("""
        UPDATE project_dim
        SET
        data_blob = jsonb_set(
            data_blob,
            '{locations}',
            to_jsonb(anonymize_post_Code())
        ),
        postcodes = anonymize_post_Code()
        WHERE data_blob->> 'locations' IS NOT NULL;
        """)
    )

    db.session.execute(
        text("""

       UPDATE programme_progress
       SET data_blob = jsonb_set(data_blob,'{answer}',to_jsonb(anonymize_progress_details()))
       WHERE data_blob->> 'answer' IS NOT NULL;
       """)
    )

    db.session.execute(
        text("""
        SECURITY LABEL FOR anon ON COLUMN programme_dim.programme_name
        IS 'MASKED WITH FUNCTION anon.fake_company()';
    """)
    )
    #
    db.session.execute(
        text("""
        SECURITY LABEL FOR anon ON COLUMN outcome_dim.outcome_category
        IS 'MASKED WITH FUNCTION anon.fake_company()';
    """)
    )
    #
    db.session.execute(
        text("""
      UPDATE risk_register
      SET
       data_blob = jsonb_set(
        jsonb_set(data_blob, '{risk_name}', to_jsonb(anon.fake_company())),
        '{risk_owner_role}', to_jsonb(anonymize_risk_detail()))
      WHERE data_blob IS NOT NULL;

        """)
    )
    db.session.execute(text("SELECT anon.anonymize_database();"))
    db.session.commit()


def dump_file():
    try:
        subprocess.run(
            [
                "pg_dump",
                "-U",
                "postgres",
                "-h",
                "localhost",
                "-p",
                "5432",
                "-F",
                "c",
                "-b",
                "-v",
                "-f",
                "anonomyize.sql",
                "data_store",
            ],
            check=True,
            capture_output=True,
        )
        print("Dump completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")


def db_sanitiser():
    setup_sanitiser()
    apply_santisation()
    dump_file()
