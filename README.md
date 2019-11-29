# Require:
## Install SAM cli
Read more at https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
## Verify SES Sandbox email 
 Open aws SES service in US-EAST-1 zone , verify sender email and receiver email
Create Collection
```
aws rekognition create-collection --collection-id demo-face-regconize
```
## Deploy:
```
sam build
sam deploy --guided
```

## How to demo:
- Upload your photo to "${AWS::AccountId}-demo-owner-face"
- Upload strange person image to "${AWS::AccountId}-demo-detection-face", system will send email
- Upload another your photo to "${AWS::AccountId}-demo-detection-face", no email be sent
