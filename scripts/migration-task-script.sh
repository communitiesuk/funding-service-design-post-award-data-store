#!/usr/bin/env bash

filename=generated_command_taskrun.sh
echo '' >$filename

(copilot task run --generate-cmd post-award/test/data-store 2>&1 | sed '$ s/$/ \\/' | sed 's/--command.*/d \\/') >>$filename

cat <<EOF >>$filename
--follow \\
--task-group-name "db-migrate" \\
EOF

echo "--command \"/bin/sh -c 'flask db current ; echo EXEC-EXIT-CODE=\\\$?'\"" >>$filename

source $filename | tee /tmp/exec-output

exitcode=$(sed -nr 's/.* EXEC-EXIT-CODE=([0-9]+)/\1/p' /tmp/exec-output | tr -d '\r\n')

echo got exit code "'$exitcode'"

if [ -z "$exitcode" ]; then
  echo could not find exit code in copilot output
  exit 1
fi
