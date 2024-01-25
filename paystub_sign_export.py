import boto3
from botocore.exceptions import NoCredentialsError

# Your AWS credentials (replace with your actual credentials)
aws_access_key_id = 'YOUR_ACCESS_KEY'
aws_secret_access_key = 'YOUR_SECRET_KEY'
s3_bucket_name = 'YOUR_S3_BUCKET_NAME'

# Initialize an S3 client
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Save the signed PDF to a local file
with open('signed_document.pdf', 'rb') as signed_pdf_file:
    signed_pdf_data = signed_pdf_file.read()

# Upload the signed PDF to S3
try:
    s3.upload_fileobj(io.BytesIO(signed_pdf_data), s3_bucket_name, 'path/to/signed_document.pdf')
except NoCredentialsError:
    print("AWS credentials not found. Make sure your credentials are correctly configured.")

# Generate a pre-signed URL for the uploaded PDF (valid for a specified time)
expiration_time = 3600  # Adjust this as needed, in seconds (e.g., 1 hour)
signed_url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': s3_bucket_name, 'Key': 'path/to/signed_document.pdf'},
    ExpiresIn=expiration_time
)

print("Signed PDF uploaded to S3.")
print("Verification URL (valid for {} seconds):".format(expiration_time))
print(signed_url)
