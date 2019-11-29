import boto3
import os

COLLECTION_ID = os.getenv('FACE_COLLECTION_ID')
FACE_MATCH_THRESHOLD = int(os.getenv('FACE_MATCH_THRESHOLD', 70))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')

rekognition_client=boto3.client('rekognition')
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
ses_client = boto3.client('ses',  region_name='us-east-1')
s3_client = boto3.client('s3')

def send_strange_person_email(bucket: str, key: str):
    
    message = MIMEMultipart()
    message['Subject'] = 'Strange person in your home'
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL
    # message body
    part = MIMEText('Strange person in your home, please see the below image', 'html')
    message.attach(part)
    TMP_FILE_NAME = '/tmp/strange_person.jpg'
    s3_client.download_file(bucket, key, TMP_FILE_NAME)
    
    # attachment
    
    part = MIMEApplication(open(TMP_FILE_NAME, 'rb').read())
    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(TMP_FILE_NAME))
    message.attach(part)
    response = ses_client.send_raw_email(
        Source=message['From'],
        Destinations=[x.strip() for x in RECEIVER_EMAIL.split(',')],
        RawMessage={
            'Data': message.as_string()
        }
    )
    
def detect_face(bucket: str, key: str):
    maxFaces=2

    print(f'Bucket: {bucket}, Key: {key}')
    response = rekognition_client.search_faces_by_image(CollectionId=COLLECTION_ID,
                                Image={'S3Object':{'Bucket':bucket,'Name':key}},
                                FaceMatchThreshold=FACE_MATCH_THRESHOLD,
                                MaxFaces=maxFaces)

                                
    faceMatches=response['FaceMatches']
    print ('Matching faces')
    if faceMatches:
        for match in faceMatches:
                print ('FaceId:' + match['Face']['FaceId'])
                print ('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                print
    else:
        print ('Not matching')
        send_strange_person_email(bucket, key)

            
def lambda_handler(event: dict, context: dict):
    records = event.get('Records', [])
    for record in records:
        s3_data = record.get('s3', {})
        event_name = record.get('eventName')
        if (event_name == 'ObjectCreated:Put' or event_name == 'ObjectCreated:Copy') and s3_data:
            bucket = s3_data.get('bucket', {}).get('name')
            key =  s3_data.get('object', {}).get('key')
            if bucket and key:
                detect_face(bucket, key)
    
