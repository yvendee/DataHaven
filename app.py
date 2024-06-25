from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
import json

app = Flask("datahaven")
CORS(app)

# MySQL database configuration
db_connection = mysql.connector.connect(
    host="sql12.freesqldatabase.com",
    user="sql12715931",
    password="tuUtrAMGZK",
    database="sql12715931",
    port=3306
)

# Function to create a cursor
def get_cursor():
    return db_connection.cursor()

# Initialize the table 'datahaven' if not exists
def initialize_table():
    cursor = get_cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datahaven (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            value TEXT
        )
    """)
    db_connection.commit()
    cursor.close()

# Initialize the table on startup
initialize_table()

# Route to handle POST requests for sending data to MySQL
@app.route('/sendData', methods=['POST'])
def log_post_request():
    try:
        data = json.loads(request.get_data().decode('utf-8'))
        name = data.get('full_name')
        value = data.get('calendar', {}).get('calendarName', '').split(' - ')[0]

        cursor = get_cursor()
        sql_insert_data = "INSERT INTO datahaven (name, value) VALUES (%s, %s)"
        cursor.execute(sql_insert_data, (name, value))
        db_connection.commit()
        cursor.close()

        return 'Data inserted successfully into MySQL!', 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to handle GET requests for retrieving data from MySQL
@app.route('/getData', methods=['POST'])
def get_post_request():
    try:
        data = json.loads(request.get_data().decode('utf-8'))
        full_name = data.get('full_name')

        cursor = get_cursor()
        sql_get_data = "SELECT value FROM datahaven WHERE name = %s"
        cursor.execute(sql_get_data, (full_name,))
        results = cursor.fetchall()
        cursor.close()

        if results:
            return jsonify([result[0] for result in results]), 200
        else:
            return jsonify({"error": "Data not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to handle deleting data by full name from MySQL
@app.route('/deleteData', methods=['POST'])
def delete_data_by_full_name_post():
    try:
        data = json.loads(request.get_data().decode('utf-8'))
        name = data.get('full_name')
        value = data.get('calendar', {}).get('calendarName', '').split(' - ')[0]

        # Connect to MySQL and create cursor
        cursor = get_cursor()

        # Retrieve the id using name and value
        sql_select_id = "SELECT id FROM datahaven WHERE name = %s AND value = %s"
        cursor.execute(sql_select_id, (name, value))
        result = cursor.fetchone()

        if result:
            field_id = result[0]

            # Delete the record using id
            sql_delete_data = "DELETE FROM datahaven WHERE id = %s"
            cursor.execute(sql_delete_data, (field_id,))
            db_connection.commit()
            cursor.close()

            return 'Data deleted successfully from MySQL!', 200
        else:
            cursor.close()
            return jsonify({"error": "Record not found in the database"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to handle insert data 
@app.route('/postData', methods=['POST'])
def log_testpost_request():
    try:
        data = json.loads(request.get_data().decode('utf-8'))
        name = data.get('full_name')
        value = data['calendar']['calendarName']  # Accessing 'calendarName' directly from 'calendar'

        cursor = get_cursor()
        sql_insert_data = "INSERT INTO datahaven (name, value) VALUES (%s, %s)"
        cursor.execute(sql_insert_data, (name, value))
        db_connection.commit()
        cursor.close()

        return 'Data inserted successfully into MySQL!', 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

        return jsonify({"error": str(e)}), 500


@app.route('/readData')
def read_data():
    try:
        cursor = get_cursor()
        sql_select_all = "SELECT * FROM datahaven"
        cursor.execute(sql_select_all)
        data = cursor.fetchall()
        cursor.close()

        return render_template('read_data.html', field_db=data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the datahaven API"})

if __name__ == '__main__':
    app.run(debug=True)
