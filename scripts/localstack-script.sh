#!/bin/bash

awslocal s3api \
create-bucket --bucket data-store-failed-files-dev \
--create-bucket-configuration LocationConstraint=eu-central-1 \
--region eu-central-1

awslocal s3api \
create-bucket --bucket data-store-successful-files-dev \
--create-bucket-configuration LocationConstraint=eu-central-1 \
--region eu-central-1
