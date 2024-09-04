#!/bin/bash

SANITISED_DB_PATH="Sanitised-database.sql"
S3_BUCKET=""
LOCAL_DB_PASSWORD="password"
LOCAL_DB_USER="postgres"
LOCAL_DB_NAME="data_store"
DB_IMAGE="postgres:16.2"

# Function to list and select an AWS Vault profile
select_aws_vault_profile() {
    local prompt_message=$1
    local profile_variable=$2
    local allowed_profile=$3

    while true; do
        echo "$prompt_message"
        PS3='Please select a profile (or Ctrl-C to quit): '
        IFS=$'\n' read -r -d '' -a profiles <<< "$(aws-vault list --profiles)"
        select profile in "${profiles[@]}"; do
            if [[ -n "$profile" ]]; then
                ACCOUNT=$(aws-vault exec "$profile" -- aws sts get-caller-identity --query 'Account' --output text)
                if [[ "$allowed_profile" == "prod" && ! "$ACCOUNT" =~ ^233 ]]; then
                    echo "You must select a production profile. Please try again."
                elif [[ "$allowed_profile" == "non_prod" && "$ACCOUNT" =~ ^233 ]]; then
                    echo "Production profile is not allowed. Please select a non-production profile."
                else
                    export "$profile_variable"="$profile"
                    return
                fi
            else
                echo "Invalid selection, please try again."
            fi
        done
    done
}

# Step 1: Select AWS Vault profile for prod
select_aws_vault_profile "Select the AWS Vault profile for the PROD env to load sanitised database:" AWS_VAULT_PROD_PROFILE "prod"
echo "You will use the ${AWS_VAULT_PROD_PROFILE} aws-vault profile for downloading the sanitised database. Ctrl-C now if this is wrong..."
sleep 5

get_S3_bucket_and_object(){

  # List all S3 buckets and get their names
  bucket_names=$(aws-vault exec $AWS_VAULT_PROD_PROFILE -- aws s3api list-buckets --query "Buckets[].Name" --output json)

  for bucket in $(echo "$bucket_names" | jq -r '.[]'); do
      TARGET_BUCKET=$(aws-vault exec $AWS_VAULT_PROD_PROFILE -- aws s3api get-bucket-tagging --bucket "$bucket")
      SANITISE_BUCKET=$(echo "$TARGET_BUCKET" | jq -r '.TagSet[] | select(.Key == "sanitise" and .Value == "db")')

      if [ -n "$SANITISE_BUCKET" ];
      then
          S3_BUCKET="$bucket"
          break
      fi
  done

  # Step 2: Download the file from S3 to a temporary location
  echo "Downloading the backup file from S3..."
  aws-vault exec $AWS_VAULT_PROD_PROFILE aws s3 cp s3://$S3_BUCKET/$SANITISED_DB_PATH $SANITISED_DB_PATH || { echo "Failed to download the backup file"; exit 1; }
  echo "${SANITISED_DB_PATH} file is ready to restore"

}

get_S3_bucket_and_object

read -p "Do you want to restore the database locally? (y/n): " RESTORE_DB

if [[ "$RESTORE_DB" == "y" || "$RESTORE_DB" == "Y" ]]; then

  echo "Restoring the database locally..."
  DB_CONTAINER_NAME=$(docker ps --filter "ancestor=$DB_IMAGE" --format "{{.Names}}")
  docker exec -i "$DB_CONTAINER_NAME" bash -c "PGPASSWORD=$LOCAL_DB_PASSWORD pg_restore -U $LOCAL_DB_USER -d $LOCAL_DB_NAME -v --clean" < "$SANITISED_DB_PATH"
  echo "Successfully restored into the local db"

else

  echo "restoring on dev or test"
  select_aws_vault_profile "Select the AWS Vault profile for the DEV/TEST env to restore the database:" AWS_VAULT_PROFILE_DEV_TEST "non_prod"
  echo "You will use the ${AWS_VAULT_PROFILE_DEV_TEST} aws-vault profile for restoring the database. Ctrl-C now if this is wrong..."
  sleep 5

  TARGET_CLUSTER=$(
    aws-vault exec $AWS_VAULT_PROFILE_DEV_TEST -- \
    aws rds describe-db-clusters \
    | jq '.DBClusters[] | select(.TagList[] | select(.Key == "aws:cloudformation:logical-id" and .Value == "postawardclusterDBCluster"))'
  )

  REMOTE_RESTORE_DB_PORT=5432
  LOCAL_RESTORE_DB_PORT=1437
  DB_TO_RESTORE_HOST=$(echo $TARGET_CLUSTER | jq -r '.Endpoint')
  DB_TO_RESTORE_SECRET=$(aws-vault exec $AWS_VAULT_PROFILE_DEV_TEST -- aws secretsmanager list-secrets | jq '.SecretList[] | select(.Tags[] | select(.Key == "aws:cloudformation:logical-id" and .Value == "postawardclusterAuroraSecret"))')
  DB_TO_RESTORE_PASSWORD=$(aws-vault exec $AWS_VAULT_PROFILE_DEV_TEST -- aws secretsmanager get-secret-value --secret-id $(echo $DB_TO_RESTORE_SECRET | jq -r '.Name') | jq -r '.SecretString' | jq -r '.password')
  DB_TO_RESTORE_URI="postgresql://postgres:${DB_TO_RESTORE_PASSWORD}@localhost:${LOCAL_RESTORE_DB_PORT}/post_award"

  trap 'unset DB_TO_RESTORE_PASSWORD' EXIT INT TERM

  # Connect to the bastion so that we can reach the DB
  BASTION_INSTANCE_ID=$(
    aws-vault exec $AWS_VAULT_PROFILE_DEV_TEST -- \
    aws ec2 describe-instances \
    --filters Name=tag:Name,Values="*-bastion" "Name=instance-state-name,Values='running'" \
    --query "Reservations[*].Instances[*].InstanceId" \
    | jq -r '.[0][0]'
  )

  aws-vault exec $AWS_VAULT_PROFILE_DEV_TEST -- \
    aws ssm start-session \
    --target $BASTION_INSTANCE_ID \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters host="$DB_TO_RESTORE_HOST",portNumber="$REMOTE_RESTORE_DB_PORT",localPortNumber="$LOCAL_RESTORE_DB_PORT" &

  BASTION_SESSION_ID=$!
  trap 'kill $BASTION_SESSION_ID' EXIT INT TERM
  sleep 10;

  # Step 3: Restore the database from the downloaded file
  echo "Restoring the database from the backup file..."
  pg_restore -d $DB_TO_RESTORE_URI -v --clean $SANITISED_DB_PATH || { echo "Failed to restore the database"; exit 1; }

fi

# Step 4: Clean up temporary file
echo "Cleaning up temporary files..."
rm -rf $SANITISED_DB_PATH || { echo "Failed to remove temporary file"; }

echo "Database restored successfully"
