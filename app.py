from flask import Flask, redirect, g, request # importing in necessary libraries
from datetime import date
import psycopg2.pool

app = Flask(__name__, static_folder="public", static_url_path="") # connects to the static files

@app.route('/')
def index(): # directs the route to index file
    return redirect('/index.html')

# Setup our database SimpleConnectionPool
app.config['postgreSQL_pool'] = psycopg2.pool.SimpleConnectionPool(
    1, #min number of connections
    10, #max number of connections
    host = '127.0.0.1', # this is localhost
    port = '5432', # DB port
    database = 'pet_hotel' # Database name
)

# Function to get a connection to the DB, use in each route that needs to access DB
def get_db_conn():
    if 'db' not in g:
        g.db = app.config['postgreSQL_pool'].getconn()
        print('Got connection to DB')
    return g.db    

# close db connections when done
@app.teardown_appcontext
def close_db_conn(taco):
    db = g.pop('db', None)
    if db is not None:
        app.config['postgreSQL_pool'].putconn(db)
        print('Closing connection!')

# Get all pets and add pets routes
@app.route('/pets', methods=['GET', 'POST'])
def petStuff():
    if request.method == 'GET':
        return getPets() # if a GET request call this function
    elif request.method == 'POST': 
        return addPet( request.form ) # if a POST request call this function and pass the object data to the function

# Delete and Put routes
@app.route("/pets/<id>", methods=["DELETE", "PUT"])
def deleteOrPut(id):
    if request.method == 'DELETE':
        return deletePet(id) # if DELETE route - call this function and pass the id to know which to delete
    elif request.method == 'PUT':
        return changeCheckIn(id, request.form['petStatus']) # if PUT route - call this function and pass the id to know which to delete, as well as the status object info - which to change it to

def changeCheckIn(id, petStatus):
    # Get a connection to database, use that to get a cursor
    conn = get_db_conn()
    cursor = conn.cursor()

    if petStatus == 'No': # conditional determines what to change in the DB
        # Database INSERT
        sql = 'UPDATE pets SET checked_in=%s WHERE id =%s;'
        cursor.execute(sql, (date.today().strftime("%b-%d-%Y"), id)) # pass in values as a tupple, which uses ()
    else:
        sql = 'UPDATE pets SET checked_in=%s WHERE id =%s;'
        cursor.execute(sql, ('No', id)) 
    
    # IMPORTANT - commit!!
    conn.commit()
    response = {'msg': 'Pet is checking in or out'}, 201
 
    # IMPORTANT!! - CLOSE the cursor
    cursor.close()

    return response # sends this back to client-side


def deletePet(id):

    # Get a connection to database, use that to get a cursor
    conn = get_db_conn()
    cursor = conn.cursor()

    # TODO Database INSERT
    sql = 'DELETE FROM pets WHERE id =%s;'
    cursor.execute(sql, (id)) # pass in values as a tupple, which uses ()
    
    # IMPORTANT - commit!
    conn.commit()
    response = {'msg': 'Pet is lost or stolen'}, 201
 
    # IMPORTANT!! - CLOSE the cursor
    cursor.close()

    return response

def addPet(animal):
    print('Adding pet', animal)
    
    cursor = None
    response = None

    try:
        # Get a connection to database, use that to get a cursor
        conn = get_db_conn()
        cursor = conn.cursor()

        # TODO Database INSERT
        sql = 'INSERT INTO pets ("pet", "breed", "color", "owner") VALUES (%s, %s, %s, %s);'
        cursor.execute(sql, (animal['pet'], animal['breed'], animal['color'], animal['owner'])) # pass in values as a tupple, which uses ()

        # IMPORTANT - FOR Add, Update, Delete - Make sure to commit!!! Or you will not see your changes
        conn.commit()
        response = {'msg': 'Added pet'}, 201

        # Python equivalent of catch
    except psycopg2.Error as e:
        print('Error from DB', e.pgerror)
        response = {'msg': 'Error adding pet'}, 500

    # python equivalent of finally
    else: # this else statment will run regardless!
        if cursor:
            # Close the cursor
            cursor.close()
    
    return response # returns this to client-side

def getPets():
    # Get a connection to database, use that to get a cursor
    conn = get_db_conn()
    cursor = conn.cursor()

    # Run our select query on the cursor
    cursor.execute('SELECT * FROM pets ORDER BY checked_in, pet;')

    # Get our results
    result = cursor.fetchall()

    # IMPORTANT!! - CLOSE the cursor
    cursor.close()

    # Send back results
    return {'pets': result}
