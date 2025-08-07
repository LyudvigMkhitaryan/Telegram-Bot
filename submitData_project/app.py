from flask import Flask, request, jsonify, abort
import sqlite3

app = Flask(__name__)
DB_NAME = 'data.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/submitData/<int:id>', methods=['GET'])
def get_data(id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM submissions WHERE id = ?', (id,)).fetchone()
    conn.close()
    if item is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(dict(item))

@app.route('/submitData/<int:id>', methods=['PATCH'])
def patch_data(id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data"}), 400
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM submissions WHERE id = ?', (id,)).fetchone()
    if item is None:
        conn.close()
        return jsonify({"error": "Not found"}), 404
    if item['status'] != 'new':
        conn.close()
        return jsonify({"error": "Cannot edit, status not 'new'"}), 400

    # Обновляем только поле data и статус (если есть)
    new_data = data.get('data', item['data'])
    new_status = data.get('status', item['status'])

    conn.execute('UPDATE submissions SET data = ?, status = ? WHERE id = ?', (new_data, new_status, id))
    conn.commit()
    updated = conn.execute('SELECT * FROM submissions WHERE id = ?', (id,)).fetchone()
    conn.close()
    return jsonify(dict(updated))

@app.route('/submitData', methods=['GET'])
def get_by_email():
    user_email = request.args.get('user_email')
    if not user_email:
        return jsonify({"error": "user_email query param required"}), 400
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM submissions WHERE user_email = ?', (user_email,)).fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])

@app.route('/submitData', methods=['POST'])
def post_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data"}), 400
    user_email = data.get('user_email')
    data_field = data.get('data')
    status = data.get('status', 'new')
    if not user_email or not data_field:
        return jsonify({"error": "user_email and data fields required"}), 400
    conn = get_db_connection()
    cursor = conn.execute('INSERT INTO submissions (user_email, data, status) VALUES (?, ?, ?)', (user_email, data_field, status))
    conn.commit()
    new_id = cursor.lastrowid
    new_item = conn.execute('SELECT * FROM submissions WHERE id = ?', (new_id,)).fetchone()
    conn.close()
    return jsonify(dict(new_item)), 201

if __name__ == '__main__':
    app.run(debug=True)
