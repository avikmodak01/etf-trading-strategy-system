# 🤖 Telegram Bot Setup Guide

## Step 1: Create Your Telegram Bot

1. **Open Telegram** on your phone or computer
2. **Search for @BotFather** (official Telegram bot for creating bots)
3. **Start a chat** with @BotFather by clicking "Start" or sending `/start`

## Step 2: Create a New Bot

1. **Send command**: `/newbot`
2. **Choose a name** for your bot (e.g., "My ETF Trading Bot")
3. **Choose a username** for your bot (must end with 'bot', e.g., "my_etf_trading_bot")
4. **Copy the token** that @BotFather gives you

Example conversation:
```
You: /newbot
BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.

You: My ETF Trading Bot
BotFather: Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.

You: my_etf_trading_bot
BotFather: Done! Congratulations on your new bot. You will find it at t.me/my_etf_trading_bot. 
You can now add a description, about section and profile picture for your bot, see /help for a list of commands.

Use this token to access the HTTP API:
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
Keep your token secure and store it safely, it can be used by anyone to control your bot.
```

## Step 3: Configure Your Bot Token

1. **Copy the token** from @BotFather (format: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
2. **Open** `bot_config.py` in your project folder
3. **Replace** `YOUR_BOT_TOKEN_HERE` with your actual token:

```python
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

## Step 4: Start Your Bot

```bash
# Activate the environment
source etf_trading_env/bin/activate

# Start the bot
python telegram_bot.py
```

You should see:
```
🤖 Starting ETF Trading Telegram Bot...
Bot token loaded successfully!
2025-XX-XX XX:XX:XX,XXX - __main__ - INFO - Starting ETF Trading Bot...
```

## Step 5: Test Your Bot

1. **Find your bot** on Telegram (search for the username you created)
2. **Start a chat** with your bot by clicking "Start" or sending `/start`
3. **Use the menu** to interact with your ETF trading system

## 🎯 Bot Features

Once your bot is running, you can:

### 📊 **Daily Strategy**
- Get buy/sell recommendations
- View ETF rankings
- See portfolio summary

### 💰 **Update Prices**
Send price data in this format:
```
GOLDBEES,81.73,80.50
NIFTYBEES,281.43,284.60
BANKBEES,580.73,585.20
```

### 📈 **Portfolio Management**
- View current holdings
- Check profit/loss
- See trading statistics

### 💸 **Execute Transactions**
- Buy ETFs with quantity and price input
- Sell ETFs with LIFO method
- Track all transactions

## 🔧 Troubleshooting

### Problem: "Invalid Token" Error
- **Solution**: Make sure you copied the complete token from @BotFather
- **Check**: Token format should be `XXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

### Problem: Bot Doesn't Respond
- **Check**: Make sure the bot script is running
- **Restart**: Stop the script (Ctrl+C) and start again
- **Verify**: Bot token is correct in `bot_config.py`

### Problem: "Bot Not Found"
- **Check**: Username is correct and ends with 'bot'
- **Search**: Use the exact username from @BotFather

## 📱 Using Your Bot

### Basic Commands
- `/start` - Initialize the bot and see main menu
- Use the buttons to navigate through options

### Price Updates
When updating prices, use this format:
```
ETF_NAME,CURRENT_PRICE,20_DAY_MA

Example:
GOLDBEES,81.50,80.20
```

### Buy/Sell Transactions
When prompted for transaction details:
```
QUANTITY,ACTUAL_PRICE

Example:
10,81.75
```

## 🔐 Security Notes

- **Keep your token secret** - don't share it publicly
- **Only you should use your bot** - it's for personal trading strategy
- **Bot data is stored locally** - no cloud storage involved

## 🚀 Advanced Features

### Scheduled Updates
You can set up automatic price updates during market hours:
- 9:35 AM (Market open)
- 12:00 PM (Mid-day)
- 3:25 PM (Market close)

### Multiple Users
Each bot can be used by multiple people, but they'll share the same portfolio data.

## 📞 Support

If you have issues:
1. Check the console output for error messages
2. Verify your token is correct
3. Make sure the bot script is running
4. Restart the bot if needed

## 🎉 You're Ready!

Once set up, you can:
- ✅ Get daily trading recommendations on your phone
- ✅ Update ETF prices remotely
- ✅ Monitor your portfolio anywhere
- ✅ Execute mock trades on the go

**Happy trading with your personal ETF bot! 🚀**