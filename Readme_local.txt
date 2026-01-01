
######################
######################
  Creating Backend
######################
#######################

Step-1 : Create a requirements.txt file in folder directory and add all the dependencies

##########################################################################################################################

Step-2 : Create a virtual environment from the terminal after navigating to project folder.
Command to create a virtual environment names "VA"- 
python3 -m venv VA

##########################################################################################################################

Step-3 : Activate Virtual environment using below command - 
python3 -m venv VA

##########################################################################################################################

Step-4 : Install all dependencies
Command - 
pip install -r ./requirements.txt

##########################################################################################################################

Step-5 : Add your API keys in the .env file

##########################################################################################################################

Step-6 : Create MCP server named - LiveNewsServer 

    6.1 Create python file - LiveNewsServer.py
    6.2 Write the code as mentioned in the file
    6.3 What code does ? 
            - It invokes the NewsAPI and gets a list of top 3 articles basis the query provided by invoking Agent
            - Then it parses the response and append the content mentioned in body in a list - news_data
            - This list is exposed to a custom function which using OpenAI llm summarize the body/content mentioned in news_data for all 3 articles
    6.4 Run the MCP inspector using below command - 
          uvx --with "mcp[cli]" --with eventregistry --with newsapi-python --with openai --python 3.13 mcp dev LiveNewsServer.py

    Note - all the --with packages like mcp[cli], eventregistry are explicitly passed as we are running mcp server as a standalone in uvx environment

    6.5 - Once the MCP inspectot launched then do update argument as below WITH Transport as "stdout" and command as "uv"

           run --with mcp --with eventregistry --with newsapi-python --with openai LiveNewsServer.py

    6.6 Click on connect

    6.7 Click on Tools
           

##########################################################################################################################

Step- 7 : Run the MCP inspector

    7.1 Run the MCP inspector using below command - 
          uvx --with "mcp[cli]" --with eventregistry --with newsapi-python --with openai --python 3.13 mcp dev LiveNewsServer.py

         Note - all the --with packages like mcp[cli], eventregistry are explicitly passed as we are running mcp server as a standalone in uvx environment

    7.2 - Once the MCP inspectot launched then do update argument as below WITH Transport as "stdout" and command as "uv"

           run --with mcp --with eventregistry --with newsapi-python --with openai LiveNewsServer.py

    7.3 Click on connect

    7.4 Click on tools

    7.5 Click on get tools

    7.6 Click on tool name

    7.7 Test the tool by passing argument
    
##########################################################################################################################

Step-8 : Add the MCP server in the agent.py code so that AI agent can invoke MCP and then use the tools hosted by MCP server for providing assstance to customer
         This code will automativally run the MCP server as that is one of job of MCPServerStdio class 
         Code - 
         news_mcp_server = mcp.MCPServerStdio(
               command=sys.executable,  # Uses the current python path (VA_new)
               args=["LiveNewsServer.py"],
               client_session_timeout_seconds=60 
          )
##########################################################################################################################



######################
######################
  Creating Frontend
######################
#######################


Step-1 : Run below Command

npm create vite@latest frontend -- --template react

After above command press enter on next two prompts. It will then install all dependencies and launch an end point for web app.

Reference only - prompts that will appear on terminal - 
*****************************************Terminal messages******************************************
Need to install the following packages:
create-vite@8.2.0
Ok to proceed? (y) y

> npx
> "create-vite" frontend --template react

│
◇  Use rolldown-vite (Experimental)?:
│  No
│
◇  Install with npm and start now?
│  Yes
│
◇  Scaffolding project in /Users/harshkansal/Documents/Cursor_Projects/HK_Voice_Agent/frontend...
│
◇  Installing dependencies with npm...

*******************************************************************************************************

##########################################################################################################################

Step-2 : Install livekit frontend components using below command

npm install @livekit/components-react @livekit/components-styles livekit-client --save


##########################################################################################################################

Step-3 : In frontend folder delete below files

 a. src -- Assets folder
 b. public folder

##########################################################################################################################

Step-4 : Update App.jsx with the required code

##########################################################################################################################

Step-5 : In src folder create below files - 

a. LiveKitModal.jsx - This will be the pop up when we need to launch livekit agent in browser
b. SimpleVoiceAssistant.jsx - Will house the logic for voice assistant
c. SimpleVoiceAssistant.css

##########################################################################################################################

Step-6 : Update SimpleVoiceAssistant.css , App.css and index.css with required code

##########################################################################################################################

Step-7 : Update App.jsx which houses the code for landing page 

##########################################################################################################################

Step-8 : Update LiveKitModal.jsx which creates a livekit room for both agent and user wherein they can interact

##########################################################################################################################

Step-9 : In LiveKitModal.jsx, Ensure to update your agent URL in the livekit room as "serverUrl={import.meta.env.VITE_LIVEKIT_URL}".

The URL will be fetched from .env file created inside of frontend folder and will start with key name as "VITE".
The reason why we cannot use the existing .env file is because - 
a. os.getenv() is Python, not JavaScript
b. React runs in the browser, not Python
c. JavaScript can't call Python functions directly

##########################################################################################################################

Step-10 : In LiveKitModal.jsx, update token which acts like credentials of user that allow us provide access to agent.
In future, if we can create multiple agents/rooms then we can use this token to provide required access to users

In order to generate token, go to Cloud.livekit.io - Settings - Keys 
Click on three dots -- Generate Token
Enter username and room name - Generate Token
Copy Token

Update Code - token={import.meta.env.Session_Token}

##########################################################################################################################

Step-11 : Update SimpleVoiceAssistant.jsx with appropriate code. This houses the UX functions of the Virtual agent 
         while it is interacting with user


##########################################################################################################################


######################
######################
  Testing Frontend
######################
#######################

Step-1 : Open another terminal and activate the virtual environment

source VA_New/bin/activate

*VA_New - name of the virtual environment
##########################################################################################################################

Step-2 : Run the agent in dev model

Python agent.py dev

##########################################################################################################################

Step-3 : Launch the frontend web from the original terminal while being in frontend dir

npm run dev

##########################################################################################################################

Step-4 : Remember to generate a new token if the prior one had expired else voice agent will not launch

##########################################################################################################################


######################
######################
  Creating Server
######################
#######################

This server is required to generate token systematically and create a new room for the conversation to 
commence between live agent and human

Step-1 : Create server.py file in source folder (NOT in front end folder)

##########################################################################################################################

Step-2 : Add appropriate code

##########################################################################################################################


##############################
##############################
Ruuning the setup in dev mode 
#############################
#############################


Step-1 : Open a new terminal and activate virtual environment using below command

source VA_New/bin/activate

########################################################################################################################

Step-2 : Run the server.py using below command

python server.py dev

########################################################################################################################

Step-3 : Open another new terminal and activate virtual environment using below command

source VA_New/bin/activate

########################################################################################################################

Step-4 : Run the agent.py in dev mode using below command

python agent.py dev

########################################################################################################################

Step-5 : Open another new terminal and activate virtual environment using below command

source VA_New/bin/activate

########################################################################################################################

Step-6 : navigate to frontend folder and run the frontend in dev mode using below command

cd frontend

npm run dev

########################################################################################################################