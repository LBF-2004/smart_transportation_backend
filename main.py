from flask import Flask
import requests
from flask_cors import CORS
import time
import json
import requests
import ParseEmails
import statistics

app = Flask(__name__)
CORS(app)

zip_city = {}

a = open("City_Price/Zip", "r")
for x in a.readlines():
    zip = x.split(",")
    zip_city[str(zip[0])] = zip[1].rstrip()


def find_city(zipcode):
    if zipcode not in zip_city:
        print("Wrong ZIP")
    else:
        return zip_city[zipcode].lower()


lax_price = {}

f = open("City_Price/lax_price", "r")
for line in f.readlines():
    items = line.split(",")
    # print(items[0], items[1]) # Key Value
    lax_price[items[0]] = float((items[1]))

# print(lax_price)

texas_price = {}

g = open("City_Price/tx_price", "r")
for a in g.readlines():
    data = a.split(",")
    texas_price[data[0]] = float((data[1]))
# print (texas_price)

okc_price = {}

h = open("City_Price/okc_price", "r")
for b in h.readlines():
    info = b.split(",")
    okc_price[info[0]] = float((info[1]))
# print (okc_price)

line_haul = {"tx": texas_price, "la": lax_price, "okc": okc_price}


# "lax" => "ALHAMBRA"
# print(line_haul["lax"]["ALHAMBRA"])


@app.route("/get_price/<org_city>/<des_city>/<container_count>")
def get_price(org_city, des_city, container_count):
    # line_haul
    if org_city.isdigit():
        org_city = find_city(org_city)
    if des_city.isdigit():
        des_city = find_city(des_city)

    # It is possible that org_city or des_city is invalid
    # or we cannot handle it, so we need to check the following 2 things before processing the request:
    # 1) is org_city in the list of supported cities (e.g., lax, ock, etc.)
    if org_city not in line_haul:
        return "na"

    # 2) is des_city in the dictionary we have for that city.
    # If we cannot support it, we will need to return "na" right away
    if des_city not in line_haul[org_city]:
        return "na"

    # if org_city or des_city is zipcode,
    # then, we look up the zip dictionary and translate it into the city name

    container_count = int(container_count)
    # TODO: save the result to user's db under quotes
    return str(line_haul[org_city][des_city] * container_count)


# review how to use and call function
# https://www.w3schools.com/python/python_functions.asp

# "newuser@gmail.com" : {
#     "password" : "test123",
#     "name" : "Leo Liao",
#     "phone" : "3451233434",
#     "email" : "newuser@gmail.com",
#     "id" : "user001",
#     "quotes" : [
#      {
#        "id" : "q111",
#        "org" : "lax",
#        "des" : "92602",
#        "time" : 123232324343,
#        "result" : 760
#      },
#      {
#        "id" : "q123",
#        "org" : "ock",
#        "des" : "92602",
#        "time" : 123232343434,
#        "result" : 890
#      }
#     ]
#   }

user_db = {
    "yusun@cpp.edu": {
        "password":
            "yusun123",
        "name":
            "Yu Sun",
        "phone":
            "9495341234",
        "email":
            "yusun@gmail.com",
        "id":
            "user002",
        "quotes": [{
            "org_city": "lax",
            "des_city": "des",
            "container_count": 3,
            "current time": 162123232322
        }, {
            "org_city": "ock",
            "des_city": "des1",
            "container_count": 2,
            "current time": 162123254223
        }]
    },

    "newuser@gmail.com": {
        "password": "test123",
        "name": "Leo Liao",
        "phone": "3451233434",
        "email": "newuser@gmail.com",
        "id": "user001",
    },
    "leoliaobofei20041217@gmail.com": {
        "password": "12345",
        "first_name": "Leo",
        "last_name": "Liao",
        "phone": "2224",
        "email": "leoliaobofei20041217@gmail.com",
        "id": "001",
        "quotes": [
            {
                "userID": "001",
                "quoteId": "2424708511",
                "org_city": "PEK",
                "des_city": "Shanghai",
                "container_count": "3",
                "item_description": "APPLE",
                "current time": "23234423",
                "result": "67",
                "list_prices": {
                    "123": "67"
                }
            }
        ]

    }
}


def saved_quote_email():
    emails = ParseEmails.getEmails()  # here is the bug
    print(emails)
    print("Total emails: ", len(emails))
    for a in emails:
        subject = a[1]
        if ParseEmails.is_git_freight_quote_subject(subject):
            result = 'na'
            result_price = ParseEmails.parseprice.extractPrice(a[2])
            # print ("Test", b)
            for h in result_price:
                if 'rate' in h["DETAIL"].lower() or 'line haul' in h["DETAIL"].lower() or 'shipment' in h[
                    'DETAIL'].lower():
                    result = float(h['PRICE'].replace('$', '').strip())
            Major_ID = ParseEmails.get_major_minor_user_ids(subject)[0]
            Minor_ID = ParseEmails.get_major_minor_user_ids(subject)[1]
            userID = ParseEmails.get_major_minor_user_ids(subject)[2]
            for key, value in user_db.items():
                # print(value)
                if value["id"] == userID:
                    for quote in (value["quotes"]):
                        if quote["quoteId"] == Major_ID:
                            quote["list_prices"][Minor_ID] = result
                            quote['result'] = compare_prices(quote["list_prices"])
    return "New Quotes Saved and Compared"


def compare_prices(quote):
    prices = quote.value()
    final_price = str(statistics.median(prices))
    return final_price


