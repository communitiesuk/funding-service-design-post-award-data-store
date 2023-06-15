#!/usr/bin/env bash

usage () {
    echo "Connects a container to a local port, for example to allow you to 'curl' requests from your local machine to the instance."
    echo "Usage: $(basename ${0}) local_port_number -p [port_number] -c [cluster_name] -s [service_name] -t [task_name] -d [docker_container_name]"
    exit 1
}

while [ $OPTIND -le "$#" ]
do
    if getopts p:c:s:t:d: opt
    then
        case $opt in
            p) port_number=$OPTARG
            ;;
            c) cluster_name=$OPTARG
            ;;
            s) service_name=$OPTARG
            ;;
            t) task_name=$OPTARG
            ;;
            d) docker_container_name=$OPTARG
            ;;
            \?) echo "Invalid option -$OPTARG" >&2
            exit 1
            ;;
        esac
    else
        script_args+=("${!OPTIND}")
        ((OPTIND++))
    fi
done

if [[ "${#script_args[@]}" -ne 1 ]]; then
    echo "Invalid number of arguments - local port number must be supplied"
    usage
fi


if [ -z "${port_number}" ]; then
    port_number='8080'
fi

if [ -z "${cluster_name}" ]; then
    cluster_name='post-award-test'
fi

if [ -z "${service_name}" ]; then
    service_name='data-store'
fi

if [ -z "${task_name}" ]; then
    task_name='post-award-test'
fi

if [ -z "${docker_container_name}" ]; then
    docker_container_name='data-store'
fi

export ECS_CLUSTER_ARN="$(aws ecs list-clusters --query "clusterArns[?contains(@, '${cluster_name}')]" --output text | sed 's|.*/||')"

if [ -z "${ECS_CLUSTER_ARN}" ]; then
    echo "Cluster not found"
    exit 1
fi

export ECS_SERVICE_ARN="$(aws ecs list-services --cluster $ECS_CLUSTER_ARN --query "serviceArns[?contains(@, '${service_name}')]" --output text | sed 's|.*/||')"

if [ -z "${ECS_SERVICE_ARN}" ]; then
    echo "Service not found"
    exit 1
fi

export ECS_TASK_ID="$(aws ecs list-tasks --cluster $ECS_CLUSTER_ARN --service $ECS_SERVICE_ARN --query "taskArns[?contains(@, '${task_name}')]" --output text | sed 's|.*/||')"

if [ -z "${ECS_TASK_ID}" ]; then
    echo "Task not found"
    exit 1
fi

export ECS_CONTAINER_ID="$(aws ecs describe-tasks --cluster $ECS_CLUSTER_ARN --task $ECS_TASK_ID --query "tasks[].containers[?name=='${docker_container_name}'].runtimeId" --output text | sed 's|.*/||')"

if [ -z "${ECS_CONTAINER_ID}" ]; then
    echo "Container not found"
    exit 1
fi

aws ssm start-session \
    --target "ecs:${ECS_CLUSTER_ARN}_${ECS_TASK_ID}_${ECS_CONTAINER_ID}" \
    --document-name AWS-StartPortForwardingSession \
    --parameters "{\"portNumber\":[\"$port_number\"],\"localPortNumber\":[\"$1\"]}"
