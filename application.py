from flask import Flask, render_template, request
import openai

openai.api_key = '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'

application = Flask(__name__)
application.secret_key = 'key'


@application.route('/', methods=['POST', 'GET'])
def index():
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


if __name__ == "__main__":
    application.run()