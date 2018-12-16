from flask import Flask, request
from flask import render_template
import requests
import os.path

TEMPLATES_FOLDER = 'templates'
STATICS_FOLDER = 'static'
app = Flask(__name__, static_url_path='', static_folder=STATICS_FOLDER, template_folder=TEMPLATES_FOLDER)

SA_TOKEN = None
SA_TOKEN_FROM_PATH = None
SA_TOKEN_PATH = '/var/run/secrets/kubernetes.io/serviceaccount/token'

APP_NAME = "APP_NAME" in os.environ and os.environ.get('APP_NAME') or "My Kubernetes Dashboard"


@app.route('/test', methods=['POST'])
def test():
    global SA_TOKEN
    json_data = request.get_json(silent=True)

    SA_TOKEN = "token" in json_data and json_data["token"] or SA_TOKEN_FROM_PATH

    print("SA_TOKEN=" + str(SA_TOKEN))

    test_results = requests.get('https://192.168.56.70:6443/api/v1/namespaces/default/pods', headers={'Authorization': 'Bearer ' + str(SA_TOKEN)},
                                        verify=False)

    return (test_results.text, test_results.status_code, test_results.headers.items())


@app.route('/')
def main():
    try:
        return render_template('index.html', theme='blue', app_name=APP_NAME, backgroundcolor='#2980b9')
    except Exception as ex:
        print(str(ex))


if __name__ == "__main__":

    if os.path.exists(SA_TOKEN_PATH):
        f = open(SA_TOKEN_PATH, "r")
        SA_TOKEN_FROM_PATH = f.read()
    app.run(host="0.0.0.0", port=8080)