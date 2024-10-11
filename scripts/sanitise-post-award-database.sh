#!/bin/bash

usage() {
    echo "Usage: $0 SANITISE_DB_NAME SANITISE_PATH "
    echo
    echo "Arguments:"
    echo "  SANITISE_DB_NAME (string) Name of the sanitised database "
    echo "  SANITISE_PATH   (string) Name of the file "
    echo
    echo "Example:"
    echo "  $0 \"custom-db-name\""
    echo "  This sets custom values for all arguments."
    echo "  $0 \"\""
    echo "  This uses default values for all arguments."
    exit 1
}

## Check if help was requested
if [[ $1 == "--help" || $1 == "-h" ]]; then
    usage
fi

version=$(psql --version | awk '{print $3}' | cut -d. -f1)

echo "psql version you have is: ${version}"

if [ "$version" -lt 16 ]; then
    echo "You need psql (Postgresql) version 16 or greater to run this script."
    exit 1
fi

# Function to list and select an AWS Vault profile
select_aws_vault_profile() {
    local prompt_message=$1
    local profile_variable=$2

    echo "$prompt_message"
    PS3='Please select a profile (or Ctrl-C to quit): '
    IFS=$'\n' read -r -d '' -a profiles <<< "$(aws-vault list --profiles)"
    select profile in "${profiles[@]}"; do
        if [[ -n "$profile" ]]; then
            export "$profile_variable"="$profile"
            break
        else
            echo "Invalid selection, please try again."
        fi
    done
}


select_aws_vault_profile "Select the AWS Vault profile for the environment:" AWS_VAULT_PROFILE_TO_SANITISE
echo "You will use the ${AWS_VAULT_PROFILE_TO_SANITISE} aws-vault profile. Ctrl-C now if this is wrong..."
sleep 10;

# Retrieve AWS account ID using the selected profile
ACCOUNT=$(aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- aws sts get-caller-identity | jq -r ".Account")
echo "Connecting through account ${ACCOUNT}"

# Determine environment based on account ID
case $ACCOUNT in
    012*)echo "(dev)"ADD=0;;
    960*)echo "(test)"ADD=10;;
    233*)echo "(prod)"ADD=30
        echo -e "==========================="
        echo -e "Pair up! This is PRODUCTION";
        echo -e "===========================";
        ;;
    *)
        echo "INVALID ACCOUNT!"
        exit 1
        ;;
esac


# Default values for variables
DEFAULT_SANITISE_DB_NAME="sanitise-db"

# Parse command-line arguments or use defaults
SANITISE_DB_NAME="${1:-$DEFAULT_SANITISE_DB_NAME}"
SANITISE_DB_INSTANCE_NAME="${SANITISE_DB_NAME}-instance"
SANITISE_PATH="Sanitised-database.sql"
S3_BUCKET=""


# Save the current directory
ORIGINAL_DIR=$(pwd)

# List all S3 buckets and get their names
bucket_names=$(aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- aws s3api list-buckets --query "Buckets[].Name" --output json)

for bucket in $(echo "$bucket_names" | jq -r '.[]'); do
    TARGET_BUCKET=$(aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- aws s3api get-bucket-tagging --bucket "$bucket" 2>/dev/null || echo "NO_TAGS")

    # Check if the bucket has no tags
    if [ "$TARGET_BUCKET" == "NO_TAGS" ]; then
        echo "No tags for bucket: $bucket. Skipping..."
        continue
    fi

    SANITISE_BUCKET=$(echo "$TARGET_BUCKET" | jq -r '.TagSet[] | select(.Key == "sanitise" and .Value == "db")')
    if [ -n "$SANITISE_BUCKET" ]; then
        S3_BUCKET="$bucket"
        echo "Found bucket with 'sanitise=db' tag: $S3_BUCKET"
        break
    fi
done


TARGET_CLUSTER=$(
  aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
  aws rds describe-db-clusters \
  | jq '.DBClusters[] | select(.TagList[] | select(.Key == "aws:cloudformation:logical-id" and .Value == "postawardclusterDBCluster"))'
)

RESTORE_SNAPSHOT=$(
  aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
  aws rds describe-db-cluster-snapshots \
  --db-cluster-identifier $(echo $TARGET_CLUSTER | jq -r ".DBClusterIdentifier") \
  | jq -r ".DBClusterSnapshots[].DBClusterSnapshotIdentifier"
)

SANITISATION_DB=$(
  aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
  aws rds restore-db-cluster-from-snapshot \
  --snapshot-identifier $RESTORE_SNAPSHOT \
  --db-cluster-identifier $SANITISE_DB_NAME \
  --serverless-v2-scaling-configuration MinCapacity=0.5,MaxCapacity=4 \
  --vpc-security-group-ids $(echo $TARGET_CLUSTER | jq -r '[.VpcSecurityGroups[].VpcSecurityGroupId] | join(",")') \
  --db-subnet-group-name $(echo $TARGET_CLUSTER | jq -r '.DBSubnetGroup') \
  --no-deletion-protection \
  --db-cluster-instance-class db.serverless \
  --no-publicly-accessible \
  --engine $(echo $TARGET_CLUSTER | jq -r ".Engine")
)

