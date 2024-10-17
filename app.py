from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Webex API base URL
WEBEX_API_BASE = 'https://webexapis.com/v1'

def get_user_info(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{WEBEX_API_BASE}/people/me', headers=headers)
    if response.status_code == 200:
        return response.json()  # user information
    else:
        return None  # Invalid token

def get_rooms(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{WEBEX_API_BASE}/rooms', headers=headers)
    if response.status_code == 200:
        return response.json().get('items', [])  # List of rooms
    else:
        return None

def send_message_to_room(access_token, room_id, message):
    headers = {'Authorization': f'Bearer {access_token}'}
    message_data = {'roomId': room_id, 'text': message}
    response = requests.post(f'{WEBEX_API_BASE}/messages', headers=headers, json=message_data)
    return response.status_code == 200  

# Routes
@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        # Option 1: User submits Webex token
        access_token = request.form.get('access_token')
        user_info = get_user_info(access_token)
        
        if user_info:
            # If token is valid, render user information (Option 1)
            return render_template('user_info.html', user_info=user_info, access_token=access_token)
        else:
            # Invalid token
            return "Invalid Access Token. Please try again.", 400
    
    return render_template('index.html')

@app.route('/rooms/<access_token>', methods=['GET', 'POST'])
def rooms(access_token):
    # Option 2: Display list of rooms
    rooms = get_rooms(access_token)
    
    if rooms is not None:
        if request.method == 'POST':
            # Option 4: If a message is sent to a room
            room_id = request.form['room_id']
            message = request.form['message']
            if send_message_to_room(access_token, room_id, message):
                flash(f"Message sent to room {room_id} successfully!")
            else:
                flash("Failed to send the message. Please try again.")
        
        return render_template('rooms.html', rooms=rooms, access_token=access_token)
    
    return "Failed to retrieve rooms.", 400

@app.route('/create_room/<access_token>', methods=['POST'])
def create_room(access_token):
    # Option 3: Create a room
    room_title = request.form['room_title']
    headers = {'Authorization': f'Bearer {access_token}'}
    data = {'title': room_title}
    response = requests.post(f'{WEBEX_API_BASE}/rooms', headers=headers, json=data)

    if response.status_code == 200:
        flash('Room created successfully!')
    else:
        flash('Failed to create a room. Please try again.')
    
    return redirect(url_for('rooms', access_token=access_token))

@app.route('/test_connection/<access_token>', methods=['GET'])
def test_connection(access_token):
    # Option 0: Test connection with Webex server
    user_info = get_user_info(access_token)
    if user_info:
        flash('Connection successful!')
        return redirect(url_for('index'))  # Redirect to the main menu 
    else:
        flash('Failed to connect Webex API. Invalid Token.')
        return redirect(url_for('index'))  # Redirect to the main menu

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
