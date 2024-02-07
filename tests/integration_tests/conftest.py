from core.aws import _S3_CLIENT


def create_bucket(bucket: str):
    """Helper function that creates a specified bucket if it doesn't already exist."""
    if bucket not in {bucket_obj["Name"] for bucket_obj in _S3_CLIENT.list_buckets()["Buckets"]}:
        _S3_CLIENT.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "eu-central-1"})


def delete_bucket(bucket: str):
    """Helper function that deletes all objects in a specified bucket and then deletes the bucket."""
    objects = _S3_CLIENT.list_objects_v2(Bucket=bucket)
    if objects := objects.get("Contents"):
        objects = list(map(lambda x: {"Key": x["Key"]}, objects))
        _S3_CLIENT.delete_objects(Bucket=bucket, Delete={"Objects": objects})
    _S3_CLIENT.delete_bucket(Bucket=bucket)
