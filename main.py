import time
import logging
import requests
import os
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

class MarketType(Enum):
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"
    COMMODITIES = "COMMODITIES"
    INDICES = "INDICES"

class TelegramNotifier:
    """Handle Telegram notifications"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}/"
        
    def send_message(self, text: str, parse_mode: str = "HTML", disable_notification: bool = False):
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_notification": disable_notification
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Telegram message sent successfully")
                return True
            else:
                logger.error(f"❌ Failed to send Telegram message: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error sending Telegram message: {e}")
            return False
    
    def send_elite_signal(self, data: Dict):
        """Send Elite Edition signal to Telegram"""
        try:
            # Extract all data
            symbol = data.get('symbol', 'UNKNOWN')
            direction = data.get('direction', 'UNKNOWN')
            signal_type = data.get('signal_type', 'UNKNOWN')
            pattern = data.get('pattern', 'UNKNOWN')
            entry = data.get('entry', 0)
            sl = data.get('stop_loss', 0)
            tp1 = data.get('tp1', 0)
            tp2 = data.get('tp2', 0)
            tp3 = data.get('tp3', 0)
            score = data.get('score', 0)
            mode = data.get('mode', 'UNKNOWN')
            session = data.get('session', 'UNKNOWN')
            timeframe = data.get('timeframe', '?')
            
            # Elite features
            bubble_detected = data.get('bubble_detected', False)
            bubble_strength = data.get('bubble_strength', 0)
            exhaustion_detected = data.get('exhaustion_detected', False)
            htf_trend = data.get('htf_trend', 'UNKNOWN')
            balanced_mode = data.get('balanced_mode', False)
            
            # Direction emoji and text
            if direction == "LONG":
                direction_emoji = "🟢"
                direction_text = "LONG / BUY"
                header_emoji = "🚀"
            else:
                direction_emoji = "🔴"
                direction_text = "SHORT / SELL"
                header_emoji = "📉"
            
            # Signal type emoji
            if signal_type == "REVERSAL":
                type_emoji = "🔄"
            else:
                type_emoji = "➡️"
            
            # Bubble strength indicator
            if bubble_strength == 3:
                bubble_text = "⚡⚡⚡ LEVEL 3 (INSTITUTIONAL!)"
                bubble_color = "🔥"
            elif bubble_strength == 2:
                bubble_text = "⚡⚡ LEVEL 2 (STRONG)"
                bubble_color = "✨"
            elif bubble_strength == 1:
                bubble_text = "⚡ LEVEL 1"
                bubble_color = "💫"
            else:
                bubble_text = "No Bubble"
                bubble_color = ""
            
            # Exhaustion indicator
            if exhaustion_detected:
                exhaustion_text = "⚠️ DETECTED (High Confidence!)"
            else:
                exhaustion_text = "None"
            
            # Score color
            if score >= 95:
                score_emoji = "🔥🔥🔥"
                quality = "EXCEPTIONAL"
            elif score >= 90:
                score_emoji = "🔥🔥"
                quality = "EXCELLENT"
            elif score >= 85:
                score_emoji = "🔥"
                quality = "GOOD"
            else:
                score_emoji = "✅"
                quality = "OK"
            
            # Mode indicator
            mode_text = "⚖️ BALANCED" if balanced_mode else "⚡ AGGRESSIVE"
            
            # Format numbers based on symbol
            def fmt_price(price):
                if "XAU" in symbol or "XAG" in symbol:
                    return f"{price:.2f}"
                elif "BTC" in symbol or "ETH" in symbol:
                    return f"{price:.2f}"
                elif "JPY" in symbol:
                    return f"{price:.3f}"
                else:
                    return f"{price:.5f}"
            
            entry_fmt = fmt_price(entry)
            sl_fmt = fmt_price(sl)
            tp1_fmt = fmt_price(tp1)
            tp2_fmt = fmt_price(tp2)
            tp3_fmt = fmt_price(tp3)
            
            # Calculate R:R
            if direction == "LONG":
                risk = entry - sl
            else:
                risk = sl - entry
            
            if risk > 0:
                rr1 = (abs(tp1 - entry) / risk)
                rr2 = (abs(tp2 - entry) / risk)
                rr3 = (abs(tp3 - entry) / risk)
            else:
                rr1 = rr2 = rr3 = 0
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
            
            # Build message
            message = f"""
<b>⚡ NEURAL ICC AI 2026 • ELITE EDITION</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{header_emoji} <b>{symbol} • {timeframe}</b>
{direction_emoji} <b>{direction_text}</b>
{type_emoji} <b>{signal_type}</b> • Pattern: {pattern}

<b>📊 ENTRY DETAILS</b>
├ Entry: <code>{entry_fmt}</code>
├ Stop Loss: <code>{sl_fmt}</code>
└ Risk: <code>{abs(entry - sl):.2f}</code> points

<b>🎯 TAKE PROFITS</b>
1️⃣ TP1: <code>{tp1_fmt}</code> ({rr1:.1f}R)
2️⃣ TP2: <code>{tp2_fmt}</code> ({rr2:.1f}R)
3️⃣ TP3: <code>{tp3_fmt}</code> ({rr3:.1f}R)

<b>🧠 AI ANALYSIS</b>
├ Score: {score_emoji} <b>{score}/100</b> ({quality})
├ Mode: {mode_text}
├ Session: {session}
└ HTF Trend: {htf_trend}

