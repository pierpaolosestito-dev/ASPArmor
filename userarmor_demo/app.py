from flask import Flask, render_template, request
import subprocess
import os

prefix = os.getenv("CLINGO_PREFIX", "")

app = Flask(__name__)


def run_clingo(program):
    return subprocess.run(["sh", "-c", f"{prefix} clingo"], input=program, text=True, capture_output=True).stdout


@app.route('/', methods=['GET', 'POST'])
def home():
    output = ""
    if request.method == 'POST':
        textarea_content = request.form['textarea']
        try:
            output = run_clingo(textarea_content)
        except Exception as e:
            output = f"Errore nell'esecuzione di Clingo: {str(e)}"

    return render_template('index.html', output=output)


if __name__ == "__main__":
    app.run(debug=True)
