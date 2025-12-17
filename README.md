# discord_ticket_bot

<!-- GETTING STARTED -->
## Getting Started

This repository is for NTU Lifeguard. The repo creates a chatbot, which is powered by Docker, Selenium and Discord API. By sending messages in specific Discord channel, the chatbot will generate QRCode for NTU swimming pool and NTU fitness center.

### Usage Example
![](examples/usage.gif)

### Prerequisites
* Docker installed.
* WSL 2(for Windows OS)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/ycchang0324/discord_ticket_bot
   ```

2. change directory to the folder
   ```sh
   cd discord_ticket_bot
   ```

3. build the image
   ```sh
   docker build --progress=plain --no-cache -t discord-ticket-bot .
   ```

4. run the container(every time you edit the code)
   ```sh
   docker-compose up -d --build
   ```  

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
(7) Maintainer's ID  
(8) Bot Name

8. Edit the payment message
```python
await ctx.followup.send("...", file=qrcode, ephemeral=True)
```
, which is in the function
```python
@bot.slash_command(name="help", description="呆呆獸怎麼用")
```
in main.py. Please notice that if the payment QR code is not needed,  please replace the QR code picture by empty picture by uncomment the code
```python
qrcode = discord.File(qrcode_path, filename="empty.png")
```


## Maintainer's prompts

The mainainer can send specific messages to the bot either privately or publicly.

1.    
```sh
   welcome
```

The bot will send the welcome message to the channel.

2.    
```sh
   swim
```

The bot will send the message that the swimming tickets is full.

3.    
```sh
   gym
```

The bot will send the message that the gym tickets is full.

4.    
```sh
   fixed
```

The bot will send the message that the bot has been fixed.

<!-- CONTACT -->
## Contact

Yuan-Chia, Chang - ycchang0324@gmail.com

Project Link: [https://github.com/ycchang0324/discord_ticket_bot](https://github.com/ycchang0324/discord_ticket_bot)

