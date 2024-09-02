#!/usr/bin/bash
#
# Takes an environment [dev|test|prod]
# * Restore to a new RDS DB from latest snapshot of production database
# * Wait for that to complete (~15 minutes)
# * Install postgresql anonymiser using standalone script
# * Run the sanitisation process against that DB
# * `pg_dump $SOURCE_URL -v -F c --clean` that to a file stored to the S3 bucket
# * Cleanup (destroy) the RDS DB used for sanitisation

SANITISE_DB_NAME=sanitise-db

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
  --db-instance-identifier sam-sanitise-instance \
  --db-instance-class db.serverless \
  --engine $(echo $SANITISATION_DB | jq -r '.DBCluster.Engine') \
  --db-cluster-identifier $(echo $SANITISATION_DB | jq -r '.DBCluster.DBClusterIdentifier')
