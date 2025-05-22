# discord_ticket_bot

<!-- GETTING STARTED -->
## Getting Started

This repository is for NTU Lifeguard. The repo creates a chatbot, which is powered by Selenium and Discord API. By sending messages in specific Discord channel, the chatbot will generate QRCode for NTU swimming pool and NTU fitness center.

### Usage Example
![](examples/usage.gif)

### Requirements
* Python 3.10.4
* pip 22.0.4

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/ycchang0324/discord_ticket_bot
   ```

1. change directory to the folder
   ```sh
   cd discord_ticket_bot
   ```

3. install packages
   ```sh
   pip install -r requirements.txt
   ```

4. Download webdriver with appropriate version, for more details please check [here](https://developer.chrome.com/docs/chromedriver?hl=zh-tw).

5. Create a Discord chatbot, for more details please check [here](https://discord.com/developers/docs/intro).

The setting for discord bot is shown in the following picture.
![](examples/bot_setting.png)

6. Add the payment QRCode as payment_qrcode.png in img folder.

7. Create .env file, copy the text in .env.example and fill in  
(1) Discord channel IDs(can be multiple, separated by colons)
(2) Discord channel name(only for main channel's name)    
(3) NTU account  
(4) NTU password  
(5) NTU rental system url: https://rent.pe.ntu.edu.tw/member/  
(6) Discord bot token.  

<!-- USAGE EXAMPLES -->
## Usage

1. execute main.py
   ```sh
   python main.py
   ```

2. To prevent sudden occurence such as power failure or network disconnection, you can create .bat file and uses Task Scheduler, which is a Windows build-in tools to wake up the chatbot. The Task Scheduler can execute the code after starting up or once in a while.
   ```sh
   cd /d "the absolute directory of the repository in your computer"
   call python main.py
   REM pause
   ```
The example setting for task scheduler is shown in the following picture.
![](examples/task_scheduler_setting_starting_up.png)
![](examples/task_scheduler_setting_every_day.png)




<!-- CONTACT -->
## Contact

Yuan-Chia, Chang - ycchang0324@gmail.com

Project Link: [https://github.com/ycchang0324/discord_ticket_bot](https://github.com/ycchang0324/discord_ticket_bot)

