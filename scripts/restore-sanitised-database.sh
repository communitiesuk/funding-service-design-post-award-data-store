#!/bin/bash

usage() {
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  --restore-to-local-db     Restore the database locally."
    echo "  --restore-to-dev/test     Restore the database in the dev or test environment, depending on the AWS profile you choose."
    echo
    echo "Examples:"
    echo "  $0 --restore-to-local-db"
    echo "    This will restore the database on your local machine."
    echo
    echo "  $0 --restore-to-dev/test"
    echo "    This will restore the database in the dev or test environment."
    exit 1
}

if [[ $1 == "--help" || $1 == "-h" ]]; then
    usage
fi

if [[ -z $1 || ($1 != "--restore-to-local-db" && $1 != "--restore-to-dev/test") ]]; then
    echo "Error: Invalid option."
    usage
fi

SANITISED_DB_PATH="Sanitised-database.sql"
S3_BUCKET="fs-sanitised-database-dumps-prod"
LOCAL_DB_PASSWORD="password"
LOCAL_DB_USER="postgres"
LOCAL_DB_NAME="data_store"
DB_IMAGE="postgres:16.2"

# Function to list and select an AWS Vault profile
select_aws_vault_profile() {
    local prompt_message=$1
    local profile_variable=$2

    while true; do
        echo "$prompt_message"
        PS3='Please select a profile (or Ctrl-C to quit): '
        IFS=$'\n' read -r -d '' -a profiles <<< "$(aws-vault list --profiles)"
        select profile in "${profiles[@]}"; do
            if [[ -n "$profile" ]]; then
                ACCOUNT=$(aws-vault exec "$profile" -- aws sts get-caller-identity --query 'Account' --output text)
                if [[ "$ACCOUNT" =~ ^233 ]]; then
                    echo "You must not select a production profile. Please try again."
                    exit
                fi
            fi
            export "$profile_variable"="$profile"
            return
      done
    done
}

# Step 1: Select AWS Vault profile
select_aws_vault_profile "Select the AWS Vault profile for the account you want to restore to: " AWS_VAULT_PROFILE
echo "You will use the ${AWS_VAULT_PROFILE} aws-vault profile for downloading the sanitised database. Ctrl-C now if this is wrong..."
sleep 5


# Step 2: Download the file from S3 to a temporary location
echo "Downloading the backup file from S3..."
aws-vault exec $AWS_VAULT_PROFILE -- aws s3 cp s3://$S3_BUCKET/$SANITISED_DB_PATH /tmp/$SANITISED_DB_PATH || { echo "Failed to download the backup file"; exit 1; }
echo "${SANITISED_DB_PATH} file is ready to restore"


if [[ $1 == "--restore-to-local-db" ]]; then

  echo "Restoring the database locally..."
  DB_CONTAINER_NAME=$(docker ps --filter "ancestor=$DB_IMAGE" --format "{{.Names}}")
  docker exec -i "$DB_CONTAINER_NAME" bash -c "PGPASSWORD=$LOCAL_DB_PASSWORD pg_restore -U $LOCAL_DB_USER -d $LOCAL_DB_NAME -v --clean" < "/tmp/$SANITISED_DB_PATH"
  echo "Successfully restored into the local db"

elif [[ $1 == "--restore-to-dev/test" ]]; then

  TARGET_CLUSTER=$(
    aws-vault exec $AWS_VAULT_PROFILE -- \
    aws rds describe-db-clusters \
    | jq '.DBClusters[] | select(.TagList[] | select(.Key == "aws:cloudformation:logical-id" and .Value == "postawardclusterDBCluster"))'
  )

  REMOTE_RESTORE_DB_PORT=5432
  LOCAL_RESTORE_DB_PORT=1437
  DB_TO_RESTORE_HOST=$(echo $TARGET_CLUSTER | jq -r '.Endpoint')
  DB_TO_RESTORE_SECRET=$(aws-vault exec $AWS_VAULT_PROFILE -- aws secretsmanager list-secrets | jq '.SecretList[] | select(.Tags[] | select(.Key == "aws:cloudformation:logical-id" and .Value == "postawardclusterAuroraSecret"))')
  DB_TO_RESTORE_PASSWORD=$(aws-vault exec $AWS_VAULT_PROFILE -- aws secretsmanager get-secret-value --secret-id $(echo $DB_TO_RESTORE_SECRET | jq -r '.Name') | jq -r '.SecretString' | jq -r '.password')
  DB_TO_RESTORE_URI="postgresql://postgres:${DB_TO_RESTORE_PASSWORD}@localhost:${LOCAL_RESTORE_DB_PORT}/post_award"

  trap 'unset DB_TO_RESTORE_PASSWORD' EXIT INT TERM

  # Connect to the bastion so that we can reach the DB
  BASTION_INSTANCE_ID=$(
    aws-vault exec $AWS_VAULT_PROFILE -- \
    aws ec2 describe-instances \
    --filters Name=tag:Name,Values="*-bastion" "Name=instance-state-name,Values='running'" \
    --query "Reservations[*].Instances[*].InstanceId" \
    | jq -r '.[0][0]'
  )

  aws-vault exec $AWS_VAULT_PROFILE -- \
    aws ssm start-session \
    --target $BASTION_INSTANCE_ID \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters host="$DB_TO_RESTORE_HOST",portNumber="$REMOTE_RESTORE_DB_PORT",localPortNumber="$LOCAL_RESTORE_DB_PORT" &

  BASTION_SESSION_ID=$!
  trap 'kill $BASTION_SESSION_ID' EXIT INT TERM
  sleep 10;

  # Step 3: Restore the database from the downloaded file
  echo "Restoring the database from the backup file..."
  pg_restore -d $DB_TO_RESTORE_URI -v --clean /tmp/$SANITISED_DB_PATH || { echo "Failed to restore the database"; exit 1; }

fi

# Step 4: Clean up temporary file
echo "Cleaning up temporary files..."
rm /tmp/$SANITISED_DB_PATH || { echo "Failed to remove temporary file"; }

echo "Database restored successfully"
