from flask import Flask, request, jsonify, render_template
from sympy import symbols, Eq, solve, simplify
from sympy.parsing.sympy_parser import parse_expr
import re

app = Flask(__name__)

def rearrange_equation(equation: str, target: str):
    try:
        if not equation or "=" not in equation:
            return {"error": "Equation must contain '=' sign."}, 400

        if not re.match(r"^[A-Za-z0-9_\+\-\*/\^\(\)=\. ]+$", equation):
            return {"error": "Invalid characters in equation."}, 400

        equation = equation.replace("^", "**").replace(" ", "")
        left, right = equation.split("=")

        all_symbols = set(re.findall(r"[a-zA-Z_]+", equation))
        if target not in all_symbols:
            return {"error": f"'{target}' not found in equation."}, 400

        all_syms = symbols(list(all_symbols))

        try:
            left_expr = parse_expr(left)
            right_expr = parse_expr(right)
        except Exception as e:
            return {"error": f"Failed to parse equation: {str(e)}"}, 400

        eq = Eq(left_expr, right_expr)
        target_symbol = symbols(target)

        try:
            sol = solve(eq, target_symbol)
        except Exception as e:
            return {"error": f"Could not solve equation: {str(e)}"}, 400

        if not sol:
            return {"error": f"No solution found for '{target}'."}, 400

        simplified = simplify(sol[0])
        return {"result": f"{target} = {simplified}"}, 200

    except Exception as e:
        return {"error": f"Unexpected server error: {str(e)}"}, 500


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/rearrange", methods=["POST"])
def rearrange():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body."}), 400

    equation = data.get("equation")
    target = data.get("target")

    if not equation or not target:
        return jsonify({"error": "Both 'equation' and 'target' are required."}), 400

    result, status = rearrange_equation(equation, target)
    return jsonify(result), status


if __name__ == "__main__":
    app.run(debug=True)
