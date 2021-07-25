# Asset Discovery and Monitoring Tool
## What it does?
The tool scans the network as specified and finds every user and computer in the Active Directory network. It is capable of scanning multiple AD networks both local and remote. It monitors the discovered devices and users using its agents which helps in keeping identfying any malicious activity.


The tool also finds external assets of the organization as well as possible threats to the organization infrastructure by leaked sensitive data on GitHub. The discovered domains/subdomains are regularly checked for vulnerabilites with nuclei framework and create alert accordingly.

## How it does?
The tool uses ldap3 python library to interact with the domain controller and get the required information, if the AD network is not inside current network, then the tool establsihes a SSH Tunnel to interact with the remote AD network.


For external assets it uses sublist3r python module to find the subdomains owned by the organization and further uses Nuclei Framework from Project Discovery to find vulnerabilities on the discovered subdomains. The tool also makes use of GitHub API in a intelligent way to find any sensitive information getting leaked through the organization's GitHub repos.  

Since the information taken by tool like Domain Controller creds' are very sensitive information, so they are never stored and live dynamically inside the program, although the information extracted is stored in the MONGO DB. 

## Installation
It is a click-to-run tool and is capable of doing most of its functions with minimal user intercation. Before running the tool install all the required modules,
*   Create a virtual environment. 
*   ```pip install -r requirements.txt```
*   Create a .env file and populate it,
    ```
    PASS_KEY="[RANDOM_64_DIGIT_STRING]"
    MONGODB="[MongoClient_Connection_String]"
    GITHUB="[GITHUB_API_KEY]"
    ```


Now, just run the main.py and give required permissions and the tool is ready to get information about the organization to start the scans.
To also monitor the user activity in the network, employ the logon/logoff scripts inside the agents directory using an AD group policy and the tool would start monitoring the activity of users and send all data to main script to process.

##  Functionalities
### Agents
The agents come on form of logon/logoff scripts written in batch which collect data whenever a user logs into the device and send it to the Device on which the driver script is running. If the driver is running on the Domain Controller then there is no need to specify the IP of driver device but in other case it can be easily specified using the "arguments" option that is available while creating AD Group Policy for the scripts.
### Nuclei
The tool integrates Nuclei framework to find vulnerabilites in the discovered subdomains. It updates the templates before every scan so that the new vulnerabilites does not get ignored.
### GitHub Leaks
A custom function which makes GitHub dorks and then uses them to find any sensitive information in the organizations's repositories. The tool has accesskey,passkey,secretkey,api_token by default but more keywords can be added and previous one removed from the webapp.
### Secure WebApp
The webapp starts inside the network and ask for permission to create firewall rule for the port to be accessible inside the network. The webapp uses JWT authentication to prevent any unauthorised person in the network to access the webapp.

## Collected Data
Only useful data is collected which might help in preventing any attack vector as well as narrowing down the devices if compromised.


In case of devices the data stored contains but not limited to the version of OS,last patch/hotfix,servicepack which if old enough might contain vulnerabilities, so giving chance to the admin to always be aware of the systems that are not updated.

In case of monitoring, the devices accessed by user along with the IP and MAC, if the user was using RDP to access are stored so that if any user's creds get compromised then it can devices accessed by attacker can be easily narrowed down and checked manually for any malicious files.
## Working Screenshots
![Dashboard](/Images/dashboard.png?raw=true)
![Sites](/Images/sites.png?raw=true)
![GitHub](/Images/github.png?raw=true)

