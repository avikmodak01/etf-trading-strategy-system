# ETF Trading Strategy Automation System

An automated ETF (Exchange-Traded Fund) trading strategy system that implements a systematic approach based on ETF rankings, moving averages, and profit/loss management.

## ✨ Key Features

### 💰 **Investment Management**
- **Investment Amount-Based Trading**: Specify investment amount, get optimal quantity suggestions
- **Smart Quantity Calculation**: Price buffers, utilization analysis, and validation
- **Multiple Investment Strategies**: Conservative (₹5K), Balanced (₹10K), Aggressive (₹25K)
- **Investment Efficiency Tracking**: Monitor capital deployment effectiveness

### 🛡️ **Volume Filtering**
- **Liquidity Assurance**: Only trade ETFs with sufficient daily volume (default: >50,000)
- **5-Day Average Volume**: Stable volume assessment for consistent liquidity
- **Configurable Thresholds**: Adjust based on risk preference and portfolio size

### 📊 **Live Data Integration**
- **Yahoo Finance Integration**: Real-time price and volume data
- **20-Day Moving Average**: Automatic calculation from historical data
- **Rate Limiting**: Intelligent API call management

### 🖥️ **Enhanced Interfaces**
- **Enhanced CLI**: 22 menu options with investment guidance
- **Telegram Bot**: Interactive workflows with investment prompts

## 🎯 Strategy Overview

This system implements a disciplined ETF trading strategy with the following rules:

### Buy Logic
1. **New ETF Purchase**: Buy the top-ranked ETF (by deviation from 20-day moving average) that you don't currently hold
2. **Averaging Down**: If all top 5 ETFs are held, buy more of an existing ETF that has fallen >2.5% below purchase price
3. **Daily Limit**: Maximum 1 ETF purchase per day

### Sell Logic
1. **Profit Taking**: Sell ETF holdings with >6% profit using LIFO (Last In, First Out)
2. **Daily Limit**: Maximum 1 ETF sale per day

### Ranking System
- ETFs ranked by deviation from 20-day moving average
- Lower deviation = higher rank (most fallen ETFs ranked first)
- Strategy focuses on buying ETFs that have fallen the most relative to their trend

## 🚀 Quick Start

### 1. Setup
```bash
# Run the setup script
python3 setup.py

# Activate the virtual environment
source etf_trading_env/bin/activate
```

### 2. Start with Enhanced Command Line Interface
```bash
python3 enhanced_cli.py
```

### 3. Configure Investment Settings
- Choose option 21: Configure Investment Capital
- Set your default investment amount (₹10,000 recommended)
- Choose strategy: Conservative/Balanced/Aggressive

### 4. Update ETF Data and Enable Volume Filtering
- Choose option 14: Update ETF Volume Status
- Choose option 17: Toggle Volume Filtering → Enable
- Choose option 6: Load ETF list from Excel

### 5. Get Daily Recommendations
- Choose option 1: Get Daily Strategy Recommendations
- Follow the investment-guided buy/sell suggestions

## 📱 Telegram Bot Setup

### 1. Create Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Send `/start` then `/newbot`
3. Follow instructions to create your bot
4. Copy the bot token

### 2. Configure Bot Token
```bash
# Edit the bot configuration file
nano bot_config.py

# Replace YOUR_BOT_TOKEN_HERE with your actual token
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

### 3. Run Telegram Bot
```bash
source etf_trading_env/bin/activate
python3 telegram_bot.py
```

### 4. Use Bot Features
- **📊 Daily Strategy**: Get buy/sell recommendations
- **📈 Portfolio**: View current holdings and P&L
- **🏆 Rankings**: See ETF rankings by deviation
- **💰 Update Prices**: Add real ETF price data
- **📋 Statistics**: View trading performance

## 📊 System Components

### Core Files
- **`etf_data_manager.py`**: Data storage and portfolio management
- **`trading_strategy.py`**: Strategy logic and recommendations
- **`enhanced_cli.py`**: Enhanced command line interface (22 menu options)
- **`investment_manager.py`**: Investment amount calculations and strategies
- **`volume_filter.py`**: Volume-based ETF qualification system
- **`price_fetcher.py`**: Live price fetching from Yahoo Finance
- **`telegram_bot.py`**: Telegram bot interface with investment prompts
- **`etf-list.xlsx`**: List of ETFs to track

### Data Storage
- **`etf_data.json`**: All data stored in JSON format
  - ETF price data and moving averages
  - Portfolio holdings and transactions
  - Historical trade records

## 💼 Usage Examples

### Enhanced Command Line Interface
```bash
# Get daily recommendations with investment guidance
python3 enhanced_cli.py
# Choose option 1: Get Daily Strategy Recommendations

