from flask import Flask, request, jsonify
import json
import sqlite3

app = Flask(__name__)

# Function to create a connection to SQLite database
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

# Function to insert data into SQLite database
def insert_data(conn, full_name, contact_source):
    sql = ''' INSERT INTO contacts(fullname, contact_source)
              VALUES(?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, (full_name, contact_source))
    conn.commit()
    return cur.lastrowid

# Function to retrieve all data from the contacts table
def get_all_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM contacts")
    rows = cur.fetchall()
    return rows

# Function to retrieve contact sources associated with a given full name
def get_contact_sources_by_fullname(conn, full_name):
    cur = conn.cursor()
    cur.execute("SELECT contact_source FROM contacts WHERE fullname=?", (full_name,))
    rows = cur.fetchall()
    # Extract contact sources from fetched rows
    contact_sources = [row[0] for row in rows]
    return contact_sources
    
# # Before request handler to log incoming requests
# @app.before_request
# def log_request_info():
#     print(f'Request URL: {request.url}')
#     print(f'Request Method: {request.method}')
#     print(f'Request Headers: {request.headers}')
#     print(f'Request Body: {request.get_data()}')

# Route to handle POST requests for sending data
@app.route('/sendData', methods=['POST'])
def log_post_request():
    # Get the JSON data from the request
    data = json.loads(request.get_data().decode('utf-8'))
    
    # Extract values from the fields
    full_name = data.get('full_name')
    contact_source = data.get('contact_source')
    
    if contact_source is not None:
        # Remove the cost from contact_source
        contact_source_without_cost = contact_source.split(' - ')[0]
    else:
        contact_source_without_cost = None

    # print("------ Data Extracted ------")
    # print(full_name)
    # print(contact_source_without_cost)

    full_name = full_name.replace(" ", "")

    # # Log the data to a file
    # with open('log.txt', 'a') as f:
    #     f.write(json.dumps(data) + '\n')
    
    # Insert data into SQLite database
    conn = create_connection('contacts.db')
    if conn is not None:
        insert_data(conn, full_name, contact_source_without_cost)
        conn.close()
        print("Data inserted into SQLite database successfully!")
    else:
        print("Error! Cannot create database connection.")
    
    # Return a response
    return 'Received and logged the POST request successfully!', 200

# Route to handle GET requests for retrieving data by fullname
@app.route('/getData', methods=['POST'])
def get_post_request():
    # Get the JSON data from the request
    data = json.loads(request.get_data().decode('utf-8'))
    
    # Extract fullname from the request
    full_name = data.get('full_name')
    
    # Create a connection to SQLite database
    conn = create_connection('contacts.db')
    if conn is not None:
        # Retrieve contact sources by fullname
        cur = conn.cursor()
        cur.execute("SELECT contact_source FROM contacts WHERE fullname=?", (full_name,))
        rows = cur.fetchall()
        # Extract contact sources from fetched rows
        contact_sources = [row[0] for row in rows]
        conn.close()
        # Return contact sources as JSON response
        return jsonify(contact_sources), 200
    else:
        return "Error! Cannot create database connection.", 500


# Route to handle GET requests for retrieving all data from contacts table
@app.route('/readData')
def read_data():
    # Create a connection to SQLite database
    conn = create_connection('contacts.db')
    if conn is not None:
        # Retrieve all data from the contacts table
        all_data = get_all_data(conn)
        conn.close()
        # Convert data to JSON format and return as response
        return jsonify(all_data), 200
    else:
        return "Error! Cannot create database connection.", 500

if __name__ == '__main__':
    app.run(debug=True)
