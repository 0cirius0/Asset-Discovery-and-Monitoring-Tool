# Asset Discovery and Monitoring Tool
## What it does?
The tool scans the network as specified and finds every user and computer in the Active Directory network. It is capable of scanning multiple AD networks both local and remote. It monitors the discovered devices and users using its agents which helps in keeping identfying any malicious activity.


The tool also finds external assets of the organization as well as possible threats to the organization infrastructure by leaked sensitive data on GitHub. The discovered domains/subdomains are regularly checked for vulnerabilites with nuclei framework and create alert accordingly.

## How it does?
The tool uses ldap3 python library to interact with the domain controller and get the required information, if the AD network is not inside current network, then the tool establsihes a SSH Tunnel to interact with the remote AD network.


Since the information taken by tool like Domain Controller creds' are very sensitive information, so they are never stored and live dynamically inside the program, although the information extracted is stored in the MONGO DB. 

## Installation
It is a click-to-run tool and is capable of doing most of its functions with minimal user intercation. Before running the tool install all the required modules using 
*   ```pip install -r requirements.txt```
*   Create a .env file and populate it,
    ```
    PASS_KEY=[RANDOM_64_DIGIT_STRING]
    MONGODB=[MongoClient Connection String]
    GITHUB=[GITHUB_API_KEY]
    ```


Now, just run the main.py and give required permissions and the tool is ready to get information about the organization to start the scans.
To also monitor the user activity in the network, employ the logon/logoff scripts inside the agents directory using an AD group policy and the tool would start monitoring the activity of users and send all data to main script to process.



