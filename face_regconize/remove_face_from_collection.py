import json

import boto3
import os

client=boto3.client('rekognition')

COLLECTION_ID = os.getenv('FACE_COLLECTION_ID')

def remove_face_in_collection(bucket, photo):
    maxResults=2
    faces_count=0
    tokens=True

    client=boto3.client('rekognition')
    response=client.list_faces(CollectionId=COLLECTION_ID,
                               MaxResults=maxResults)

    print('Faces in collection ' + COLLECTION_ID)

 
    while tokens:
        faces=response['Faces']

        for face in faces:
            print (face)
            external_image_id = face.get('ExternalImageId')
            if external_image_id == (bucket + ':' + photo):
                face_id = face.get('FaceId')
                delete_response=client.delete_faces(CollectionId=COLLECTION_ID,
                               FaceIds=[face_id])
    
                print(str(len(delete_response['DeletedFaces'])) + ' faces deleted:') 
            faces_count+=1
        if 'NextToken' in response:
            nextToken=response['NextToken']
            response=client.list_faces(CollectionId=COLLECTION_ID,
                                       NextToken=nextToken,MaxResults=maxResults)
        else:
            tokens=False
    return faces_count   

    
def lambda_handler(event, context):
    records = event.get('Records', [])
    print(json.dumps(event))
    for record in records:
        s3_data = record.get('s3', {})
        event_name = record.get('eventName')
        if event_name == 'ObjectRemoved:Delete' and s3_data:
            bucket = s3_data.get('bucket', {}).get('name')
            key =  s3_data.get('object', {}).get('key')
            if bucket and key:
                remove_face_in_collection(bucket, key)
