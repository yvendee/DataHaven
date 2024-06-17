from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask("datahaven")
CORS(app)



# List to store fields, each represented as [id, name, value]
field_db = []

# Initialize the list with some initial data
field_db.append([1, "JohnDoe", "Clarifying Facial"])
field_db.append([2, "BobMartin", "Snow Facial"])
field_db.append([3, "JohnDoe", "Glycolic Express Facial"])


# Function to generate unique field ID
def get_next_field_id():
    return len(field_db) + 1

# Route to handle POST requests for sending data
@app.route('/sendData', methods=['POST'])
def log_post_request():
    # Get the JSON data from the request
    data = json.loads(request.get_data().decode('utf-8'))
    
    # Extract values from the fields
    full_name = data.get('full_name')

    # Extract the calendarName from the data
    calendar_name = data.get('calendar', {}).get('calendarName')
    
    if calendar_name is not None:
        # Remove the cost from contact_source
        contact_source_without_cost = calendar_name.split(' - ')[0]
    else:
        contact_source_without_cost = None

    full_name = full_name.replace(" ", "")

    # Insert data into field_db list
    field_id = get_next_field_id()
    new_field = [field_id, full_name, contact_source_without_cost]
    field_db.append(new_field)
    
    # Return a response
    return 'Received and logged the POST request successfully!', 200

# Route to handle GET requests for retrieving data by fullname
@app.route('/getData', methods=['POST'])
def get_post_request():
    # Get the JSON data from the request
    data = json.loads(request.get_data().decode('utf-8'))
    
    # Extract fullname from the request
    full_name = data.get('full_name')
    
    # Retrieve contact sources by fullname from field_db list
    contact_sources = [field[2] for field in field_db if field[1].lower() == full_name.lower()]
    
    if contact_sources:
        return jsonify(contact_sources), 200
    else:
        return jsonify({"error": "Field not found"}), 404

# Route to handle GET requests for retrieving all data from field_db list
@app.route('/readData')
def read_data():
    # Return all data from field_db list
    return jsonify(field_db), 200


@app.route('/deleteData', methods=['POST'])
def delete_data_by_full_name_post():
    # Get the JSON data from the request
    data = json.loads(request.get_data().decode('utf-8'))
    
    # Extract full_name from the request
    full_name = data.get('full_name')
    
    # Delete all entries matching the full_name from field_db
    global field_db
    initial_length = len(field_db)
    field_db = [field for field in field_db if field[1].lower() != full_name.lower()]
    deleted_count = initial_length - len(field_db)
    
    if deleted_count > 0:
        return jsonify({"message": f"Deleted {deleted_count} entries for {full_name}"}), 200
    else:
        return jsonify({"error": f"No entries found for {full_name}"}), 404

        
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the datahaven API"})

if __name__ == '__main__':
    app.run(debug=True)
