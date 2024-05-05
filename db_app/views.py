from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect

import mysql.connector
from datetime import date


#Connect with the precise info
mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="2652",
  database="volleydb",
)

#from team_id return players and positions as a dictionary
def player_position_from_team_id(team_id):
    cursor = mydb.cursor()
    #inner join query to get player names and positions
    inner_join_query = """SELECT player.name
    FROM player 
    INNER JOIN playerteams ON playerteams.username = player.username
    WHERE playerteams.team = %s"""
    cursor.execute(inner_join_query, (team_id,))
    players = cursor.fetchall()
    players_and_positions = {}
    for player in players:
        player_name = player[0]
        query = """SELECT playerpositions.position
    FROM player 
    INNER JOIN playerpositions ON playerpositions.username = player.username
    WHERE player.name = %s"""
        cursor.execute(query, (player_name,))
        positions = cursor.fetchall()
        positions = [position[0] for position in positions]
        players_and_positions[player_name] = positions
    return players_and_positions


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

    player_positions = player_position_from_team_id(team_id)

    
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
    
    if request.method == 'POST' and 'create_squad' in request.POST:
        
        selected_players = request.POST.getlist('selected_players')  # Get list of selected player names
        player_positions = {}  # Dictionary to store selected player positions

        # Loop through selected players and extract their positions
        for player_name in selected_players:
            position = request.POST.get(f'{player_name}_position')  # Get selected position for the player
            if position:
                player_positions[player_name] = position

        # Now you have a dictionary of selected player positions

        


        # Query to get the squad_ID of the last row
        query_last_squad_id = "SELECT squad_ID FROM sessionsquads ORDER BY squad_ID DESC LIMIT 1"
        cursor.execute(query_last_squad_id)
        last_squad_id = cursor.fetchone()

        # Increment the last squad_ID by one
        if last_squad_id:
            squad_id = last_squad_id[0]
        else:
            # If there are no existing rows, start squad_ID from 1
            squad_id = 0

        
        # Query to get the session_ID of the last row
        query_last_session_id = "SELECT session_ID FROM matchsession WHERE team_ID = %s ORDER BY session_ID DESC LIMIT 1"
        cursor.execute(query_last_session_id, (team_id,))
        last_session_id = cursor.fetchone()[0]

        # Insert the new squad into the database
        for player_name, position in player_positions.items():

            # get player username from player name
            query = "SELECT username FROM player WHERE name = %s"
            cursor.execute(query, (player_name,))
            player_username = cursor.fetchone()[0]

            squad_id += 1
            query = "INSERT INTO sessionsquads (squad_ID, session_ID, played_player_username, position_ID) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (squad_id, last_session_id, player_username, position))
            mydb.commit()
            

        
        
        # Redirect or render the response
        return redirect('coach_dashboard')  # Redirect to the same page after processing the data

     
    return render(request, 'coach_dashboard.html', {'username': username, 'team_id': team_id, 'stadiums': stadiums, 'player_positions': player_positions})

def jury_dashboard(request):
    username = request.session.get('username')
    cursor = mydb.cursor()
    query = """
        SELECT 
            AVG(rating) AS average_rating,
            COUNT(rating) AS total_rated_sessions
        FROM 
            matchsession
        WHERE 
            assigned_jury_username = %s
    """
    cursor.execute(query, (username,))
    data = cursor.fetchone()
    average_rating = data[0]
    count = data[1]


    # Get the current date
    today = date.today()
    reformatted_date = today.strftime("%d.%m.%Y")
    # compare the date with the date of the session in the query
    query_assigned_sessions = """SELECT session_ID, team_ID, stadium_name, time_slot, date
    FROM matchsession 
    WHERE assigned_jury_username = %s AND rating IS NULL AND STR_TO_DATE(date, '%d.%m.%Y') < STR_TO_DATE(%s, '%d.%m.%Y')"""
    cursor.execute(query_assigned_sessions, (username, reformatted_date,))
    assigned_sessions = cursor.fetchall()
    assigned_sessions = [list(session) for session in assigned_sessions]
    session_ids = [session[0] for session in assigned_sessions]
    print(assigned_sessions)

    if request.method == 'POST' and 'rate_sessions' in request.POST:
        # Get the list of ratings submitted by the user
        ratings = request.POST.getlist('ratings[]')

        # Iterate through each rating and its corresponding session ID
        for session_id, rating in zip(session_ids, ratings):
            # Ensure that the rating is not empty
            if rating:
                # Insert or update the rating in the database for the corresponding session ID
                query_update_rating = "UPDATE matchsession SET rating = %s WHERE session_ID = %s"
                cursor.execute(query_update_rating, (rating, session_id))
                mydb.commit()

        # Redirect back to the jury dashboard
        return redirect('jury_dashboard')


    return render(request, 'jury_dashboard.html', {'username': username, 'average_rating': average_rating, 'count': count, 'assigned_sessions': assigned_sessions})

def player_dashboard(request):
    username = request.session.get('username')
    team_mates_query = """SELECT DISTINCT player.name, player.surname
    FROM sessionsquads
    INNER JOIN player ON sessionsquads.played_player_username = player.username
    WHERE sessionsquads.session_id IN (
        SELECT DISTINCT session_id
        FROM sessionsquads
        WHERE played_player_username = %s
    )
    AND player.username != %s

    """

    cursor = mydb.cursor()
    cursor.execute(team_mates_query, (username, username))
    team_mates = cursor.fetchall()
    team_mates = [f"{team_mate[0]} {team_mate[1]}" for team_mate in team_mates]

    most_played_player_height_query = """SELECT AVG(player.height) AS average_height
    FROM (
        SELECT played_player_username, COUNT(*) AS play_count
        FROM sessionsquads
        WHERE session_id IN (
            SELECT DISTINCT session_id
            FROM sessionsquads
            WHERE played_player_username = 'g_orge'
        )
        AND played_player_username != 'g_orge'
        GROUP BY played_player_username
        HAVING play_count = (
            SELECT MAX(play_count)
            FROM (
                SELECT COUNT(*) AS play_count
                FROM sessionsquads
                WHERE session_id IN (
                    SELECT DISTINCT session_id
                    FROM sessionsquads
                    WHERE played_player_username = 'g_orge'
                )
                AND played_player_username != 'g_orge'
                GROUP BY played_player_username
            ) AS max_counts
        )
    ) AS most_played_players
    INNER JOIN player ON most_played_players.played_player_username = player.username
    """

    cursor.execute(most_played_player_height_query)
    data = cursor.fetchone()
    average_height = data[0]



    return render(request, 'player_dashboard.html', {'username': username, 'team_mates': team_mates, 'average_height': average_height})