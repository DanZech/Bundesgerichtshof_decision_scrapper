import requests
from bs4 import BeautifulSoup
import boto3
from botocore.exceptions import ClientError
import json
import re
from datetime import datetime

# Initialize S3 client
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb', region_name="eu-central-1")
def getStageVariables(stage):
    if stage == "prod":
        all_data_table = 'iurcrowd-adb-alldata-prod'
        output_bucket_name = 'iurcrowd-s3-crawled.data-prod'  # replace with your bucket name
    else:
        all_data_table = 'iurcrowd-adb-alldata-dev'
        output_bucket_name = 'iurcrowd-s3-crawled.data-dev'  # replace with your bucket name
    return all_data_table,output_bucket_name

def extract_info_from_resources(context):
    resource = context.invoked_function_arn
    if '_dev' in resource:
        return 'dev'
    elif '_prod' in resource:
        return 'prod'
    return None

def get_document_id(event):
    record = event['Records'][0]        # Step 1: Access the first record in the event

    if isinstance(record, str):         # Step 2: Check if the record is a string
        record = json.loads(record)     # Step 3: If it is a string, parse it to a JSON object
        
    body_str = record['body']           # Step 4: Access the body of the record
    body = json.loads(body_str)         # Step 5: Parse the body to a JSON object
     
    if isinstance(body, str):
        body = json.loads(body)

    body_records = body['Records']
    if isinstance(body, str):
        records = json.loads(body_records)
    else: 
        records = body_records

    s3_info = records[0]['s3']

    object_info = s3_info['object']

    document_fn = object_info['key']

    document_id = int(document_fn.split(".")[0])

    return document_id, document_fn
 

