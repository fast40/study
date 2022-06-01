from flask import Flask, render_template, request
import openai

# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:   
# https://aws.amazon.com/developers/getting-started/python/

import boto3
import base64
from botocore.exceptions import ClientError


def get_secret():
    secret_name = "prod/study/openai_api_key"
    region_name = "us-west-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            return 'DecryptionFailureException'
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            return 'InternalServiceErrorException'
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            return 'InvalidParameterException'
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            return 'InvalidRequestException'
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            return 'ResourceNotFoundException'
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
        
        return e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret
            
    # Your code goes here. 
    # return secret

# openai.api_key = get_secret()

application = Flask(__name__)
application.secret_key = 'key'


@application.route('/', methods=['POST', 'GET'])
def index():
    # if request.method == 'POST':
        # response = openai.Completion.create(
        #     engine='text-davinci-002',
        #     prompt=f'Write a multi paragraph essay explaining why the following business name is either effective or ineffective:\n{request.form["user-input"]}. Then give it a score out of 100.',
        #     temperature=0.7,
        #     max_tokens=2048,
        #     top_p=1,
        #     frequency_penalty=0,
        #     presence_penalty=0
        # )

    #     return render_template('survey.html', data={'feedback': response.choices[0].text, 'user_input': request.form['user-input']})
    #     # return render_template('survey.html', feedback='hello')

    # return render_template('survey.html')
    return str(get_secret())


@application.route('/end-of-survey')
def end_of_survey():
    return render_template('end_of_survey.html')


if __name__ == "__main__":
    application.run()