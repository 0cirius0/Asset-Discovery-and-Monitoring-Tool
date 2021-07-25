# Asset Discovery and Monitoring Tool
## What it does?
The tool scans the network as specified and finds every user and computer in the Active Directory network. It is capable of scanning multiple AD networks both local and remote. It monitors the discovered devices and users using its agents which helps in keeping identfying any malicious activity.
The tool also finds external assets of the organization as well as possible threats to the organization infrastructure by leaked sensitive data on GitHub. The discovered domains/subdomains are regularly checked for vulnerabilites with nuclei framework and create alert accordingly.

## Installation
It is a click-to-run tool and is capable of doing most of its functions with minimal user intercation. Before running the tool install all the required modules using 
`pip install -r requirements.txt`

Now, just run the main.py and give required permissions and the tool is ready to get information about the organization to start the scans.
To also monitor the user activity in the network, employ the logon/logoff scripts inside the agents directory using a AD group policy and it's done.
