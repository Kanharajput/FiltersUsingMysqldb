from sqlalchemy import create_engine, select, MetaData, Table
from sqlalchemy.orm import Session
from flask import Flask, jsonify, json, request


# initialise the flask app
app = Flask(__name__)

# mysql+mysqlconnector://user:password@host//password
engine = create_engine("mysql+mysqlconnector://root:root_pass@localhost/classicmodels")

# metadata needed to initilise table and get orm features
metadata = MetaData()

# SqlAlchemy ORM for core use engine.connect()
session = Session(engine)

# get the table obj
products = Table(
    "products",
    metadata,
    # autoload = True,
    autoload_with= engine
)


#------------- HELPER FUNC---------------

# ResultCursor -> dic -> JSON    
def jsonData(result_cur):
    # convert row to dict and append into list
    data = [dict(row) for row in result_cur.mappings()]
    return jsonify(data)

#------------ END OF HELPER FUNC----------

@app.route("/all_products", methods = ["GET"])
def get_all_products():
    dy_query = select(products)
    result_cur = session.execute(dy_query)

    # calling func to get json data
    return jsonData(result_cur)



@app.route("/filters",methods=["POST"])
def specific_products():
    # get the data
    filters = request.get_json()

    # runnig static query
    # st_query = select(products).where(products.columns.productCode == "S10_1678")
    # st_query = st_query.where(getattr(products.c, "productLine") == "Planes")

    st_query = select(products)        # normal query to select all data from the table

    for filter in filters:
        if filter == "buyPrice" or filter == "MSRP":
            st_query = st_query.where(getattr(products.c, filter) < filters[filter])

        elif filter == "quantityInStock":
            st_query = st_query.where(getattr(products.c, filter) > filters[filter])

        else:
            st_query = st_query.where(getattr(products.c, filter) == filters[filter])


    print(st_query)

    result_cur = session.execute(st_query)

    return jsonData(result_cur)