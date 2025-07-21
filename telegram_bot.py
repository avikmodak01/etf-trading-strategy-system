import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from etf_data_manager import ETFDataManager
from trading_strategy import ETFTradingStrategy
from price_fetcher import PriceFetcher, PriceUpdateScheduler
from volume_filter import VolumeFilter
from investment_manager import InvestmentManager
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ETFTradingBot:
    def __init__(self, token: str):
        self.token = token
        self.data_manager = ETFDataManager()
        self.price_fetcher = PriceFetcher()
        self.volume_filter = VolumeFilter(self.data_manager, self.price_fetcher)
        self.investment_manager = InvestmentManager(self.data_manager)
        self.strategy = ETFTradingStrategy(self.data_manager, self.volume_filter)
        self.scheduler = PriceUpdateScheduler(self.data_manager, self.price_fetcher)
        self.user_sessions = {}  # Store user interaction sessions
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        keyboard = [
            [InlineKeyboardButton("📊 Daily Strategy", callback_data='daily_strategy')],
            [InlineKeyboardButton("📈 Portfolio", callback_data='portfolio')],
            [InlineKeyboardButton("🏆 Rankings", callback_data='rankings')],
            [InlineKeyboardButton("💰 Update Prices", callback_data='update_prices')],
            [InlineKeyboardButton("📋 Statistics", callback_data='statistics')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🤖 *ETF Trading Strategy Bot*

Welcome! This bot helps you execute a systematic ETF trading strategy based on:
• ETF rankings by deviation from 20-day moving average
• Buying top-ranked ETFs not currently held
• Averaging down on positions with >2.5% loss
• LIFO selling with >6% profit threshold

Choose an option from the menu below:
        """
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button clicks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'daily_strategy':
            await self.show_daily_strategy(query, context)
        elif query.data == 'portfolio':
            await self.show_portfolio(query, context)
        elif query.data == 'rankings':
            await self.show_rankings(query, context)
        elif query.data == 'update_prices':
            await self.prompt_price_update(query, context)
        elif query.data == 'statistics':
            await self.show_statistics(query, context)
        elif query.data.startswith('buy_'):
            await self.handle_buy_action(query, context)
        elif query.data.startswith('sell_'):
            await self.handle_sell_action(query, context)
        elif query.data == 'use_default_investment':
            await self.handle_default_investment(query, context)
        elif query.data == 'main_menu':
            await self.show_main_menu(query, context)
    
    async def show_daily_strategy(self, query, context):
        """Show daily trading recommendations"""
        recommendations = self.strategy.get_daily_recommendations()
        
        message = f"📊 *Daily Strategy - {recommendations['date']}*\n\n"
        
        # Buy recommendation
        buy_rec = recommendations['buy_recommendation']
        message += "🟢 *BUY RECOMMENDATION:*\n"
        if buy_rec['action'] != 'no_action':
            message += f"ETF: {buy_rec['etf_name']}\n"
            message += f"Action: {buy_rec['action'].replace('_', ' ').title()}\n"
            message += f"Current Price: ₹{buy_rec.get('cmp', buy_rec.get('current_price', 'N/A'))}\n"
            if 'deviation_percent' in buy_rec:
                message += f"Deviation: {buy_rec['deviation_percent']:.2f}%\n"
            message += f"Reason: {buy_rec['reason']}\n"
        else:
            message += f"No action recommended\nReason: {buy_rec['reason']}\n"
        
        message += "\n🔴 *SELL RECOMMENDATION:*\n"
        sell_rec = recommendations['sell_recommendation']
        if sell_rec['action'] != 'no_action':
            message += f"ETF: {sell_rec['etf_name']}\n"
            message += f"Current Price: ₹{sell_rec['current_price']}\n"
            message += f"Profit: {sell_rec['profit_percent']:.2f}%\n"
            message += f"Reason: {sell_rec['reason']}\n"
        else:
            message += f"No action recommended\nReason: {sell_rec['reason']}\n"
        
        # Create action buttons
        keyboard = []
        if buy_rec['action'] != 'no_action':
            keyboard.append([InlineKeyboardButton(
                f"💰 Buy {buy_rec['etf_name']}", 
                callback_data=f"buy_{buy_rec['etf_name']}"
            )])
        
        if sell_rec['action'] != 'no_action':
            keyboard.append([InlineKeyboardButton(
                f"💸 Sell {sell_rec['etf_name']}", 
                callback_data=f"sell_{sell_rec['etf_name']}"
            )])
        
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_portfolio(self, query, context):
        """Show current portfolio"""
        portfolio = self.data_manager.get_portfolio_summary()
        
        message = "📈 *Current Portfolio*\n\n"
        message += f"Total ETFs: {portfolio['total_etfs']}\n"
        message += f"Total Investment: ₹{portfolio['total_investments']:,.2f}\n"
        message += f"Current Value: ₹{portfolio['current_value']:,.2f}\n"
        message += f"P&L: ₹{portfolio['total_profit_loss']:,.2f}\n\n"
        
        if portfolio['holdings_detail']:
            message += "*Holdings Detail:*\n"
            for holding in portfolio['holdings_detail']:
                message += f"\n🔸 {holding['etf_name']}\n"
                message += f"   Qty: {holding['quantity']}\n"
                message += f"   Avg Price: ₹{holding['avg_buy_price']}\n"
                message += f"   Current: ₹{holding['current_price']}\n"
                message += f"   P&L: ₹{holding['profit_loss']:.2f} ({holding['profit_loss_percent']:.2f}%)\n"
        else:
            message += "No current holdings."
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_rankings(self, query, context):
        """Show ETF rankings"""
        rankings = self.data_manager.get_etf_rankings()
        
        message = "🏆 *ETF Rankings (Top 10)*\n"
        message += "_Ranked by deviation from 20-day moving average_\n\n"
        
        if rankings:
            for i, (etf_name, cmp, dma_20, deviation) in enumerate(rankings[:10], 1):
                message += f"{i}. {etf_name}\n"
                message += f"   CMP: ₹{cmp:.2f} | 20DMA: ₹{dma_20:.2f}\n"
                message += f"   Deviation: {deviation:.2f}%\n\n"
        else:
            message += "No ETF data available. Please update prices first."
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_statistics(self, query, context):
        """Show trading statistics"""
        stats = self.strategy.get_strategy_statistics()
        
        message = "📋 *Trading Statistics*\n\n"
        message += f"Total Buy Transactions: {stats['total_buy_transactions']}\n"
        message += f"Total Sell Transactions: {stats['total_sell_transactions']}\n"
        message += f"Profitable Sells: {stats['profitable_sells']}\n"
        message += f"Loss Sells: {stats['loss_sells']}\n"
        message += f"Win Rate: {stats['win_rate_percent']}%\n"
        message += f"Total Realized Profit: ₹{stats['total_realized_profit']:,.2f}\n"
        message += f"Average Profit per Sell: ₹{stats['average_profit_per_sell']:,.2f}\n"
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def prompt_price_update(self, query, context):
        """Prompt for price updates"""
        message = """💰 *Update ETF Prices*

🚀 *OPTION 1: LIVE DATA (RECOMMENDED)*
Send: `live` or `yahoo` or `fetch`
This will automatically fetch live prices from Yahoo Finance!

📝 *OPTION 2: MANUAL ENTRY*
Send price data in this format:
`ETF_NAME,CMP,20DMA`

Example:
`GOLDBEES,45.50,44.20`

Or send multiple ETFs (one per line):
```
GOLDBEES,45.50,44.20
KOTAKGOLD,12.30,12.10
SETFGOLD,50.75,49.80
```

Send your choice now:"""
        
        # Set user state for price updates
        user_id = query.from_user.id
        self.user_sessions[user_id] = {'state': 'waiting_for_prices'}
        
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_buy_action(self, query, context):
        """Handle buy action with investment amount"""
        etf_name = query.data.replace('buy_', '')
        user_id = query.from_user.id
        
        # Get current recommendation
        recommendations = self.strategy.get_daily_recommendations()
        buy_rec = recommendations['buy_recommendation']
        
        if buy_rec['etf_name'] == etf_name:
            current_price = buy_rec.get('cmp', buy_rec.get('current_price', 0))
            default_investment = self.investment_manager.config["default_investment_per_trade"]
            
            message = f"💰 *Buy {etf_name}*\n\n"
            message += f"Current Price: ₹{current_price:.2f}\n"
            message += f"Action: {buy_rec['action'].replace('_', ' ').title()}\n"
            message += f"Reason: {buy_rec['reason']}\n\n"
            message += f"💰 *Investment Amount*\n"
            message += f"Default: ₹{default_investment:,}\n\n"
            message += "Send your investment amount or press the button for default:\n"
            message += "Example: `10000` for ₹10,000"
            
            # Set user state
            self.user_sessions[user_id] = {
                'state': 'waiting_for_investment_amount',
                'etf_name': etf_name,
                'recommendation': buy_rec,
                'current_price': current_price
            }
            
            keyboard = [
                [InlineKeyboardButton(f"Use Default (₹{default_investment:,})", callback_data='use_default_investment')],
                [InlineKeyboardButton("❌ Cancel", callback_data='main_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_default_investment(self, query, context):
        """Handle using default investment amount"""
        user_id = query.from_user.id
        
        if user_id not in self.user_sessions:
            await query.edit_message_text("❌ Session expired. Please start again.", parse_mode='Markdown')
            return
        
        session = self.user_sessions[user_id]
        if session['state'] != 'waiting_for_investment_amount':
            await query.edit_message_text("❌ Invalid action. Please start again.", parse_mode='Markdown')
            return
        
        # Use default investment amount
        default_investment = self.investment_manager.config["default_investment_per_trade"]
        await self.process_investment_amount(query, context, default_investment, session)
    
    async def process_investment_amount(self, query, context, investment_amount, session):
        """Process the investment amount and show quantity suggestion"""
        etf_name = session['etf_name']
        current_price = session['current_price']
        
        try:
            # Get investment suggestion
            suggestion = self.investment_manager.get_investment_suggestion(
                etf_name, current_price, investment_amount
            )
            
            suggested_qty = suggestion['suggested_quantity']
            exact_investment = suggestion['exact_investment']
            utilization = suggestion['utilization_percentage']
            
            message = f"💰 *Investment Suggestion for {etf_name}*\n\n"
            message += f"💵 Investment Amount: ₹{investment_amount:,.2f}\n"
            message += f"💰 Current Price: ₹{current_price:.2f}\n"
            message += f"📊 Suggested Quantity: *{suggested_qty}* units\n"
            message += f"💸 Exact Cost: ₹{exact_investment:,.2f}\n"
            message += f"📈 Utilization: {utilization:.1f}%\n\n"
            
            if utilization < 80:
                message += "⚠️ Low utilization - consider adjusting quantity\n\n"
            elif utilization > 98:
                message += "⚠️ High utilization - buffer may be insufficient\n\n"
            else:
                message += "✅ Good utilization - balanced investment\n\n"
            
            message += "Now send your transaction details:\n"
            message += "`QUANTITY,ACTUAL_PRICE`\n\n"
            message += f"Suggested: `{suggested_qty},{current_price:.2f}`"
            
            # Update session state
            session.update({
                'state': 'waiting_for_buy_details',
                'investment_amount': investment_amount,
                'suggested_quantity': suggested_qty,
                'suggestion': suggestion
            })
            
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}", parse_mode='Markdown')
    
    async def process_investment_amount_input(self, update, context, message_text, session):
        """Process custom investment amount input"""
        try:
            investment_amount = float(message_text.strip())
            
            # Validate investment amount
            min_amount = self.investment_manager.config["min_investment_per_trade"]
            max_amount = self.investment_manager.config["max_investment_per_trade"]
            
            if investment_amount < min_amount:
                await update.message.reply_text(f"❌ Investment amount must be at least ₹{min_amount:,}")
                return
            
            if investment_amount > max_amount:
                await update.message.reply_text(f"❌ Investment amount cannot exceed ₹{max_amount:,}")
                return
            
            # Process the investment amount
            await self.process_investment_amount_message(update, context, investment_amount, session)
            
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a valid number.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def process_investment_amount_message(self, update, context, investment_amount, session):
        """Process investment amount for message-based flow"""
        etf_name = session['etf_name']
        current_price = session['current_price']
        
        try:
            # Get investment suggestion
            suggestion = self.investment_manager.get_investment_suggestion(
                etf_name, current_price, investment_amount
            )
            
            suggested_qty = suggestion['suggested_quantity']
            exact_investment = suggestion['exact_investment']
            utilization = suggestion['utilization_percentage']
            
            message = f"💰 *Investment Suggestion for {etf_name}*\n\n"
            message += f"💵 Investment Amount: ₹{investment_amount:,.2f}\n"
            message += f"💰 Current Price: ₹{current_price:.2f}\n"
            message += f"📊 Suggested Quantity: *{suggested_qty}* units\n"
            message += f"💸 Exact Cost: ₹{exact_investment:,.2f}\n"
            message += f"📈 Utilization: {utilization:.1f}%\n\n"
            
            if utilization < 80:
                message += "⚠️ Low utilization - consider adjusting quantity\n\n"
            elif utilization > 98:
                message += "⚠️ High utilization - buffer may be insufficient\n\n"
            else:
                message += "✅ Good utilization - balanced investment\n\n"
            
            message += "Now send your transaction details:\n"
            message += "`QUANTITY,ACTUAL_PRICE`\n\n"
            message += f"Suggested: `{suggested_qty},{current_price:.2f}`"
            
            # Update session state
            session.update({
                'state': 'waiting_for_buy_details',
                'investment_amount': investment_amount,
                'suggested_quantity': suggested_qty,
                'suggestion': suggestion
            })
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_sell_action(self, query, context):
        """Handle sell action"""
        etf_name = query.data.replace('sell_', '')
        user_id = query.from_user.id
        
        # Get current recommendation
        recommendations = self.strategy.get_daily_recommendations()
        sell_rec = recommendations['sell_recommendation']
        
        if sell_rec['etf_name'] == etf_name:
            message = f"💸 *Sell {etf_name}*\n\n"
            message += f"Current Price: ₹{sell_rec['current_price']:.2f}\n"
            message += f"Expected Profit: {sell_rec['profit_percent']:.2f}%\n\n"
            message += "Send your transaction details in this format:\n"
            message += "`QUANTITY,ACTUAL_PRICE`\n\n"
            message += "Example: `5,48.25`"
            
            # Set user state
            self.user_sessions[user_id] = {
                'state': 'waiting_for_sell_details',
                'etf_name': etf_name,
                'recommendation': sell_rec
            }
            
            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def show_main_menu(self, query, context):
        """Show main menu"""
        keyboard = [
            [InlineKeyboardButton("📊 Daily Strategy", callback_data='daily_strategy')],
            [InlineKeyboardButton("📈 Portfolio", callback_data='portfolio')],
            [InlineKeyboardButton("🏆 Rankings", callback_data='rankings')],
            [InlineKeyboardButton("💰 Update Prices", callback_data='update_prices')],
            [InlineKeyboardButton("📋 Statistics", callback_data='statistics')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = "🤖 *ETF Trading Strategy Bot*\n\nChoose an option:"
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        message_text = update.message.text.strip()
        
        if user_id not in self.user_sessions:
            await update.message.reply_text("Please use /start to begin.")
            return
        
        session = self.user_sessions[user_id]
        
        if session['state'] == 'waiting_for_prices':
            await self.process_price_updates(update, context, message_text)
        elif session['state'] == 'waiting_for_investment_amount':
            await self.process_investment_amount_input(update, context, message_text, session)
        elif session['state'] == 'waiting_for_buy_details':
            await self.process_buy_transaction(update, context, message_text, session)
        elif session['state'] == 'waiting_for_sell_details':
            await self.process_sell_transaction(update, context, message_text, session)
    
    async def process_price_updates(self, update, context, message_text):
        """Process ETF price updates"""
        try:
            # Check if user wants to fetch live data
            if message_text.strip().lower() in ['live', 'fetch', 'auto', 'yahoo']:
                await update.message.reply_text("🔄 Fetching live prices from Yahoo Finance for ALL ETFs...")
                
                # Get ALL ETF names from the loaded list (no limit)
                all_etf_names = list(self.data_manager.data["etfs"].keys())
                
                await update.message.reply_text(f"📊 Found {len(all_etf_names)} ETFs to update. This may take a moment...")
                
                # Fetch live data for ALL ETFs
                updated_count = self.scheduler.update_all_etf_prices(all_etf_names)
                
                response = f"🎉 Successfully updated {updated_count} ETFs with live data from Yahoo Finance!"
                
                # Clear user session
                del self.user_sessions[update.effective_user.id]
                
                await update.message.reply_text(response)
                return
            
            # Manual price update processing
            lines = message_text.strip().split('\n')
            updated_count = 0
            errors = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split(',')
                if len(parts) != 3:
                    errors.append(f"Invalid format: {line}")
                    continue
                
                etf_name, cmp_str, dma_str = [p.strip() for p in parts]
                
                try:
                    cmp = float(cmp_str)
                    dma_20 = float(dma_str)
                    
                    self.data_manager.update_etf_price(etf_name, cmp, dma_20)
                    updated_count += 1
                except ValueError:
                    errors.append(f"Invalid numbers in: {line}")
            
            response = f"✅ Updated {updated_count} ETF(s) successfully!"
            if errors:
                response += f"\n\n❌ Errors:\n" + "\n".join(errors)
            
            # Clear user session
            del self.user_sessions[update.effective_user.id]
            
            await update.message.reply_text(response)
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error processing updates: {str(e)}")
    
    async def process_buy_transaction(self, update, context, message_text, session):
        """Process buy transaction"""
        try:
            parts = message_text.strip().split(',')
            if len(parts) != 2:
                await update.message.reply_text("❌ Invalid format. Use: QUANTITY,PRICE")
                return
            
            quantity = int(parts[0].strip())
            price = float(parts[1].strip())
            
            # Validate inputs
            is_valid, validation_msg = self.strategy.validate_transaction_inputs(quantity, price)
            if not is_valid:
                await update.message.reply_text(f"❌ {validation_msg}")
                return
            
            # Execute transaction
            result = self.strategy.execute_buy_recommendation(
                session['recommendation'], quantity, price
            )
            
            if result['success']:
                response = f"✅ {result['message']}\n"
                response += f"Total Amount: ₹{result['total_amount']:,.2f}"
                
                # Add investment efficiency information if available
                if 'investment_amount' in session:
                    target_investment = session['investment_amount']
                    suggested_qty = session.get('suggested_quantity', 'N/A')
                    utilization = (result['total_amount'] / target_investment) * 100
                    
                    response += f"\n\n📊 Investment Analysis:"
                    response += f"\nTarget Investment: ₹{target_investment:,.2f}"
                    response += f"\nSuggested Quantity: {suggested_qty}"
                    response += f"\nActual Quantity: {quantity}"
                    response += f"\nInvestment Utilization: {utilization:.1f}%"
                    
                    if abs(result['total_amount'] - target_investment) > target_investment * 0.1:
                        response += f"\n⚠️ Significant difference from target investment"
            else:
                response = f"❌ {result['message']}"
            
            # Clear user session
            del self.user_sessions[update.effective_user.id]
            
            await update.message.reply_text(response)
            
        except ValueError:
            await update.message.reply_text("❌ Invalid numbers. Please check your input.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def process_sell_transaction(self, update, context, message_text, session):
        """Process sell transaction"""
        try:
            parts = message_text.strip().split(',')
            if len(parts) != 2:
                await update.message.reply_text("❌ Invalid format. Use: QUANTITY,PRICE")
                return
            
            quantity = int(parts[0].strip())
            price = float(parts[1].strip())
            
            # Validate inputs
            is_valid, validation_msg = self.strategy.validate_transaction_inputs(quantity, price)
            if not is_valid:
                await update.message.reply_text(f"❌ {validation_msg}")
                return
            
            # Execute transaction
            result = self.strategy.execute_sell_recommendation(
                session['recommendation'], quantity, price
            )
            
            if result['success']:
                response = f"✅ {result['message']}\n"
                response += f"Profit: ₹{result['profit']:,.2f} ({result['profit_percent']:.2f}%)"
            else:
                response = f"❌ {result['message']}"
            
            # Clear user session
            del self.user_sessions[update.effective_user.id]
            
            await update.message.reply_text(response)
            
        except ValueError:
            await update.message.reply_text("❌ Invalid numbers. Please check your input.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    def run(self):
        """Run the bot"""
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Initialize ETF list
        try:
            self.data_manager.load_etf_list_from_excel("etf-list.xlsx")
            logger.info("ETF list loaded successfully")
        except Exception as e:
            logger.error(f"Error loading ETF list: {e}")
        
        # Run the bot
        logger.info("Starting ETF Trading Bot...")
        application.run_polling()

if __name__ == "__main__":
    # Load bot token from config file
    try:
        from bot_config import BOT_TOKEN
        
        if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
            print("Please set your Telegram Bot Token in bot_config.py!")
            print("1. Create a new bot with @BotFather on Telegram")
            print("2. Get the token and replace BOT_TOKEN in bot_config.py")
            exit(1)
        
        print("🤖 Starting ETF Trading Telegram Bot...")
        print(f"Bot token loaded successfully!")
        
        bot = ETFTradingBot(BOT_TOKEN)
        bot.run()
        
    except ImportError:
        print("❌ bot_config.py file not found!")
        print("Please create bot_config.py with your bot token")
        exit(1)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        exit(1)