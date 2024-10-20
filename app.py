from math import ceil
from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager

app = Flask(__name__)

# Database connection function
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='myapp_db',
            user='root',
            password=''
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

@contextmanager
def get_db_cursor():
    connection = create_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            yield cursor
            connection.commit()
        except Error as e:
            connection.rollback()
            print(f"Error during database operation: {e}")
        finally:
            cursor.close()
            connection.close()
    else:
        yield None

        
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    power = request.args.get('power', type=int)
    view = request.args.get('view', 'users')  # Default to 'users' if not specified
    per_page = 5
    offset = (page - 1) * per_page

    with get_db_cursor() as cursor:
        if cursor:
            # Prepare the base query
            base_query = "SELECT * FROM users"
            count_query = "SELECT COUNT(*) as count FROM users"
            
            # If power filter is applied, modify the queries
            if power:
                base_query += " WHERE power = %s"
                count_query += " WHERE power = %s"
                query_params = (power, per_page, offset)
                count_params = (power,)
            else:
                query_params = (per_page, offset)
                count_params = ()

            # Get total number of records
            cursor.execute(count_query, count_params)
            total_records = cursor.fetchone()['count']
            
            # Calculate total pages
            total_pages = ceil(total_records / per_page)
            
            # Get paginated data
            query = base_query + " LIMIT %s OFFSET %s"
            cursor.execute(query, query_params)
            users = cursor.fetchall()
            
            return render_template('index.html', users=users, page=page, total_pages=total_pages, power=power, view=view)
        else:
            return "Unable to connect to the database."

if __name__ == '__main__':
    app.run(debug=True)