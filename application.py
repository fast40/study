from flask import Flask

application = Flask(__name__)


@application.route('/')
def index():
    return 'Hello AWS world!'


if __name__ == "__main__":
    application.run()