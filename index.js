const { Telegraf } = require('telegraf');
const express  = require('express');
const app = express();


const bot = new Telegraf(process.env.BOT_TOKEN)

bot.start((ctx) => {
    let message = ` Please use the /fact command to receive a new fact`
    ctx.reply(message)
})
bot.on('sticker', (ctx) => ctx.reply('👍'))
bot.launch();