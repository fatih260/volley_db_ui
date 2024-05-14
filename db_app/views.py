from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from mysql.connector import Error as MySQLError

# Create your views here.
from django.shortcuts import render, redirect

import mysql.connector
from datetime import date, datetime

def convert_date(date_str):
    # Convert string date in format dd.mm.yyyy to datetime object
    return datetime.strptime(date_str, '%d.%m.%Y')

#Connect with the precise info
mydb = mysql.connector.connect(
  host="127.0.0.1",
  user="root",
  password="2652",
  database="volleydb",
  buffered = True
)
def get_stadiums():
    print("get stadiums")
    cursor = mydb.cursor()
    query_stadium = "SELECT stadium_name, stadium_country FROM stadium"
    cursor.execute(query_stadium)
    stadiums = cursor.fetchall()
    cursor.close()
    print(stadiums)
    return stadiums

def get_teams():
    cursor = mydb.cursor()
    query_teams = "SELECT team_ID, team_name FROM team WHERE STR_TO_DATE(contract_finish, '%d.%m.%Y') > CURDATE() AND STR_TO_DATE(contract_start, '%d.%m.%Y') < CURDATE()"
    cursor.execute(query_teams)
    teams = cursor.fetchall()
    cursor.close()
    return teams

def get_positions():
    cursor = mydb.cursor()
    query_positions = "SELECT position_ID, position_name FROM position"
    cursor.execute(query_positions)
    positions = cursor.fetchall()
    cursor.close()
    return positions

def get_jury_names_surnames():
    cursor = mydb.cursor()
    query_jury = "SELECT name, surname FROM jury"
    cursor.execute(query_jury)
    jury = cursor.fetchall()
    cursor.close()
    return jury

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
    cursor.close()

    players_and_positions = {}
    for player in players:
        cursor = mydb.cursor()
        player_name = player[0]
        query = """SELECT playerpositions.position
    FROM player 
    INNER JOIN playerpositions ON playerpositions.username = player.username
    WHERE player.name = %s"""
        cursor.execute(query, (player_name,))
        positions = cursor.fetchall()
        cursor.close()
        positions = [position[0] for position in positions]
        players_and_positions[player_name] = positions
    return players_and_positions

def home(request):
    return render(request, 'home.html')


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
        cursor.close()

        if user:
            # Redirect to a dashboard or homepage
            return redirect('db_admin_dashboard')
        
        cursor = mydb.cursor()
        query = "SELECT * FROM player WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Redirect to a dashboard or homepage
            return redirect('player_dashboard')
        

        cursor = mydb.cursor()
        query = "SELECT * FROM coach WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Redirect to a dashboard or homepage
            return redirect('coach_dashboard')
        

        cursor = mydb.cursor()        
        query = "SELECT * FROM jury WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Redirect to a dashboard or homepage
            return redirect('jury_dashboard')


        # User does not exist or invalid credentials, return an error message
        error_message = "Invalid username or password. Please try again."
        return render(request, 'login.html', {'error_message': error_message})


    return render(request, 'login.html')