# Configure investment settings
python3 enhanced_cli.py
# Choose option 21: Configure Investment Capital

# Update ETF prices and volume data
# Choose option 2, then enter:
GOLDBEES,45.50,44.20
KOTAKGOLD,12.30,12.10
done

# Execute mock buy transaction
# Choose option 5, follow prompts
```

### Telegram Bot Commands
```
/start - Start the bot and see main menu
📊 Daily Strategy - Get trading recommendations
💰 Update Prices - Send price updates like:
GOLDBEES,45.50,44.20
KOTAKGOLD,12.30,12.10
```

## 📈 Strategy Features

### Ranking Algorithm
- Calculates `(CMP - 20DMA) / 20DMA * 100` for each ETF
- Ranks ETFs by deviation (ascending - most fallen first)
- Focuses on mean reversion opportunities

### Portfolio Management
- **LIFO Selling**: Sells most recent purchases first
- **Position Tracking**: Monitors all buy/sell transactions
- **P&L Calculation**: Real-time profit/loss tracking
- **Tax Consideration**: Tracks holding periods for tax implications

### Risk Management
- **Daily Limits**: Max 1 buy and 1 sell per day
- **Loss Threshold**: Only average down after 2.5% loss
- **Profit Target**: Systematic profit taking at 6%

## 🔧 Configuration

### Strategy Parameters (customizable in `trading_strategy.py`)
- `max_rank_to_consider`: 5 (consider top 5 ETFs)
- `averaging_loss_threshold`: -2.5% (loss threshold for averaging)
- `profit_threshold`: 6.0% (profit threshold for selling)
- `max_daily_transactions`: 1 (transactions per day)

### Input Validation
- Quantity: 1-10,000 units
- Price: ₹0.01-₹100,000
- ETF names: Alphanumeric validation

## 📋 Sample Workflow

### Day 1: Initial Setup
1. Load ETF list from Excel
2. Update current prices and 20-day moving averages
3. Get strategy recommendation
4. Execute recommended buy (if any)

### Daily Routine
1. Update ETF prices
2. Check daily strategy recommendations
3. Execute buy recommendation (if eligible)
4. Execute sell recommendation (if profitable)
5. Review portfolio performance

### Data Management
1. Monitor portfolio P&L
2. Track trading statistics
3. Review ETF rankings
4. Backup `etf_data.json` regularly

## 🛡️ Important Notes

### Mock Trading Only
- **No Real Trades**: System provides recommendations only
- **Paper Trading**: All transactions are simulated
- **Educational Purpose**: Learn strategy implementation

### Data Requirements
- **Manual Price Updates**: ETF prices must be updated manually
- **20-Day Moving Average**: Calculate externally and input
- **Market Data**: Source from reliable financial data providers

### Limitations
- No real-time data integration
- No automatic trade execution
- No market hours validation
- No order management system

## 🔍 Troubleshooting

### Common Issues
1. **Import Errors**: Ensure virtual environment is activated
2. **Permission Errors**: Check file permissions on JSON data file
3. **Bot Token**: Verify telegram bot token is correct
4. **Data Validation**: Check ETF price format (comma-separated)

### Error Messages
- `Invalid format`: Check input format for price updates
- `No ETF data available`: Update ETF prices first
- `Invalid numbers`: Ensure numeric values are correct
- `No holdings found`: Verify ETF holdings exist before selling

## 📊 Performance Tracking

### Available Statistics
- Total buy/sell transactions
- Win rate percentage
- Total realized profit
- Average profit per trade
- Portfolio value and P&L

### Portfolio Metrics
- Current holdings count
- Total investment amount
- Current portfolio value
- Unrealized profit/loss
- Individual ETF performance

## 🔄 Data Backup

### Important Files to Backup
- `etf_data.json` - All portfolio and transaction data
- `bot_config.py` - Bot configuration
- `etf-list.xlsx` - ETF universe

### Backup Strategy
```bash
# Create backup
cp etf_data.json etf_data_backup_$(date +%Y%m%d).json

# Restore from backup
cp etf_data_backup_20240120.json etf_data.json
```

## 🤝 Contributing

This is a personal trading strategy automation tool. Feel free to:
- Fork the repository
- Modify strategy parameters
- Add new features
- Improve error handling
- Integrate with real data sources

## ⚠️ Disclaimer

This software is for educational and research purposes only. It does not provide financial advice or execute real trades. Always consult with financial professionals before making investment decisions. Past performance does not guarantee future results.

## 📄 License

This project is for personal use. Modify and adapt as needed for your trading strategy research and education.