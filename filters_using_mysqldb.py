import MySQLdb
from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL


# initilise the app
app = Flask(__name__)

# configure database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'classicmodels'
app.config['MYSQL_PASSWORD'] = 'root_pass'

# initialise the client
mysql = MySQL(app)


@app.route("/")
def getAllProducts():
 
    #Creating a connection cursor
    cursor = mysql.connection.cursor()
    
    #Executing SQL Statements
    cursor.execute('''SELECT * FROM products; ''')
    rows = cursor.fetchall()
    
    #Closing the cursor
    cursor.close()

    return jsonify(rows)


@app.errorhandler(405)
def wrong_method(err_msg):
    return jsonify(error=str(err_msg)), 405

# don't need to call it manually 
# when internally error with status code 404 occurs
# this method called automatically
@app.errorhandler(404)
def wrong_method(err_msg):
    return jsonify(error=str(err_msg)), 404


def where_condition(fields):

    # list to store subqueries
    dynamic_sub_queries = []
    values = fields.values()

    for col in fields:

        if col == 'buyPrice' or col == 'MSRP':
            dynamic_sub_queries.append("{} < %s".format(col))

        elif col == 'quantityInStock':
            dynamic_sub_queries.append("{} > %s".format(col))

        else:
            dynamic_sub_queries.append("{} = %s".format(col))

    return dynamic_sub_queries, values



@app.route("/search", methods=['POST'])
def search_product():
    
    static_query = "SELECT * FROM products WHERE "
    limit = 10       # no. of rows to return back

    # get the user's filter choice
    filters = request.get_json()

    # generate subqueries for appropriate to run with where clause
    dynamic_sub_queries, values = where_condition(filters.get('where',{}))


    # convert it back to string
    dynamic_query = " AND ".join(dynamic_sub_queries)

    # merge the queries without order by
    query = static_query + dynamic_query

    # if order by exist in request then add it in query
    if filters.get('order_by',0):
        query += f" ORDER BY {filters['order_by']}"
        print(query)


    # pagination using offset and limit
    if filters.get('page_no',0):
        offset = (filters['page_no'] - 1) * limit
        query += f" LIMIT {limit} OFFSET {offset}"
    

    try:
        cursor = mysql.connection.cursor()
        cursor.execute(query, values)        # passed the col values
        rows = cursor.fetchall()
        cursor.close()
    
    except MySQLdb.OperationalError as e:
        return jsonify({"error": e.args[1]})

    except Exception:
        return jsonify({'error': "Check the passed data"})
    

    # true when rows empty
    if not rows:
        return jsonify("No data available after applying this filters")


    return jsonify(rows)