# sign up
@app.route(
    "/signup/<email_adress>/<password>/<first_name>/<last_name>/<phone>/<company>"
)
def signup(email_address, password, first_name, last_name, phone, company):
    email_address = email_address.lower()
    if email_address not in user_db:
        user_db[email_address] = {
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "email": email_address,
            "company": company,
            "quotes": []
        }

    else:
        return "Email already exists."
    return "OK"


# login
@app.route("/login/<email_adress>/<password>")
def login(email_adress, password):
    email_adress = email_adress.lower()
    if email_adress in user_db:
        if user_db[email_adress]["password"] == password:
            print("Correct")
            return "OK"
        else:
            print("Wrong Password")
            return "Invalid username or password"
    else:
        return "User doesn't exist."


# signup("leo@edu", "12345")
# login("liao@edu", "12345")

email_list = [
    {
        "id": "001",
        "email": "leoliaobofei20041217@gmail.com",
        "name": "Leo Transportation Inc."
    },
    {
        "id": "002",
        "email": "yu.sun.cs@gmail.com",
        "name": "Yu sun"
    },
    {
        "id": "003",
        "email": "zhangling1729@gmail.com",
        "name": "Zhangling"
    }

]


def send_quote_emails(quote_data):
    # for each email in the email_list,
    # send an email with the quote information
    for i in range(len(email_list)):  #
        result = requests.post(
            "https://api.mailgun.net/v3/mail.gitfreight.com/messages",
            auth=("api", "57f394120fe10bf3ad3b675cc9f7054c-29561299-e12f4399"),
            data={"from": "Rachael <rachael@gitfreight.com>",
                  "to": [email_list[i]["email"]],
                  "subject": quote_data["userID"] + "GitFreight Quote Request #" + quote_data["quoteId"] + "-" +
                             email_list[i]["id"],
                  "text": "To whotm it may concern, \n" +

                          "\nThere is one shipment need your kind support. Please kindly check and advise your trucking charge per below info: \n" +

                          "\nFrom: " + quote_data["org_city"] + "\n"
                                                                "Service: Trucking" + "\n"
                                                                                      "Quantity: " + quote_data[
                              "container_count"] + "\n"
                                                   "Commondity: " + quote_data["item_description"] + "\n"
                                                                                                     "Delivery Adress: " +
                          quote_data["des_city"] + "\n"

                                                   "\nNote: \n" +

                          "Commericial area/ need lift gate" + "\n"

                                                               "\nThank you," + "\n"
                                                                                "Rachael Zhang" + "\n"

                                                                                                  "\nGlobal Intertrans \n" +
                          "1300 Valley Vista, Dr 205A, \n" +
                          "Diamond Bar CA 91765 \n" +
                          "Tel: 1-909-345-7587 \n" +
                          "Fax: 1-909-345-7589 \n" +
                          "Web site: www.globalintertrans.com \n" +
                          "Email: Rachael@globalintertrans.com \n"
                  })
        print(result)


@app.route(
    "/submit_quote/<org_city>/<des_city>/<container_count>/<email_adress>/<item_description>")
def submit_quote(org_city, des_city, container_count, item_description, email_adress):
    current_time = time.time()
    quote_data = {
        "userID": user_db[email_adress]["id"],
        "quoteId": str(int(current_time)),
        "org_city": org_city,
        "des_city": des_city,
        "container_count": container_count,
        "item_description": item_description,
        "current time": current_time,
        "result": "na",
    }
    user_db[email_adress]["quotes"].append(quote_data)

    # TODO: to process this quote
    # Follow a sequnce of startegies
    # 1) Try the port query table (get_price)
    #  if 1) returns na, we will move to 2)
    #  if 1) returns the price, we will update the result right away, and finish this function
    a = get_price(org_city, des_city, container_count)
    if a != "na":
        # move to 2)
        lastindex = len(user_db[email_adress]["quotes"]) - 1
        user_db[email_adress]["quotes"][lastindex]["result"] = a
        return "OK"

    # 2) Call the TTX API to get the price
    #  if 2) returns na, we will move to 3)
    # 3) Send email and wait for the reply
    #  send the email and wait
    send_quote_emails(quote_data)

    return "OK"

    # line_haul
    # if org_city.isdigit():
    #     org_city = find_city(org_city)
    # if des_city.isdigit():
    #     des_city = find_city(des_city)

    # container_count = int(container_count)
    # TODO: save the result to user's db under quotes
    # return str(line_haul[org_city][des_city] * container_count)


@app.route("/list_all_my_quotes/<email_adress>")
def list_all_my_quotes(email_adress):
    # return all the quotes as a list from the users' record

    return json.dumps(user_db[email_adress]["quotes"])


app.run(host='0.0.0.0')
# print (user_db)

# change in functioning needs to be done at "def"
# while(True):
#  find_city(zipcode=int(input()))

# zip_city_inv = {   }

# b = open("zip.csv", "r")
# for y in b.readlines():
#   code = y.split(",")
#   zip_city_inv[str(code[1])]= [int(code[0])]
# def find_zipcode(cityname):
#   for n in zip_city_inv:
#     if n[0] in zip_city_inv:
#       zip_city_inv[n[0]].append(n[1])
#       print(zip_city_inv[cityname])
#     else:
#       print ("invalid cityname")
# find_zipcode(str(input())

# def find_zipcode_inv(cityname):

# type of data is IMPORTANT!!!
