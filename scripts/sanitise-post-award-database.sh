#!/usr/bin/bash
#
# Takes an environment [dev|test|prod]
# * Restore to a new RDS DB from latest snapshot of production database
# * Wait for that to complete (~15 minutes)
# * Install postgresql anonymiser using standalone script
# * Run the sanitisation process against that DB
# * `pg_dump $SOURCE_URL -v -F c --clean` that to a file stored to the S3 bucket
# * Cleanup (destroy) the RDS DB used for sanitisation


TARGET_CLUSTER=$(aws rds describe-db-clusters | jq '.DBClusters[] | select(.TagList[] | select(.Key == "aws:cloudformation:logical-id" and .Value == "postawardclusterDBCluster")) | {DBClusterIdentifier, Engine,}')

RESTORE_SNAPSHOT=$(aws rds describe-db-cluster-snapshots --db-cluster-identifier $(echo $TARGET_CLUSTER | jq -r ".DBClusterIdentifier") | jq -r ".DBClusterSnapshots[].DBClusterSnapshotIdentifier")

aws rds restore-db-cluster-from-snapshot \
  --snapshot-identifier $RESTORE_SNAPSHOT \
  --db-cluster-identifier sanitise-db \
  --engine $(echo $TARGET_CLUSTER | jq -r ".Engine")
