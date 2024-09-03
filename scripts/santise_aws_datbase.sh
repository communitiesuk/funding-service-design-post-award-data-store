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


SANITISE_DB_NAME=sanitise-db
SOURCE_URL=""
BACKUP_FILE="mydatabase_backup.sql"
S3_BUCKET="sanitisation-db"
S3_PATH="backups/mydatabase_backup.sql"

# Save the current directory
ORIGINAL_DIR=$(pwd)

TARGET_CLUSTER=$(
  aws rds describe-db-clusters \
  | jq '.DBClusters[] | select(.TagList[] | select(.Key == "aws:cloudformation:logical-id" and .Value == "postawardclusterDBCluster"))'
)

RESTORE_SNAPSHOT=$(
  aws rds describe-db-cluster-snapshots \
  --db-cluster-identifier $(echo $TARGET_CLUSTER | jq -r ".DBClusterIdentifier") \
  | jq -r ".DBClusterSnapshots[].DBClusterSnapshotIdentifier"
)

SANITISATION_DB=$(
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

aws rds create-db-instance \
  --db-instance-identifier sanitisation-db \
  --db-instance-class db.serverless \
  --engine $(echo $SANITISATION_DB | jq -r '.DBCluster.Engine') \
  --db-cluster-identifier $(echo $SANITISATION_DB | jq -r '.DBCluster.DBClusterIdentifier')


#download the postgres anonymiser
##!/bin/bash


# Clone the repository and cd into it
echo "Cloning the repository..."
git clone https://gitlab.com/dalibo/postgresql_anonymizer.git
cd ./postgresql_anonymizer || { echo "Failed to enter repository directory"; exit 1; }

# Checkout the version that allows standalone installation
echo "Checking out version 0.8.1..."
git checkout 0.8.1 || { echo "Failed to checkout version 0.8.1"; exit 1; }

# Create the anon_standalone.sql file
echo "Creating the anon_standalone.sql file..."
make standalone || { echo "Failed to create anon_standalone.sql"; exit 1; }

 Execute the SQL file against your Amazon RDS instance
echo "Executing anon_standalone.sql against RDS instance..."
psql $SOURCE_URL -f anon_standalone.sql || { echo "Failed to execute anon_standalone.sql"; exit 1; }

# Navigate back to the original directory
cd "$ORIGINAL_DIR" || { echo "Failed to return to the original directory"; exit 1; }
echo "Anonymising db now"
psql $SOURCE_URL -f anonymise_2.sql || { echo "Failed to execute anonmisation.sql"; exit 1; }
echo "Process completed and anonymisation successfully."

#Create backup
pg_dump $SOURCE_URL -v -F c --clean -f $BACKUP_FILE

#Upload to S3 aws s3 ls
aws s3 cp $BACKUP_FILE s3://$S3_BUCKET/$S3_PATH
