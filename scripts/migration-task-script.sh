#!/usr/bin/env bash

# Define the options
options="-l environment:,command:,"

# Initialize the variables
environment="test"
command="flask db current"

# Get the options
while getopts $options OPT; do
  case $OPT in
    e|environment)
      environment="$OPTARG"
      ;;
    c|command)
      command="$OPTARG"
      ;;
    l)
      echo "Environment: $environment (long: --environment)"
      echo "Command: $command (long: --command)"
      exit 0
      ;;
    ?)
      echo "Invalid option: $OPT"
      exit 1
      ;;
  esac
done

# Print the arguments
echo "Environment: $environment"
echo "Command: $command"

filename=generated_command_taskrun.sh
echo '' >$filename

(copilot task run --generate-cmd post-award/$environment/data-store 2>&1 | sed '$ s/$/ \\/' | sed 's/--command.*/d \\/') >>$filename

cat <<EOF >>$filename
--follow \\
--task-group-name "db-migrate" \\
EOF

echo "--command \"/bin/sh -c '$command ; echo EXEC-EXIT-CODE=\\\$?'\"" >>$filename

source $filename | tee /tmp/exec-output

exitcode=$(sed -nr 's/.* EXEC-EXIT-CODE=([0-9]+)/\1/p' /tmp/exec-output | tr -d '\r\n')

echo got exit code "'$exitcode'"

if [ -z "$exitcode" ]; then
  echo could not find exit code in copilot output
  exit 1
fi
