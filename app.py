
from flask import Flask, render_template, request, jsonify
import uuid, datetime

app = Flask(__name__)
workflows = {}
runs = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/workflows", methods=["GET","POST"])
def workflow_list():
    if request.method=="POST":
        data=request.json or {}
        wid=str(uuid.uuid4())[:8]
        workflows[wid]={
            "id":wid,
            "name":data.get("name","New Workflow"),
            "nodes":data.get("nodes",[])
        }
        return jsonify(workflows[wid])
    return jsonify(list(workflows.values()))

@app.route("/api/workflows/<wid>", methods=["GET","PUT","DELETE"])
def workflow_item(wid):
    if wid not in workflows:
        return jsonify({"error":"not found"}),404
    if request.method=="GET":
        return jsonify(workflows[wid])
    if request.method=="PUT":
        data=request.json or {}
        workflows[wid]["name"]=data.get("name", workflows[wid]["name"])
        workflows[wid]["nodes"]=data.get("nodes", workflows[wid]["nodes"])
        return jsonify(workflows[wid])
    del workflows[wid]
    return jsonify({"ok":True})

@app.route("/api/run/<wid>", methods=["POST"])
def run(wid):
    wf=workflows.get(wid)
    if not wf:
        return jsonify({"error":"not found"}),404
    output=[]
    for node in wf["nodes"]:
        t=node.get("type")
        if t=="input":
            output.append(node.get("value",""))
        elif t=="llm":
            text=" ".join(output)
            output=[f"AI Response: {text[::-1]}"]
        elif t=="webhook":
            output.append("Webhook executed")
    run={
        "id":str(uuid.uuid4())[:8],
        "workflow_id":wid,
        "time":datetime.datetime.utcnow().isoformat(),
        "result":" | ".join(output)
    }
    runs.append(run)
    return jsonify(run)

@app.route("/api/runs")
def run_list():
    return jsonify(runs[::-1])

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
