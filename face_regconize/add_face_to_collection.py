import json

import boto3
import os

client=boto3.client('rekognition')

COLLECTION_ID = os.getenv('FACE_COLLECTION_ID')

def add_faces_to_collection(bucket, photo):
    print(f'add face from {bucket}, photo: {photo}')
    response=client.index_faces(CollectionId=COLLECTION_ID,
                                Image={'S3Object':{'Bucket':bucket,'Name':photo}},
                                ExternalImageId=bucket + ':' + photo,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])

    print ('Results for ' + photo) 	
    print('Faces indexed:')						
    for faceRecord in response['FaceRecords']:
         print('  Face ID: ' + faceRecord['Face']['FaceId'])
         print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

    print('Faces not indexed:')
    for unindexedFace in response['UnindexedFaces']:
        print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)
    return len(response['FaceRecords'])
    
def lambda_handler(event, context):
    records = event.get('Records', [])
    print(json.dumps(event))
    for record in records:
        s3_data = record.get('s3', {})
        event_name = record.get('eventName')
        if (event_name == 'ObjectCreated:Put' or event_name == 'ObjectCreated:Copy') and s3_data:
            bucket = s3_data.get('bucket', {}).get('name')
            key =  s3_data.get('object', {}).get('key')
            if bucket and key:
                add_faces_to_collection(bucket, key)