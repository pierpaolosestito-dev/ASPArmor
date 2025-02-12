from flask import Flask, render_template, request
import clingo

app = Flask(__name__)

def run_clingo(program):
    output = []

    def on_model(model):
        output.append(f"Soluzione: {', '.join(str(atom) for atom in model.symbols(atoms=True))}")

    ctl = clingo.Control()
    ctl.add("base", [], program)
    ctl.ground([("base", [])])
    ctl.solve(on_model=on_model)

    return "\n".join(output) if output else "Nessuna soluzione trovata."

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