SANITISATION_DB_INSTANCE=$(
  aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
  aws rds create-db-instance \
  --db-instance-identifier $SANITISE_DB_INSTANCE_NAME \
  --db-instance-class db.serverless \
  --engine $(echo $SANITISATION_DB | jq -r '.DBCluster.Engine') \
  --db-cluster-identifier $(echo $SANITISATION_DB | jq -r '.DBCluster.DBClusterIdentifier')
)

# Wait for the DB instance to become available
while : ; do
  SANITISATION_DB_INSTANCE_STATUS=$(
    aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
    aws rds describe-db-instances --db-instance-id $SANITISE_DB_INSTANCE_NAME \
    | jq -r '.DBInstances[0].DBInstanceStatus'
  )
  echo "DB Instance status is: $SANITISATION_DB_INSTANCE_STATUS"
  [[ "$SANITISATION_DB_INSTANCE_STATUS" != "available" ]] || break
  echo "Waiting for 30 seconds..."
  sleep 30;
done

# Connect to the bastion so that we can reach the DB
BASTION_INSTANCE_ID=$(
  aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
  aws ec2 describe-instances \
  --filters Name=tag:Name,Values="*-bastion" "Name=instance-state-name,Values='running'" \
  --query "Reservations[*].Instances[*].InstanceId" \
  | jq -r '.[0][0]'
)


REMOTE_SANITISE_DB_PORT=5432
LOCAL_SANITISE_DB_PORT=1437
DB_TO_SANITISE_HOST=$(echo $SANITISATION_DB | jq -r '.DBCluster.Endpoint')
DB_TO_SANITISE_SECRET=$(aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- aws secretsmanager list-secrets | jq '.SecretList[] | select(.Tags[] | select(.Key == "aws:cloudformation:logical-id" and .Value == "postawardclusterAuroraSecret"))')
DB_TO_SANITISE_PASSWORD=$(aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- aws secretsmanager get-secret-value --secret-id $(echo $DB_TO_SANITISE_SECRET | jq -r '.Name') | jq -r '.SecretString' | jq -r '.password')
DB_TO_SANITISE_URI="postgresql://postgres:${DB_TO_SANITISE_PASSWORD}@localhost:${LOCAL_SANITISE_DB_PORT}/post_award"


trap 'unset DB_TO_SANITISE_PASSWORD' EXIT INT TERM
trap 'DB_TO_SANITISE_URI' EXIT INT TERM

aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
  aws ssm start-session \
  --target $BASTION_INSTANCE_ID \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters host="$DB_TO_SANITISE_HOST",portNumber="$REMOTE_SANITISE_DB_PORT",localPortNumber="$LOCAL_SANITISE_DB_PORT" &

BASTION_SESSION_ID=$!
trap 'kill $BASTION_SESSION_ID' EXIT INT TERM
sleep 10;

echo "removing postgresql_anonymizer if already exist"
rm -rf postgresql_anonymizer

# Clone the repository and Install the postgres anonymiser
echo "Cloning the repository..."
git clone https://gitlab.com/dalibo/postgresql_anonymizer.git
cd ./postgresql_anonymizer || { echo "Failed to enter repository directory"; exit 1; }

# Checkout the version that allows standalone installation
echo "Checking out version 0.8.1..."
git checkout 0.8.1 || { echo "Failed to checkout version 0.8.1"; exit 1; }

# Create the anon_standalone.sql file
echo "Creating the anon_standalone.sql file..."
make standalone || { echo "Failed to create anon_standalone.sql"; exit 1; }

# Execute the SQL file against your Amazon RDS instance
echo "Executing anon_standalone.sql against RDS instance..."
psql $DB_TO_SANITISE_URI -f anon_standalone.sql || { echo "Failed to execute anon_standalone.sql"; exit 1; }

# Navigate back to the original directory
cd "$ORIGINAL_DIR" || { echo "Failed to return to the original directory"; exit 1; }
echo "Anonymising db now"

psql $DB_TO_SANITISE_URI -f sanitise-db.sql || { echo "Failed to execute anonymisation.sql"; exit 1; }
echo "Anonymisation successfully completed."

# Create backup
pg_dump $DB_TO_SANITISE_URI -v -F c --clean --schema=public -f $SANITISE_PATH

# Upload to S3 aws s3 ls
aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE aws s3 cp $SANITISE_PATH s3://$S3_BUCKET/$SANITISE_PATH
echo "File has been uploaded to the S3 bucket"

echo "Cleaning up temporary files..."
rm -rf postgresql_anonymizer || { echo "Failed to remove temporary file"; }
rm -rf $SANITISE_PATH

# deleting database instance≠
aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
    aws rds delete-db-instance \
    --db-instance-identifier $SANITISE_DB_INSTANCE_NAME \
    --skip-final-snapshot \
    --region eu-west-2

echo "Waiting to delete instance...."
aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
    aws rds wait db-instance-deleted \
    --db-instance-identifier $SANITISE_DB_INSTANCE_NAME \
    --region eu-west-2
echo "Db instance has been deleted"

aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
    aws rds delete-db-cluster \
    --db-cluster-identifier $SANITISE_DB_NAME \
    --skip-final-snapshot \
    --region eu-west-2

echo "Waiting for the cluster to be deleted...."
aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
    aws rds wait db-cluster-deleted \
    --db-cluster-identifier $SANITISE_DB_NAME \
    --region eu-west-2
echo "Cluster has been deleted"
