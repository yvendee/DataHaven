from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector

app = Flask("datahaven")
CORS(app)

# MySQL database configuration
db_connection = mysql.connector.connect(
    host="1y1.h.filess.io",
    user="datahaven_according",
    password="274f26f7138d3389dcb8a7afac6f10c6dc593d84",
    database="datahaven_according",
    port=3307
)

# Function to create a cursor
def get_cursor():
    return db_connection.cursor()

# Check if table exists function
def table_exists(table_name):
    cursor = get_cursor()
    cursor.execute("SHOW TABLES LIKE %s", (table_name,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None

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

# Route to create the 'datahaven' table if it doesn't exist
@app.route('/createdb', methods=['GET'])
def create_db():
    try:
        if not table_exists('datahaven'):
            cursor = get_cursor()
            sql_create_table = """
            CREATE TABLE datahaven (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                value TEXT
            );
            """
            cursor.execute(sql_create_table)
            db_connection.commit()
            cursor.close()
            return 'Table "datahaven" created successfully.', 200
        else:
            return 'Table "datahaven" already exists.', 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to insert mock-up data into the 'datahaven' table
@app.route('/insertmockupdata', methods=['GET'])
def insert_mockup_data():
    try:
        data_to_insert = [
            (1, "JohnDoe", "Clarifying Facial"),
            (2, "BobMartin", "Snow Facial"),
            (3, "JohnDoe", "Glycolic Express Facial")
        ]

        cursor = get_cursor()

        for item in data_to_insert:
            sql_insert_data = "INSERT INTO datahaven (id, name, value) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert_data, item)

        db_connection.commit()
        cursor.close()

        return 'Mock-up data inserted successfully into MySQL!', 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to handle POST requests for sending data to MySQL
@app.route('/sendData', methods=['POST'])
def log_post_request():
    try:
        data = request.json  # Assuming data is sent as JSON
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
        data = request.json  # Assuming data is sent as JSON
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

# @app.route('/getData', methods=['POST'])
# def get_post_request():
#     try:
#         data = request.json  # Assuming data is sent as JSON
#         full_name = data.get('full_name')

#         if not full_name:
#             return jsonify({"error": "Full name is required"}), 400

#         cursor = get_cursor()
#         sql_get_data = "SELECT value FROM datahaven WHERE name = %s"
#         cursor.execute(sql_get_data, (full_name,))
#         results = cursor.fetchall()
        
#         cursor.close()

#         if results:
#             return jsonify([result[0] for result in results]), 200
#         else:
#             return jsonify({"error": "Data not found"}), 404

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# Route to handle deleting data by full name from MySQL
@app.route('/deleteData', methods=['POST'])
def delete_data_by_full_name_post():
    try:
        data = request.json  # Assuming data is sent as JSON
        name = data.get('full_name')
        value = data.get('calendar', {}).get('calendarName', '').split(' - ')[0]

        cursor = get_cursor()

        sql_select_id = "SELECT id FROM datahaven WHERE name = %s AND value = %s"
        cursor.execute(sql_select_id, (name, value))
        result = cursor.fetchone()

        if result:
            field_id = result[0]

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
        data = request.json  # Assuming data is sent as JSON
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
