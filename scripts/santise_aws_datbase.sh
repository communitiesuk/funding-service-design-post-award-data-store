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

echo "You selected the ${ENV} environment."
select_aws_vault_profile "Select the AWS Vault profile for the ${ENV} environment:" AWS_VAULT_PROFILE_TO_SANITISE
echo "You will use the ${AWS_VAULT_PROFILE_TO_SANITISE} aws-vault profile. Ctrl-C now if this is wrong..."

sleep 10;

# Variables based on the environment
SANITISE_DB_NAME="sanitise-db"
SANITISE_DB_INSTANCE_NAME="$SANITISE_DB_NAME-instance"
BACKUP_FILE="mydatabase_backup.sql"
S3_BUCKET="aws-s3-bucket-sanitise-database"
S3_PATH="mydatabase_backup.sql"

# Save the current directory
ORIGINAL_DIR=$(pwd)

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

#download the postgres anonymiser
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

# Connect to the bastion so that we can reach the DB
BASTION_INSTANCE_ID=$(
  aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- \
  aws ec2 describe-instances \
  --filters Name=tag:Name,Values=\'*-bastion\' "Name=instance-state-name,Values='running'" \
  --query "Reservations[*].Instances[*].InstanceId" \
  | jq -r '.[0][0]'
)

REMOTE_SANITISE_DB_PORT=5432
LOCAL_SANITISE_DB_PORT=1437
DB_TO_SANITISE_HOST=$(echo $SANITISATION_DB | jq -r '.DBCluster.Endpoint')
DB_TO_SANITISE_SECRET=$(aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- aws secretsmanager list-secrets | jq '.SecretList[] | select(.Tags[] | select(.Key == "aws:cloudformation:logical-id" and .Value == "postawardclusterAuroraSecret"))')
DB_TO_SANITISE_PASSWORD=$(aws-vault exec $AWS_VAULT_PROFILE_TO_SANITISE -- aws secretsmanager get-secret-value --secret-id $(echo $DB_TO_SANITISE_SECRET | jq -r '.Name') | jq -r '.SecretString' | jq -r '.password')
DB_TO_SANITISE_URI="postgresql://postgres:${DB_TO_SANITISE_PASSWORD}@localhost:${LOCAL_SANITISE_DB_PORT}/post_award"
aws-vault exec $AWS_AWS_VAULT_PROFILE_TO_SANITISE -- \
  aws ssm start-session \
  --target $BASTION_INSTANCE_ID \
  --document-name AWS-StartPortForwardingSessionToRemoteHost \
  --parameters host="$DB_TO_SANITISE_HOST",portNumber="$REMOTE_SANITISE_DB_PORT",localPortNumber="$LOCAL_SANITISE_DB_PORT" &

BASTION_SESSION_ID=$!

# Execute the SQL file against your Amazon RDS instance
echo "Executing anon_standalone.sql against RDS instance..."
psql $DB_TO_SANITISE_URI -f anon_standalone.sql || { echo "Failed to execute anon_standalone.sql"; exit 1; }

# Navigate back to the original directory
cd "$ORIGINAL_DIR" || { echo "Failed to return to the original directory"; exit 1; }
echo "Anonymising db now"
psql $DB_TO_SANITISE_URI -f anonymise_2.sql || { echo "Failed to execute anonmisation.sql"; exit 1; }
echo "Process completed and anonymisation successfully."

#Create backup
pg_dump $DB_TO_SANITISE_URI -v -F c --clean -f $BACKUP_FILE

kill $BASTION_SESSION_ID # Terminate the session on the bastion SSH forwarding to the sanitisation DB

#Upload to S3 aws s3 ls
aws s3 cp $BACKUP_FILE s3://$S3_BUCKET/$S3_PATH
