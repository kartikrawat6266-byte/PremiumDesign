const TelegramBot = require('node-telegram-bot-api');

const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
if (!TOKEN) {
  console.error("❌ TELEGRAM_BOT_TOKEN environment variable not set!");
  process.exit(1);
}

// Polling mode – Railway ke liye best
const bot = new TelegramBot(TOKEN, { polling: true });

console.log("🤖 Bot started with polling...");

// Green & Red inline keyboard
const mainKeyboard = {
  reply_markup: {
    inline_keyboard: [
      [{ text: '🛒 Shop Now', callback_data: 'shop' }],
      [{ text: '📦 My Orders', callback_data: 'orders' }],
      [{ text: '👤 Profile', callback_data: 'profile' }],
      [{ text: '📘 How to Use', callback_data: 'howto' }],
      [{ text: '🎧 Support', callback_data: 'support' }],
      [{ text: '🎁 Refer & Earn', callback_data: 'refer' }],
      [{ text: '📋 Menu', callback_data: 'menu' }, { text: '💬 Message', callback_data: 'message' }]
    ]
  }
};

// /start command
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, '🚆 *Railway Bot Active* \nChoose an option:', {
    parse_mode: 'Markdown',
    ...mainKeyboard
  });
});

// Button callback responses
bot.on('callback_query', (query) => {
  const chatId = query.message.chat.id;
  const data = query.data;
  let reply = '';

  switch (data) {
    case 'shop': reply = '🛒 *Shop Now* – All keys available instantly!\n\n🔑 GTA V: $10\n🔑 Steam Wallet: $5\n🔑 FreeFire diamonds: ₹50'; break;
    case 'orders': reply = '📦 *My Orders*\n• #FF123 – Diamonds (Delivered)\n• #FF456 – Elite Pass (Pending)'; break;
    case 'profile': reply = '👤 *Profile*\nUsername: @' + (query.from.username || 'user') + '\nBalance: $0.00\nMember since: 2025'; break;
    case 'howto': reply = '📘 *How to Use*\n1️⃣ Send /start\n2️⃣ Tap any green button to buy\n3️⃣ Payment via UPI / Crypto\n4️⃣ Instant delivery in DM'; break;
    case 'support': reply = '🎧 *Support* (Red alert)\nContact admin: @support_admin\nOr create ticket: /ticket'; break;
    case 'refer': reply = '🎁 *Refer & Earn*\nInvite friends – earn $5 each\nYour link: https://t.me/yourbot?start=ref_123'; break;
    case 'menu': reply = '📋 *Main Menu* – Use the buttons below.'; break;
    case 'message': reply = '💬 *Message* – Send /feedback your message to admin.'; break;
    default: reply = '❓ Unknown option';
  }

  bot.sendMessage(chatId, reply, { parse_mode: 'Markdown', ...mainKeyboard });
  bot.answerCallbackQuery(query.id);
});

// /help command
bot.onText(/\/help/, (msg) => {
  bot.sendMessage(msg.chat.id, 'Send /start to see the main menu.', mainKeyboard);
});

console.log("✅ Bot is ready – polling mode active");
