#!/usr/bin/env bash

usage () {
    echo "Connects a container to a local port, for example to allow you to 'curl' requests from your local machine to the instance."
    echo "Usage: $(basename ${0}) local_port_number [port_number] [cluster_name] [service_name] [task_name] [container_name]"
    exit 1
}

if [[ "${#}" -lt 1 ]]; then
    echo "Invalid number of arguments - local port number must be supplied"
    usage
fi

if [ -z "${2}" ]; then
    port_number='8080'
else
    port_number=${2}
fi

if [ -z "${3}" ]; then
    cluster_name='post-award-test'
else
    cluster_name=${3}
fi

if [ -z "${4}" ]; then
    service_name='data-store'
else
    service_name=${4}
fi

if [ -z "${5}" ]; then
    task_name='post-award-test'
else
    task_name=${5}
fi

if [ -z "${6}" ]; then
    container_name='data-store'
else
    container_name=${6}
fi

export ECS_CLUSTER_ARN="$(aws ecs list-clusters --query "clusterArns[?contains(@, '${cluster_name}')]" --output text | sed 's|.*/||')"
export ECS_SERVICE_ARN="$(aws ecs list-services --cluster $ECS_CLUSTER_ARN --query "serviceArns[?contains(@, '${service_name}')]" --output text | sed 's|.*/||')"
export ECS_TASK_ID="$(aws ecs list-tasks --cluster $ECS_CLUSTER_ARN --service $ECS_SERVICE_ARN --query "taskArns[?contains(@, '${task_name}')]" --output text | sed 's|.*/||')"
export ECS_CONTAINER_ID="$(aws ecs describe-tasks --cluster $ECS_CLUSTER_ARN --task $ECS_TASK_ID --query "tasks[].containers[?name=='${container_name}'].runtimeId" --output text | sed 's|.*/||')"

aws ssm start-session \
    --target "ecs:${ECS_CLUSTER_ARN}_${ECS_TASK_ID}_${ECS_CONTAINER_ID}" \
    --document-name AWS-StartPortForwardingSession \
    --parameters "{\"portNumber\":[\"$port_number\"],\"localPortNumber\":[\"$1\"]}"
