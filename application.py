from unittest import TestCase
from flask import Flask, render_template, request
import openai
import ast

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

openai.api_key = ast.literal_eval(get_secret())['openai_api_key']

application = Flask(__name__)
application.secret_key = 'key'


@application.route('/')
def index():
    return render_template('final.html')


@application.route('/api', methods=['POST'])
def api():
    version = request.form["version"]
    user_input = request.form["input"]

    if version == '0':
        prompt = f'Evaluate the following coffee shop name: "{user_input}". Describe the name\'s strengths and weaknesses, but do not provide other name options.'
    elif version == '1':
        prompt = f'Evaluate the following coffee shop name: "{user_input}". Describe the name\'s strengths and weaknesses, and assign it a rating from 0 to 50, with 50 being the best.'
    else:
        return "If you are seeing this text there was an issue displaying the feedback"

    response = openai.Completion.create(
        engine='text-davinci-002',
        prompt=prompt,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].text


@application.route('/legacy', methods=['POST', 'GET'])
def legacy():
    # s = get_secret()
    # return s.openai_api_key
    if request.method == 'POST':
        response = openai.Completion.create(
            engine='text-davinci-002',
            prompt=f'Write a multi paragraph essay explaining why the following business name is either effective or ineffective:\n{request.form["user-input"]}. Then give it a score out of 100.',
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return render_template('survey.html', data={'feedback': response.choices[0].text, 'user_input': request.form['user-input']})
        # return render_template('survey.html', feedback='hello')

    return render_template('survey.html')


@application.route('/end-of-survey')
def end_of_survey():
    return render_template('end_of_survey.html')


@application.route('/csv', methods=['POST'])
def csv():
    s3 = boto3.resource('s3')

    obj = s3.Object('userresponses', 'responses.csv')

    file_content = obj.get()['Body'].read().decode() + \
        '"' + request.form['id'].strip().replace('"', '""') + '",' + \
        '"' + request.form['condition'].strip().replace('"', '""') + '",' + \
        '"' + request.form['name1'].strip().replace('"', '""') + '",' + \
        '"' + request.form['feedback1'].strip().replace('"', '""') + '",' + \
        '"' + request.form['name2'].strip().replace('"', '""') + '",' + \
        '"' + request.form['feedback2'].strip().replace('"', '""') + '"\n'

    obj.put(Body=file_content.encode())

    return obj.get()['Body'].read().decode()


@application.route('/reset-csv', methods=['GET'])
def reset_csv():
    s3 = boto3.resource('s3')

    obj = s3.Object('userresponses', 'responses.csv')
    obj.put(Body=b'id,condition,name1,feedback1,name2,feedback2\n')

    return obj.get()['Body'].read().decode()


if __name__ == "__main__":
    application.run()