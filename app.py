from flask import Flask, jsonify
from rekomendasi_buku import rekomendasi_buku_member

app = Flask(__name__)

@app.route("/recommend/<int:member_id>", methods=["GET"])
def recommend(member_id):
    hasil, status = rekomendasi_buku_member(member_id, top_n=10)

    if hasil is None or hasil.empty:
        return jsonify({
            "status": "error",
            "message": status,
            "data": []
        }), 404

    # Convert DataFrame → JSON
    data_rekom = hasil.to_dict(orient="records")

    return jsonify({
        "status": "success",
        "message": status,
        "member_id": member_id,
        "results": data_rekom
    })

# Gunicorn will run this (CMD in Dockerfile)
# No need for app.run() here