def db_admin_dashboard(request):
    username = request.session.get('username')

    teams = get_teams()
    positions = get_positions()
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
        cursor.close()

        cursor = mydb.cursor()
        query_stadium = "UPDATE stadium SET stadium_name = %s WHERE stadium_name = %s"
        cursor.execute(query_stadium, (new_name, old_name))
        mydb.commit()
        cursor.close()

        return redirect('db_admin_dashboard')
    
    if request.method == 'POST' and 'add_user' in request.POST:
        
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        
        if user_type == 'player':
            team_id = request.POST.get('team')
            position_id = request.POST.get('position')
            height = request.POST.get('height')
            weight = request.POST.get('weight')
            date_of_birth = request.POST.get('date_of_birth')

            # Process adding a new player
            # Insert the new player into the database
            # You can use the provided information (username, password, name, surname, team_id, position_id, height, weight, date_of_birth) to insert into the players table

            cursor = mydb.cursor()
            query_player = "INSERT INTO player (username, password, name, surname, date_of_birth, height, weight) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query_player, (username, password, name, surname, date_of_birth, height, weight))
            mydb.commit()
            cursor.close()

            cursor = mydb.cursor()
            # first get the last player_teams_id 
            query_last_player_id = "SELECT player_teams_id FROM playerteams ORDER BY player_teams_id DESC LIMIT 1" 
            cursor.execute(query_last_player_id)
            last_player_id = cursor.fetchone()[0]
            cursor.close()

            cursor = mydb.cursor()
            query_players_teams = "INSERT INTO playerteams (player_teams_id, username, team) VALUES (%s, %s, %s)"
            cursor.execute(query_players_teams, (last_player_id+1, username, team_id))
            mydb.commit()
            cursor.close()


            #first get the last player_positions_id
            cursor = mydb.cursor()
            query_last_player_position_id = "SELECT player_positions_id FROM playerpositions ORDER BY player_positions_id DESC LIMIT 1"
            cursor.execute(query_last_player_position_id)
            last_player_position_id = cursor.fetchone()[0]
            cursor.close()

            cursor = mydb.cursor()
            query_player_positions = "INSERT INTO playerpositions (player_positions_id, username, position) VALUES (%s, %s, %s)"
            cursor.execute(query_player_positions, (last_player_position_id+1, username, position_id))
            mydb.commit()
            cursor.close()


        elif user_type == 'jury' or user_type == 'coach':
            nationality = request.POST.get('nationality')
            cursor = mydb.cursor()
            query_jury = "INSERT INTO jury (username, password, name, surname, nationality) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query_jury, (username, password, name, surname, nationality))
            mydb.commit()
            cursor.close()
            
        # Redirect or render success message

        return redirect('db_admin_dashboard')

    print("positions: ", positions)
    return render(request, 'db_admin_dashboard.html', {'username': username, 'teams': teams, 'positions': positions})