<b>💎 SMART MONEY</b>
├ Bubble: {bubble_color} {bubble_text}
└ Exhaustion: {exhaustion_text}

<i>🕐 {current_time}</i>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#{symbol.replace('/', '')} #{direction} #{mode}
"""
            
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"❌ Error creating Elite signal message: {e}")
            return False
    
    def send_tp_hit(self, data: Dict):
        """Send TP hit notification"""
        try:
            symbol = data.get('symbol', 'UNKNOWN')
            direction = data.get('direction', 'UNKNOWN')
            level = data.get('level', 'UNKNOWN')
            price = data.get('price', 0)
            
            # Determine level details
            if "TP1" in level:
                emoji = "💰"
                level_text = "TP1"
                comment = "First target hit! Consider moving SL to breakeven."
            elif "TP2" in level:
                emoji = "💰💰"
                level_text = "TP2"
                comment = "Second target hit! Trail your stop loss."
            elif "TP3" in level:
                emoji = "🚀🔥"
                level_text = "TP3 (FULL TARGET)"
                comment = "Final target hit! Exceptional trade!"
            else:
                emoji = "✅"
                level_text = level
                comment = "Target reached!"
            
            def fmt_price(price):
                if "XAU" in symbol or "XAG" in symbol:
                    return f"{price:.2f}"
                elif "BTC" in symbol or "ETH" in symbol:
                    return f"{price:.2f}"
                elif "JPY" in symbol:
                    return f"{price:.3f}"
                else:
                    return f"{price:.5f}"
            
            message = f"""
<b>{emoji} PROFIT HIT: {symbol}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>🎯 Level:</b> {level_text}
<b>{direction}</b> Position
<b>💵 Price:</b> <code>{fmt_price(price)}</code>

<i>{comment}</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#{symbol.replace('/', '')} #{level_text}
"""
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"❌ Error creating TP hit message: {e}")
            return False
    
    def send_sl_hit(self, data: Dict):
        """Send SL hit notification"""
        try:
            symbol = data.get('symbol', 'UNKNOWN')
            direction = data.get('direction', 'UNKNOWN')
            price = data.get('price', 0)
            
            def fmt_price(price):
                if "XAU" in symbol or "XAG" in symbol:
                    return f"{price:.2f}"
                elif "BTC" in symbol or "ETH" in symbol:
                    return f"{price:.2f}"
                elif "JPY" in symbol:
                    return f"{price:.3f}"
                else:
                    return f"{price:.5f}"
            
            message = f"""
<b>❌ STOP LOSS HIT: {symbol}</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<b>Direction:</b> {direction}
<b>💵 Price:</b> <code>{fmt_price(price)}</code>

<i>Trade closed. Wait for next setup.</i>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#{symbol.replace('/', '')} #SL
"""
            return self.send_message(message)
            
        except Exception as e:
            logger.error(f"❌ Error creating SL hit message: {e}")
            return False

class TradingBot:
    """Elite Trading Bot with Webhook Support"""
    
    def __init__(self):
        # Read credentials from environment variables
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.telegram_token or not self.chat_id:
            logger.warning("⚠️ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set! Notifications will fail.")
        else:
            self.telegram = TelegramNotifier(self.telegram_token, self.chat_id)
            logger.info("✅ Telegram notifier initialized")
    
    def process_webhook(self, data: Dict) -> bool:
        """Process incoming webhook from Elite indicator"""
        try:
            logger.info(f"📥 Received webhook data: {data}")
            
            # Check event type
            event = data.get('event', 'UNKNOWN')
            
            if event == 'NEW_TRADE':
                logger.info("🚀 Processing NEW_TRADE signal")
                if self.telegram:
                    return self.telegram.send_elite_signal(data)
                else:
                    logger.error("❌ Telegram not initialized")
                    return False
            
            elif event == 'TP_HIT':
                logger.info("💰 Processing TP_HIT notification")
                if self.telegram:
                    return self.telegram.send_tp_hit(data)
                else:
                    logger.error("❌ Telegram not initialized")
                    return False
            
            elif event == 'SL_HIT':
                logger.info("❌ Processing SL_HIT notification")
                if self.telegram:
                    return self.telegram.send_sl_hit(data)
                else:
                    logger.error("❌ Telegram not initialized")
                    return False
            
            else:
                logger.warning(f"⚠️ Unknown event type: {event}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing webhook: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

# Initialize bot instance
bot = TradingBot()

@app.route('/')
def home():
    return "⚡ Neural ICC AI 2026 • Elite Edition Bot Active 🟢", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        logger.info(f"📨 RAW PAYLOAD: {request.data}")
        logger.info(f"📋 ContentType: {request.headers.get('Content-Type')}")
        
        # Force parsing as JSON
        try:
            data = request.get_json(force=True, silent=True)
            if not data and request.data:
                import json
                data = json.loads(request.data.decode('utf-8'))
        except Exception as e:
            logger.error(f"❌ JSON parsing error: {e}")
            return jsonify({"error": "Invalid JSON format"}), 400
            
        if not data:
            logger.error("❌ No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400
        
        success = bot.process_webhook(data)
        
        if success:
            logger.info("✅ Signal processed and sent successfully")
            return jsonify({"status": "success", "message": "Signal processed"}), 200
        else:
            logger.warning("⚠️ Signal processing failed")
            return jsonify({"status": "failed", "message": "Signal processing failed"}), 200
            
    return jsonify({"error": "Method not allowed"}), 405

def main():
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Starting Elite Trading Bot on port {port}")
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    main()
