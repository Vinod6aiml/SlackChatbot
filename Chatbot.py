#Import the required libraries
import requests,json, os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initializes the app with the bot token and app token
#SLACK_APP_TOKEN and SLACK_BOT_TOKEN will be stored in environment variables
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

#headers are common in all the API requests, so declaring as global variable
headers={"Accept": "application/json", "Authorization":"SSWS 00SyMgGVNhaL8sDOuVVOk7u5A3DUYYk3fl4cghxuLf", "Content-Type":"application/json"}

#Function to query user data based on the email provided
#This will listen to the word query and the function gets invoked whenever there is a hit.
@app.message("query")
def message_hello(message, say):

    query = message["text"]
    query = query.split()
    email = query[1].split("|")[0].split(":")[1]
    #store the rest of the query in attributes array 
    attributes = query[2:]

    # users cannot be queried based on email, user ID is prerequisite to query any user

    URL_find = "https://dev-72145890.okta.com/api/v1/users/"+email
    #fetch the USER ID
    response = requests.get(URL_find,headers=headers)

    if (response.status_code == 200):
        user_ID = response.json()["id"]
    else:
        say("Employee with the email provided doesn't exist")

    #fetch the attributes of the user based on the 'id'
    URL_query = "https://dev-72145890.okta.com/api/v1/users/" + user_ID
    response = requests.get(URL_query,headers=headers)

    if(response.status_code == 200):
        #Return the result of the query
        say(f"Email: {response.json()['profile']['email']}")
        for item in attributes:
            say(f"{item}: {response.json()['profile'][item]}")
        
    else:
        #return the error summary
        say("Failed to find the user")
        print(response.json)
        say(f"FailureReason: {response.json()['errorCauses'][0]['errorSummary']}")

#Function to create new employee and add them to OKTA
@app.message("create")
def message_hello(message, say):
    #copy the query entered in slack into a string to parse it    
    query = message["text"]
    #split into different words to parse the email and the attributes. This splits based on the spaces
    query_list = query.split()
    #email is the second word in the string
    email = query_list[1].split("|")[0].split(":")[1]
    attribute_list = query_list[2:] #To remove the first two words in the query to get key value pairs
    print(attribute_list)
    attribute = {}
    for t in attribute_list:
        t_list = t.split("=")
        attribute[t_list[0]] = t_list[1]   #To store the key value pairs i.e user_attribute and their value

    #email and login key are mandatory for the create user API. 
    attribute['email']=email
    attribute['login']=email
 
    # OKTA endpoint to create users
    URL = "https://dev-72145890.okta.com/api/v1/users?activate=true"
    data=json.dumps({"profile": attribute})
    response = requests.post(URL,headers=headers,data=data)

    if(response.status_code == 200):
        #Return the result of the query
        say("CREATION:SUCCESS")
        say(f"Email: {response.json()['profile']['email']}")
        for item in attribute:
            if item not in ["email", "login"]:
                say(f"{item}: {response.json()['profile'][item]}")

    else:
        #return the error summary
        say("CREATION:FAILED")
        print(response.json)
        say(f"FailureReason: {response.json()['errorCauses'][0]['errorSummary']}")

#function to list all the employees
@app.message("list")
def message_hello(message, say):
    #Okta end point to list all the users
    URL = "https://dev-72145890.okta.com/api/v1/users?limit=200"
    
    response = requests.get(URL,headers=headers)
    if(response.status_code == 200):
        #Return the result of the query
        say("Users")
        Number_Of_Users=len(response.json())
        #print(Number_Of_Users)
        for user in response.json():
            #format to print the users is fristName lastName - email
            say(f"{user['profile']['firstName']} {user['profile']['lastName']} - {user['profile']['email']}")

    else:
        #return the error summary
        say("FAILED TO GET THE LIST")
        print(response.json)
        say(f"FailureReason: {response.json()['errorCauses'][0]['errorSummary']}")

@app.message("update")
def message_hello(message, say):    
    query = message["text"]
    #Convert the string to an array of words by seperating the sentence based on space. Split will return an array of words. 
    query_list= query.split()
    email = query_list[1].split("|")[0].split(":")[1] 
    attribute_list = query_list[2:] #To remove the first two words in the query to get key value pairs
    attribute = {}
    for t in attribute_list:
        t_list = t.split("=")
        attribute[t_list[0]] = t_list[1]   #To store the key value pairs i.e user_attribute and their value

    #email and login attributes are mandatory for update user API
    attribute['email']=email
    attribute['login']=email
    
    #To update the user, the API needs user ID. So, first user ID needs to be fetched
    URL_find = "https://dev-72145890.okta.com/api/v1/users/"+email
    response = requests.get(URL_find,headers=headers)

    if (response.status_code == 200):
        user_ID = response.json()["id"]
    else:
        say("Employee with the email provided doesn't exist")

    print(user_ID)    

    # Funtcion to update the parameters of the user ID fetched
    # OKTA endpoint to update users
    URL_update = "https://dev-72145890.okta.com/api/v1/users/" + user_ID
    data=json.dumps({"profile": attribute})
    response = requests.post(URL_update,headers=headers, data=data)

    if(response.status_code == 200):
        #Return the result of the query
        say("Update:SUCCESS")
        say(f"Email: {response.json()['profile']['email']}")
        for item in attribute:
            #return only the attribute and it's value
            if item not in ["email", "login"]:
                say(f"{item}: {response.json()['profile'][item]}")

    else:
        #return the error summary
        say("update:FAILED")
        print(response.json)
        say(f"FailureReason: {response.json()['errorCauses'][0]['errorSummary']}")


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()