const { Telegraf } = require('telegraf');
const express  = require('express');
require('dotenv').config();
const app = express();

const bot = new Telegraf(process.env.BOT_TOKEN)

bot.start((ctx) => {
    let message = ` Please use the menu to see the available options`;
    ctx.reply(message);
})
bot.command('ora', (ctx) => ctx.replyWithDice());

// Launch bot
bot.launch();

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'))
process.once('SIGTERM', () => bot.stop('SIGTERM'))