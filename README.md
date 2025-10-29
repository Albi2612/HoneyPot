
🍯 Simple Multi-Module Python Honeypot
A project to lure in the bad guys and learn from their moves.
This repository hosts a simple yet effective honeypot system built in Python. It's designed to mimic common services—specifically SSH and a Web Server—to detect and gather intelligence on low-interaction probing and attacks. It's a fantastic educational tool for understanding network security, attack patterns, and defensive programming.
Features
•	Modular Design: Easily extendable structure with separate modules for different service emulations.
•	SSH Honeypot: Uses Paramiko to emulate a functional SSH server, capturing credentials and commands without ever granting real shell access.
•	Web Honeypot: A basic web service using Flask to log requests, probes, and common scanner attempts.
•	Centralized Dispatcher: The Honeypy file acts as the main entry point, letting you choose which honeypot service to run.
Getting Started
Prerequisites
Before you start catching bots, you'll need the following installed:
•	Python 3.x
•	pip (Python package installer)
Installation
1.	Clone the repository:
Bash
https://github.com/Albi2612/HoneyPot
2.	Install dependencies:
We use a few key Python libraries to make the magic happen (like paramiko for SSH and Flask for the web server).
Bash
pip install -r requirements.txt
(Note: You'll need to create a requirements.txt file listing paramiko and Flask if you haven't already!)
How to Run
The main show is run through Honeypy.py. This script will prompt you to select the honeypot you want to activate.
1.	Execute the main script:
Bash
python Honeypy.py

💻 Module Breakdown
1. The SSH Honeypot (ssh_honeypot.py)
This module uses the Paramiko framework to create a minimal SSH server. When an attacker connects:
•	It presents a standard login prompt.
•	It logs the IP address, attempted username, and password.
•	Any commands entered are logged (not executed!) before the connection is gracefully closed.
Security Note: This script must be run with appropriate permissions to bind to port 22 (or a privileged port of your choice), but ensure it is not run as root unnecessarily for security reasons.
2. The Web Honeypot (web_honeypot.py)
Powered by Flask, this module simulates a very basic web server.
•	It serves a simple HTML page (which you'll find in the relevant template directory).
•	The primary function is to log all HTTP requests. This lets you see scanners looking for common files (/admin, .env, /wp-login.php, etc.), their user-agents, and the source IP.
3. The Dispatcher (Honeypy.py)
This is the brain of the operation. It manages user input, validates the choice, and calls the selected module to start the listening service.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Contact
If you have questions or just want to chat about honeypots and network security, feel free to reach out!
•	GitHub: Albi2612

