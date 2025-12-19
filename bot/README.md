# Discord Bot - Quick Setup

**App ID:** `1451543287382016121`  
**Public Key:** `85642a0c69462892a2fcd91fc6097e5ac7fb9dd4de73676384098f144e883eca`

## 1. Get Bot Token

https://discord.com/developers/applications/1451543287382016121/bot → Reset Token → Copy

## 2. Get Your User ID

Discord Settings → Advanced → Developer Mode → Right-click name → Copy User ID

## 3. Install on VPS

```bash
# Upload files
scp -r bot sl4x0@YOUR_VPS:/home/sl4x0/js-scanner/

# SSH and setup
ssh sl4x0@YOUR_VPS
cd /home/sl4x0/js-scanner/bot

# Install
pip3 install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Fill in: DISCORD_BOT_TOKEN, AUTHORIZED_USER_ID

# Run as service
sudo cp discord-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord-bot.service
sudo systemctl start discord-bot.service
```

## 4. Invite Bot

https://discord.com/api/oauth2/authorize?client_id=1451543287382016121&permissions=2048&scope=bot%20applications.commands

## Usage

```
/scan python3 -m jsscanner -t target --subjs-only -u https://example.com
/screen-status
/screen-list
```

That's it. Scanner sends notifications as usual.
