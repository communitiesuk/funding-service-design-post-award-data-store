
#!/bin/bash

usage() {
    echo "Usage: $0 [-h] [-e env]"
    echo "       -h for this message"
    echo "       -e env specify the environment (dev, test, or prod)"
    exit 1
}

# Default values
ENV=""

# Parse command-line options
while getopts "he:" opt; do
    case $opt in
        h)
            usage
            ;;
        e)
            ENV=$OPTARG
            ;;
        \?)
            usage
            ;;
    esac
done

# Check if environment argument was provided
if [ -z "$ENV" ]; then
    echo "Error: Environment argument required."
    usage
fi

# Validate environment argument
case "$ENV" in
    dev|test|prod)
        ;;
    *)
        echo "Error: Invalid environment. Choose 'dev', 'test', or 'prod'."
        usage
        ;;
esac

# Function to list and select an AWS Vault profile
select_aws_vault_profile() {
    local prompt_message=$1
    local profile_variable=$2

    echo "$prompt_message"
    PS3='Please select a profile (or Ctrl-C to quit): '
    IFS=$'\n' read -r -d '' -a profiles <<< "$(aws-vault list --profiles)"
    select profile in "${profiles[@]}"; do
        if [[ -n "$profile" ]]; then
            echo "Selected profile: $profile"
            export "$profile_variable"="$profile"
            break
        else
            echo "Invalid selection, please try again."
        fi
    done
}


# Prompt user for AWS profiles based on environment
case "$ENV" in
    dev)
        echo "You selected the development environment."
        select_aws_vault_profile "Select the AWS Vault profile for the development environment:" AWS_VAULT_DEV_PROFILE
        ;;
    test)
        echo "You selected the test environment."
        select_aws_vault_profile "Select the AWS Vault profile for the test environment:" AWS_VAULT_TEST_PROFILE
        ;;
    prod)
        echo "You selected the production environment."
        select_aws_vault_profile "Select the AWS Vault profile for the production environment:" AWS_VAULT_PROD_PROFILE
        ;;
esac


# Variables based on the environment
if [ "$ENV" == "dev" ]; then
    S3_BUCKET="sanitisation-db"
    TARGET_URL=""
elif [ "$ENV" == "test" ]; then
    S3_BUCKET="sanitisation-db"
    TARGET_URL=""
elif [ "$ENV" == "prod" ]; then
    S3_BUCKET="sanitisation-db"
    TARGET_URL=""
fi


# Variables
DB_NAME="post_award"
S3_BUCKET="sanitisation-db"
S3_PATH="backups/mydatabase_backup.dump"
TEMP_FILE="/tmp/mydatabase_backup.sql"



# Step 1: Clean the target database by dropping all tables
echo "Cleaning the target database..."
psql $TARGET_URL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" || { echo "Failed to clean the target database"; exit 1; }

# Step 2: Download the file from S3 to a temporary location
echo "Downloading the backup file from S3..."
aws s3 cp s3://$S3_BUCKET/$S3_PATH $TEMP_FILE --endpoint-url=http://localhost:4566 --quiet || { echo "Failed to download the backup file"; exit 1; }

# Step 3: Restore the database from the downloaded file
echo "Restoring the database from the backup file..."
pg_restore -d $TARGET_URL -v $TEMP_FILE || { echo "Failed to restore the database"; exit 1; }

# Step 4: Clean up temporary file
echo "Cleaning up temporary files..."
rm -f $TEMP_FILE || { echo "Failed to remove temporary file"; exit 1; }

echo "Database restored successfully."