def analyze_and_save_title(title, all_data_table, dataset_id):
    # Replace '&nbsp;' with spaces
    title = title.replace('&nbsp;', ' ')

    # Regular expression to find the date in format 'dd.mm.yyyy'
    date_match = re.search(r'\d{1,2}\.\d{1,2}\.\d{4}', title)
    parts = title.replace('&nbsp;', ' ').split(' ')
    print("date_match: ",date_match)
    if date_match:
        date_str = date_match.group()
        # Extract everything before the date
        before_date = title.split(date_str)[0]

        # Extract the document type (first word) and then remove it along with certain words
        parts_date = before_date.split(' ')
        if len(parts) < 2:
            print("Title format is not as expected.")
            return

        # Convert the date to the specified format (Soll-Format: YYYY-MM-DD)
        date = datetime.strptime(date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
    else:
        print("No date found in the title.")
        date=""
        return
    
    aktenzeichen = ''.join(parts[-1:])  # Takes the last part without spaces
    aktenzeichen = aktenzeichen.strip().strip("-").strip()
    aktenzeichen = aktenzeichen.replace('\xa0', ' ')  # Replace non-breaking spaces with regular spaces
    
    
    
    document_type = parts_date[0]  # First word as document type
    Senat = ' '.join(parts_date[1:])  # Rest of the title without document type
    # Remove specific words
    Senat = re.sub(r'\b(der|die|das|des|vom)\b', '', Senat).strip()
    Senat=Senat.replace('\xa0', ' ')
    
    # Remove the last letter if it is 's'
    if Senat.endswith('s'):
        Senat = Senat[:-1]  # Remove the last character
    
    i =0
    for part in parts:
        print("Part ",i,": ",part)
        i = i+1
        
    print("Extracted data: ", document_type, "date:" ,date,"aktenzeichen: ",aktenzeichen)

    # Check in DynamoDB if Aktenzeichen already exists
    try:
        response = dynamodb_client.query(
            TableName=all_data_table,
            IndexName='aktenzeichen-index',  # Update with your index name
            KeyConditionExpression="aktenzeichen = :aktenzeichen",
            ExpressionAttributeValues={
                ":aktenzeichen": {"S": aktenzeichen}
            }
        )
        if response['Items']:
            # Aktenzeichen exists, update the entry
            print("Aktenzeichen exists in DynamoDB. Updating the entry.")
            aktenzeichen_exists= True
            # Add your logic here to update the DynamoDB entry
        else:
            # Aktenzeichen does not exist, create a new entry
            print("Aktenzeichen does not exist in DynamoDB. Creating a new entry.")
            aktenzeichen_exists= False
        # create unique_id 
        juris_dataset_prefix = "100000"
        # unique_id filled up to 8 digits with leading 0s
        unique_id = juris_dataset_prefix + str(dataset_id).zfill(8)
        item = {
                'category': {'S': "DOCUMENT"},
                'unique_id': {'N': str(unique_id)},
                'aktenzeichen': {'S': aktenzeichen},
                'dataset_id': {'S': str(dataset_id)},
                'data_set': {'S': 'juris_bundesgerichtshof'},
                'document_type': {'S': document_type},
                'database_title':{'S': title.replace('\xa0', ' ')},
                'senat':{'S': Senat},
                'crawled_from': {'S': "juris.bundesgerichtshof"} # Set to True if applicable
            }
        if date == "":        
            item['veroeffentlichung'] = {'S': date}
        # IF Aktenzeichen contains "KZR" add KZR_in_aktenzeichen to item 
        # Check if Aktenzeichen contains "KZR" and add KZR_in_aktenzeichen to item
        if "KZR" in aktenzeichen:
            item['KZR_in_aktenzeichen'] = {'BOOL': True}

        item['aktenzeichen_already_existed'] = {'BOOL': aktenzeichen_exists}
        print("DynamoDB Item: ",item)
        dynamodb_client.put_item(
            TableName=all_data_table,
            Item=item            
            )
        print("New entry created in DynamoDB.")

    except ClientError as e:
        print(f"Error querying DynamoDB: {e}")


def scrape_and_save_webpage(url, file_name,bucket_name):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find('title')
        print("title_tag", title_tag)
        print("title_tag.text: ",title_tag.text)
        # Check if the title tag is exactly 'Dokument'
        if title_tag and title_tag.text.strip() == 'Dokument':
            print(f"Title is exactly 'Dokument' in '{url}', skipping download.")
            return False, ""

        # Save the HTML content to S3
        s3_client.put_object(Bucket=bucket_name, Key=f'HTML/{file_name}', Body=response.text, ContentType='text/html')
        print(f"HTML content saved to S3 bucket in 'HTML/{file_name}'")
        return True, title_tag.text

    except requests.HTTPError as e:
        print(f"Failed to access '{url}': {e}")
        return False, title_tag.text

def download_pdf(url, file_name,output_bucket_name):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Save the PDF to S3
        s3_client.put_object(Bucket=output_bucket_name, Key=f'PDFs/{file_name}', Body=response.content, ContentType='application/pdf')
        print(f"Downloaded PDF saved to S3 bucket in 'PDFs/{file_name}'")
    except requests.HTTPError as e:
        print(f"Failed to download PDF from '{url}': {e}")



def file_exists_in_s3(key,output_bucket_name):
    try:
        s3_client.head_object(Bucket=output_bucket_name, Key=key)
        return True
    except ClientError:
        return False
    
def lambda_handler(event, context):
    stage = extract_info_from_resources(context)
    all_data_table,output_bucket_name = getStageVariables(stage)
    unique_id, file_key = get_document_id(event)
    # Base URL components
    base_url = "https://juris.bundesgerichtshof.de"
    document_path = "/cgi-bin/rechtsprechung/document.py?Gericht=bgh&Art=en"
    
    # Iterate over a range of 'nr' values
    base_file_name = f"juris_bundesgerichtshof_{unique_id}"
    html_file_name = f"{base_file_name}.html"
    pdf_file_name = f"{base_file_name}.pdf"

    # Check if files already exist in S3
    if not file_exists_in_s3('HTML/' + html_file_name,output_bucket_name):
        webpage_url = f"{base_url}{document_path}&nr={unique_id}" 
        pdf_url = f"{base_url}{document_path}&nr={unique_id}&Frame=4&.pdf"

        # Scrape and save webpage
        scrape_flag, title = scrape_and_save_webpage(webpage_url, html_file_name,output_bucket_name)
        if scrape_flag:
            # Download and save PDF
            analyze_and_save_title(title,all_data_table,unique_id)
            download_pdf(pdf_url, pdf_file_name,output_bucket_name)
    else:
        print(f"Files for NR {unique_id} already exist in S3.")


    
    