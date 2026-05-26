const TelegramBot = require('node-telegram-bot-api');
const express = require('express');

const TOKEN = process.env.TELEGRAM_BOT_TOKEN; // Railway environment variable mein daalna
if (!TOKEN) throw new Error('TELEGRAM_BOT_TOKEN missing');

// Webhook mode for Railway (production)
const bot = new TelegramBot(TOKEN);
const app = express();

// Webhook endpoint
app.use(express.json());
app.post(`/webhook/${TOKEN}`, (req, res) => {
  bot.processUpdate(req.body);
  res.sendStatus(200);
});

// Start express server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Bot webhook running on port ${PORT}`);
});

// Set webhook (Railway ka public URL chahiye)
const webhookUrl = `${process.env.RAILWAY_PUBLIC_DOMAIN}/webhook/${TOKEN}`;
bot.setWebHook(webhookUrl).then(() => {
  console.log(`Webhook set to ${webhookUrl}`);
}).catch(console.error);

// Green & Red inline keyboard
const mainKeyboard = {
  reply_markup: {
    inline_keyboard: [
      [{ text: '🛒 Shop Now', callback_data: 'shop', color: 'green' }],
      [{ text: '📦 My Orders', callback_data: 'orders', color: 'green' }],
      [{ text: '👤 Profile', callback_data: 'profile', color: 'green' }],
      [{ text: '📘 How to Use', callback_data: 'howto', color: 'green' }],
      [{ text: '🎧 Support', callback_data: 'support', color: 'red' }],
      [{ text: '🎁 Refer & Earn', callback_data: 'refer', color: 'green' }],
      [{ text: '📋 Menu', callback_data: 'menu' }, { text: '💬 Message', callback_data: 'message' }]
    ]
  }
};

// Handle /start command
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, '🚆 *Railway Bot Active* \nChoose an option:', {
    parse_mode: 'Markdown',
    ...mainKeyboard
  });
});

// Handle callback queries (button presses)
bot.on('callback_query', (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;
  let reply = '';

  switch (data) {
    case 'shop': reply = '🛒 *Shop Now* – All keys available instantly!\n\n🔑 GTA V: $10\n🔑 Steam Wallet: $5\n🔑 FreeFire diamonds: ₹50'; break;
    case 'orders': reply = '📦 *My Orders*\n• #FF123 – Diamonds (Delivered)\n• #FF456 – Elite Pass (Pending)'; break;
    case 'profile': reply = '👤 *Profile*\nUsername: @' + query.from.username + '\nBalance: $0.00\nMember since: 2025'; break;
    case 'howto': reply = '📘 *How to Use*\n1️⃣ Send /start\n2️⃣ Tap any green button to buy\n3️⃣ Payment via UPI / Crypto\n4️⃣ Instant delivery in DM'; break;
    case 'support': reply = '🎧 *Support* (Red alert)\nContact admin: @support_admin\nOr create ticket: /ticket'; break;
    case 'refer': reply = '🎁 *Refer & Earn*\nInvite friends – earn $5 each\nYour link: https://t.me/yourbot?start=ref_123'; break;
    case 'menu': reply = '📋 *Main Menu* – Use the buttons below.'; break;
    case 'message': reply = '💬 *Message* – Send /feedback your message to admin.'; break;
    default: reply = '❓ Unknown option';
  }

  bot.sendMessage(chatId, reply, { parse_mode: 'Markdown', ...mainKeyboard });
  bot.answerCallbackQuery(query.id); // remove loading state
});

// Optional: /help command
bot.onText(/\/help/, (msg) => {
  bot.sendMessage(msg.chat.id, 'Use /start to see the green & red button menu.', mainKeyboard);
});
