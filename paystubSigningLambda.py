# import json
# import boto3
# from PyPDF2 import PdfFileWriter, PdfFileReader

# def populate_pdf(json_data, template_path):
#     # Load the PDF template
#     pdf = PdfFileReader(template_path)
#     pdf_writer = PdfFileWriter()

#     # Extract the page to be modified
#     page = pdf.getPage(0)

#     # Replace placeholders with data from JSON
#     for key, value in json_data.items():
#         if value.get("S"):
#             placeholder = f"{{{{{key}.S}}}}"
#             page = replace_placeholder(page, placeholder, value["S"])
#         elif value.get("N"):
#             placeholder = f"{{{{{key}.N}}}}"
#             page = replace_placeholder(page, placeholder, value["N"])
#         elif value.get("M"):
#             for sub_key, sub_value in value["M"].items():
#                 if sub_value.get("S"):
#                     placeholder = f"{{{{{key}.{sub_key}.S}}}}"
#                     page = replace_placeholder(page, placeholder, sub_value["S"])
#                 elif sub_value.get("N"):
#                     placeholder = f"{{{{{key}.{sub_key}.N}}}}"
#                     page = replace_placeholder(page, placeholder, sub_value["N"])

#     # (Implement the replace_placeholder function to handle string replacements)
    
#     # Add the modified page to pdf_writer
#     pdf_writer.addPage(page)
    
#     # Return the populated PDF
#     return pdf_writer

# def lambda_handler(event, context):
#     # Assume the event contains the JSON payload
#     json_data = event['body']
    
#     # Path to the template (for Lambda, the template would be in the same directory or in an S3 bucket)
#     template_path = "path_to_template.pdf"
    
#     # Populate the PDF
#     populated_pdf = populate_pdf(json_data, template_path)
    
#     # Digitally sign, save to S3, and generate verification URL (as described in the initial response)
#     # ...

#     return {
#         'statusCode': 200,
#         'body': "PDF generated and stored"
#     }

import json
import boto3
from PyPDF2 import PdfFileWriter, PdfFileReader
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from PyPDF2 import PdfFileWriter, PdfFileReader
import io

# Implement the replace_placeholder function to handle string replacements
def replace_placeholder(page, placeholder, replacement):
    # Replace the placeholder with the replacement text on the page
    return page.extractText().replace(placeholder, replacement)

def populate_pdf(json_data, template_path):
    # Load the PDF template
    pdf = PdfFileReader(open(template_path, "rb"))
    pdf_writer = PdfFileWriter()

    # Extract the page to be modified
    page = pdf.getPage(0)

    # Replace placeholders with data from JSON
    for key, value in json_data.items():
        if isinstance(value, str):
            placeholder = f"{{{{{key}}}}"
            page = replace_placeholder(page, placeholder, value)

    # Add the modified page to pdf_writer
    pdf_writer.addPage(page)
    
    # Return the populated PDF
    return pdf_writer

def lambda_handler(event, context):
    # Assume the event contains the JSON payload
    json_data = json.loads(event['body'])
    
    # Path to the template (for Lambda, the template would be in the same directory or in an S3 bucket)
    template_path = "path_to_template.pdf"
    
    # Populate the PDF
    populated_pdf = populate_pdf(json_data, template_path)
    
    # Digitally sign, save to S3, and generate verification URL (as described in the initial response)
    # ...



# Generate a key pair (public and private keys)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

# Serialize and save the private key securely (you should handle key storage securely)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)
with open('private_key.pem', 'wb') as private_key_file:
    private_key_file.write(private_pem)

# Load the PDF to sign
pdf_path = 'document_to_sign.pdf'
pdf = PdfFileReader(open(pdf_path, 'rb'))

# Create a PDF writer to create the signed PDF
output_pdf = PdfFileWriter()

# Iterate through each page of the PDF
for page in pdf.pages:
    # Calculate the hash of the page content
    page_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
    page_hash.update(page.extractText().encode())
    hash_value = page_hash.finalize()

    # Sign the hash with the private key
    signature = private_key.sign(
        hash_value,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Embed the signature in the PDF
    page.annotation_update.append(signature)

    # Add the page to the output PDF
    output_pdf.addPage(page)

# Save the signed PDF
with io.BytesIO() as output_buffer:
    output_pdf.write(output_buffer)
    with open('signed_document.pdf', 'wb') as signed_pdf_file:
        signed_pdf_file.write(output_buffer.getvalue())


    return {
        'statusCode': 200,
        'body': "PDF generated and stored"
    }

