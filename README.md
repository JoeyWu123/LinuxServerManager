# LinuxServerManager

This project provides a console-like web page, which allows users to conveniently manage and monitor the important services running on linux server, as well as adding user's own service like crawler. So far, this project is integrated with service to periodically refresh freemyip DNS configuration by calling freemyip API; you can use this project to conveniently manage and config all your freemyip domain names;

Note: currently this project is only tested on Mac and Raspberry Pi. This code cannot run on Windows machine (and is only compatilble with systems with Linux/Unix kernel); In addition, as I haven't integrated this project with https encryption & login verification component yet, please don't deploy this project on the servers without the protection of firewall; It's dangerous to expose the ports on public network without additional security mechanism

To run this project, git pull the code, and use command
```
sudo nohup streamlit run Home.py&
```
then use 8507 port to open the web page

all needed libraries/dependencies can installed via pip