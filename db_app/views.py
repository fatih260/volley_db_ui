from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect

import mysql.connector

#Connect with the precise info
mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="2652",
  database="volleydb",
)

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        request.session['username'] = username
        password = request.POST.get('password')
        # check if the user is in the database
         # Create a cursor object to execute SQL queries
        cursor = mydb.cursor(dictionary=True)

        # Query to check if the user exists and retrieve user data
        query = "SELECT * FROM dbmanager WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            # Redirect to a dashboard or homepage
            return redirect('db_admin_dashboard')
        

        query = "SELECT * FROM player WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            # Redirect to a dashboard or homepage
            return redirect('player_dashboard')
        

        
        query = "SELECT * FROM coach WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            # Redirect to a dashboard or homepage
            return redirect('coach_dashboard')
        

        
        query = "SELECT * FROM jury WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            # Redirect to a dashboard or homepage
            return redirect('jury_dashboard')


        # User does not exist or invalid credentials, return an error message
        error_message = "Invalid username or password. Please try again."
        return render(request, 'login.html', {'error_message': error_message})


    return render(request, 'login.html')


def db_admin_dashboard(request):
    username = request.session.get('username')
    print("username: ", username)
    if request.method == 'POST' and 'update_stadium' in request.POST:
        
        # Process stadium update form
        old_name = request.POST.get('old_name')
        new_name = request.POST.get('new_name')

        cursor = mydb.cursor()

        # Update stadium names
        query = "UPDATE matchsession SET stadium_name = %s WHERE stadium_name = %s"
        cursor.execute(query, (new_name, old_name))
        mydb.commit()

        return redirect('db_admin_dashboard')
        

    return render(request, 'db_admin_dashboard.html', {'username': username})

def player_dashboard(request):
    return render(request, 'player_dashboard.html')


def coach_dashboard(request):
    username = request.session.get('username')
    cursor = mydb.cursor()
    query_for_team_id = "SELECT team_ID FROM team WHERE coach_username = %s"
    cursor.execute(query_for_team_id, (username,))
    team_id = cursor.fetchone()[0]

    # get existing stadium names and countries
    query_stadium = "SELECT stadium_name, stadium_country FROM stadium"
    cursor.execute(query_stadium)
    stadiums = cursor.fetchall()

    
    if request.method == 'POST' and 'delete_session' in request.POST:
        session_id = request.POST.get('session_id')
        
        # Delete the match session and related data
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM matchsession WHERE session_id = %s", (session_id,))
        cursor.execute("DELETE FROM sessionsquads WHERE session_id = %s", (session_id,))
        
        # Commit the changes to the database
        mydb.commit()
        
        # Redirect back to the coach dashboard
        return redirect('coach_dashboard')

    if request.method == 'POST' and 'add_match_session' in request.POST:


        # Process match session form
        
        stadium_name = request.POST.get('stadium_name')
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        jury_name = request.POST.get('jury_name')
        jury_surname = request.POST.get('jury_surname')

        cursor = mydb.cursor()

        # first get stadium id and country from stadium name
        query = "SELECT stadium_id, stadium_country FROM stadium WHERE stadium_name = %s"
        cursor.execute(query, (stadium_name,))
        stadium_data = cursor.fetchone()
        stadium_id = stadium_data[0]
        stadium_country = stadium_data[1]


        # Query to get the session_ID of the last row
        query_last_session_id = "SELECT session_ID FROM matchsession ORDER BY session_ID DESC LIMIT 1"
        cursor.execute(query_last_session_id)
        last_session_id = cursor.fetchone()

        # Increment the last session ID by one
        if last_session_id:
            session_id = last_session_id[0] + 1
        else:
            # If there are no existing rows, start session_ID from 1
            session_id = 1

        # Query to get the username of the jury
        query_jury_username = "SELECT username FROM jury WHERE name = %s AND surname = %s"
        cursor.execute(query_jury_username, (jury_name, jury_surname))
        jury_username = cursor.fetchone()[0]

        # Extract day, month, and year from the date string
        year, month, day = date.split('-')
        # Reformat the date string as DD.MM.YYYY
        formatted_date = f"{day}.{month}.{year}"


        # Insert the new match session into the database
        query = "INSERT INTO matchsession (session_ID, team_ID, stadium_ID, stadium_name, stadium_country, time_slot, date, assigned_jury_username, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL)"
        cursor.execute(query, (session_id, team_id, stadium_id, stadium_name, stadium_country, time_slot, formatted_date, jury_username))
        mydb.commit()

        
        # Redirect back to the coach dashboard
        return redirect('coach_dashboard')    
    

    return render(request, 'coach_dashboard.html', {'username': username, 'team_id': team_id, 'stadiums': stadiums})

def jury_dashboard(request):
    return render(request, 'jury_dashboard.html')
