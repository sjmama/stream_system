import boto3 as to3

def s3_connection():
    try:
        s3 = to3.client(
            service_name="s3",
            region_name="your_s3 region_name",
            aws_access_key_id="your_aws_access_key",
            aws_secret_access_key="your_aws_credit",
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3
s3=s3_connection()