def coach_dashboard(request):
    username = request.session.get('username')
    cursor = mydb.cursor()
    query_for_team_id = """
    SELECT team_ID, contract_start, contract_finish 
    FROM team 
    WHERE coach_username = %s
    """ 
    ## AND STR_TO_DATE(contract_finish, '%d.%m.%Y') > CURDATE() AND STR_TO_DATE(contract_start, '%d.%m.%Y') < CURDATE()
    cursor.execute(query_for_team_id, (username,))
    team_data = cursor.fetchone()

    print(team_data)
    team_id, contract_start, contract_finish = int(team_data[0]), team_data[1], team_data[2]
    cursor.close()

    # get existing stadium names and countries
    stadiums = get_stadiums()

    jury_names_surnames = get_jury_names_surnames()
    jury_names_surnames_list = [f"{name} {surname}" for name, surname in jury_names_surnames]

    player_positions = player_position_from_team_id(team_id)

    
    if request.method == 'POST' and 'delete_session' in request.POST:
        session_id = request.POST.get('session_id')
        
        # Delete the match session and related data
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM matchsession WHERE session_id = %s", (session_id,))
        cursor.execute("DELETE FROM sessionsquads WHERE session_id = %s", (session_id,))
        
        # Commit the changes to the database
        mydb.commit()

        cursor.close()
        
        # Redirect back to the coach dashboard
        return redirect('coach_dashboard')

    if request.method == 'POST' and 'add_match_session' in request.POST:

        if team_id is None:
            error_message = "You do not have an active team. You cannot add a match."
            return render(request, 'coach_dashboard.html', {'username': username, 'team_id': team_id, 'stadiums': stadiums, 'player_positions': player_positions, 'jury_names_surnames': jury_names_surnames_list, 'error_message_os': error_message})

        # Process match session form
        
        stadium_name = request.POST.get('stadium_name')
        print("stadium_name: ", stadium_name)
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        jury_name_surname = request.POST.get('jury_name_surname')
        jury_name = jury_name_surname.split()[0]
        jury_surname = jury_name_surname.split()[1]

        # Extract day, month, and year from the date string
        year, month, day = date.split('-')
        # Reformat the date string as DD.MM.YYYY
        formatted_date = f"{day}.{month}.{year}"

        # Check if the date is within the contract period
        formatted_date_c = convert_date(formatted_date)
        contract_start_c = convert_date(contract_start)
        contract_finish_c = convert_date(contract_finish)

        #compare date with contract_start and contract_finish
        if not (contract_start_c < formatted_date_c and formatted_date_c < contract_finish_c):
            error_message = "The date of the match is not within the contract period."
            return render(request, 'coach_dashboard.html', {'username': username, 'team_id': team_id, 'stadiums': stadiums, 'player_positions': player_positions, 'jury_names_surnames': jury_names_surnames_list, 'error_message_dp': error_message})


        cursor = mydb.cursor()

        # first get stadium id and country from stadium name
        query_stadium_id_country = "SELECT stadium_id, stadium_country FROM stadium WHERE stadium_name = %s"
        cursor.execute(query_stadium_id_country, (stadium_name,))
        stadium_data = cursor.fetchone()
        cursor.close()
        stadium_id = stadium_data[0]
        stadium_country = stadium_data[1]


        # Query to get the session_ID of the last row
        cursor = mydb.cursor()
        query_last_session_id = "SELECT session_ID FROM matchsession ORDER BY session_ID DESC LIMIT 1"
        cursor.execute(query_last_session_id)
        last_session_id = cursor.fetchone()
        cursor.close()

        # Increment the last session ID by one
        if last_session_id:
            session_id = last_session_id[0] + 1
        else:
            # If there are no existing rows, start session_ID from 1
            session_id = 1

        # Query to get the username of the jury
        query_jury_username = "SELECT username FROM jury WHERE name = %s AND surname = %s"

        cursor = mydb.cursor()
        cursor.execute(query_jury_username, (jury_name, jury_surname))
        jury_username = cursor.fetchone()[0]
        cursor.close()

        # Insert the new match session into the database
        query_add_match_session = "INSERT INTO matchsession (session_ID, team_ID, stadium_ID, stadium_name, stadium_country, time_slot, date, assigned_jury_username, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL)"
        cursor = mydb.cursor()
        try:
            cursor.execute(query_add_match_session, (session_id, team_id, stadium_id, stadium_name, stadium_country, time_slot, formatted_date, jury_username))
            mydb.commit()
            cursor.close()
        # Your existing code...
        except MySQLError as e:
            cursor.close()
            error_message_os = "Cannot insert. Overlapping sessions detected."
            return render(request, 'coach_dashboard.html', {'username': username, 'team_id': team_id, 'stadiums': stadiums, 'player_positions': player_positions, 'jury_names_surnames': jury_names_surnames_list, 'error_message_os': error_message_os})
        
        
        
        # Redirect back to the coach dashboard
        return redirect('coach_dashboard')    
    
    if request.method == 'POST' and 'create_squad' in request.POST:
        
        selected_players = request.POST.getlist('selected_players')  # Get list of selected player names

        if len(selected_players) != 6:
            error_message = "Please select exactly 6 players for the squad."
            return render(request, 'coach_dashboard.html', {'username': username, 'team_id': team_id, 'stadiums': stadiums, 'player_positions': player_positions, 'jury_names_surnames': jury_names_surnames_list , 'error_message': error_message})
        
        get_player_positions = {}  # Dictionary to store selected player positions

        # Loop through selected players and extract their positions
        for player_name in selected_players:
            position = request.POST.get(f'{player_name}_position')  # Get selected position for the player
            if position:
                get_player_positions[player_name] = position
            else:
                error_message = "Please select a position for each player."
                return render(request, 'coach_dashboard.html', {'username': username, 'team_id': team_id, 'stadiums': stadiums, 'player_positions': player_positions, 'jury_names_surnames': jury_names_surnames_list, 'error_message': error_message})


        # Query to get the squad_ID of the last row
        query_last_squad_id = "SELECT squad_ID FROM sessionsquads ORDER BY squad_ID DESC LIMIT 1"
        cursor = mydb.cursor()
        cursor.execute(query_last_squad_id)
        last_squad_id = cursor.fetchone()
        cursor.close()

        # Get the last squad ID
        if last_squad_id:
            squad_id = last_squad_id[0]
        else:
            # If there are no existing rows, start squad_ID from 1
            squad_id = 0

        
        # Query to get the session_ID of the last row
        query_last_session_id = "SELECT session_ID FROM matchsession WHERE team_ID = %s ORDER BY session_ID DESC LIMIT 1"
        cursor = mydb.cursor()
        cursor.execute(query_last_session_id, (team_id,))
        last_session_id = cursor.fetchone()[0]
        cursor.close()

        # Insert the new squad into the database
        for player_name, position in get_player_positions.items():

            # get player username from player name
            cursor = mydb.cursor()
            query_player_username = "SELECT username FROM player WHERE name = %s"
            cursor.execute(query_player_username, (player_name,))
            player_username = cursor.fetchone()[0]
            cursor.close()

            cursor = mydb.cursor()
            squad_id += 1
            query_add_session_squad = "INSERT INTO sessionsquads (squad_ID, session_ID, played_player_username, position_ID) VALUES (%s, %s, %s, %s)"    
            try:
                cursor.execute(query_add_session_squad, (squad_id, last_session_id, player_username, position))
                mydb.commit()
                cursor.close()
            except MySQLError as e:
                cursor.close()
                error_message_tc = f"Cannot insert. Player {player_username} has a time conflict"
                query_delete_squad = "DELETE FROM sessionsquads WHERE session_ID = %s"
                cursor = mydb.cursor()
                cursor.execute(query_delete_squad, (last_session_id,))
                mydb.commit()
                cursor.close()
                return render(request, 'coach_dashboard.html', {'username': username, 'team_id': team_id, 'stadiums': stadiums, 'player_positions': player_positions, 'jury_names_surnames': jury_names_surnames_list, 'error_message_tc': error_message_tc})

        
        
        # Redirect or render the response
        return redirect('coach_dashboard')  # Redirect to the same page after processing the data

     
    return render(request, 'coach_dashboard.html', {'username': username, 'team_id': team_id, 'stadiums': stadiums, 'player_positions': player_positions, 'jury_names_surnames': jury_names_surnames_list})

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
    cursor.close()


    # Get the current date
    today = date.today()
    reformatted_date = today.strftime("%d.%m.%Y")
    # compare the date with the date of the session in the query
    query_assigned_sessions = """SELECT session_ID, team_ID, stadium_name, time_slot, date
    FROM matchsession 
    WHERE assigned_jury_username = %s AND rating IS NULL AND STR_TO_DATE(date, '%d.%m.%Y') < STR_TO_DATE(%s, '%d.%m.%Y')"""
    cursor = mydb.cursor()
    cursor.execute(query_assigned_sessions, (username, reformatted_date,))
    assigned_sessions = cursor.fetchall()
    cursor.close()
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
                cursor = mydb.cursor()
                cursor.execute(query_update_rating, (rating, session_id))
                mydb.commit()
                cursor.close()

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
    cursor.close()
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
    cursor = mydb.cursor()
    cursor.execute(most_played_player_height_query)
    data = cursor.fetchone()
    cursor.close()
    average_height = data[0]



    return render(request, 'player_dashboard.html', {'username': username, 'team_mates': team_mates, 'average_height': average_height})