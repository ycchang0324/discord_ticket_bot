# discord_ticket_bot

<!-- GETTING STARTED -->
## Getting Started

This repository is for NTU Lifeguard. The repo creates a chatbot, which is powered by Selenium and Discord API. By sending messages in specific Discord channel, the chatbot will generate QRCode for NTU swimming pool and NTU fitness center.

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

4. Download webdriver with appropriate version, for more details please check [here](https://developer.chrome.com/docs/chromedriver?hl=zh-tw)

5. Create a Discord chatbot, for more details please check [here](https://discord.com/developers/docs/intro)

![](examples/bot_setting.png)

6. Create .env file, copy the text in .env.example and fill in 
(1) Discord channel ID 
(2) Discord channel name 
(3) NTU account 
(4) NTU password 
(5) NTU rental system url: https://rent.pe.ntu.edu.tw/member/ 
(6) Discord bot token



<!-- USAGE EXAMPLES -->
## Usage

1. execute main.py
   ```sh
   python main.py
   ```

2. If you want to create 24hr Discord chatbot, you can create .bat file and uses Task Scheduler, which is a Windows build-in tools to wake up the chatbot every once in a while
   ```sh
   cd /d "the absolute directory of the repository in your computer"
   call python main.py
   REM pause
   ```




<!-- CONTACT -->
## Contact

Yuan-Chia, Chang - ycchang0324@gmail.com

Project Link: [https://github.com/ycchang0324/discord_ticket_bot](https://github.com/ycchang0324/discord_ticket_bot)

