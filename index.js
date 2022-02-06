const { Telegraf } = require('telegraf');
const express  = require('express');
const moment = require('moment');
const requestPromise = require('request-promise-native');
require('dotenv').config();
const app = express();

const BEGINNING_TIME = moment('6:00', 'h:mm');

const bot = new Telegraf(process.env.BOT_TOKEN)
bot.start((ctx) => {
    let message = ` Please use the menu to see the available options`;
    ctx.reply(message);
})
bot.command('ora', async (ctx) => {
    let htmlTemplate = await getCurrentSchedule();
    ctx.replyWithHTML(htmlTemplate);
});

// Launch bot
bot.launch();

// Enable graceful stop
process.once('SIGINT', () => bot.stop('SIGINT'))
process.once('SIGTERM', () => bot.stop('SIGTERM'))

const getCurrentSchedule = async () => {
    let date = moment().isBefore(BEGINNING_TIME) ? 
                moment().subtract(1, 'days').format('YYYY-MM-DD') 
                :
                moment().format('YYYY-MM-DD');
    let jsonResponse = await fetchData(date);
    return jsonResponse;
};

const fetchData = (date) => {
    console.log(process.env.NEW_API_URL);
    let options = {
        // uri: process.env.API_URL.replace('{DATE_MACRO}', date),
        uri: process.env.NEW_API_URL,
        json: true
    };
    return requestPromise(options)
        .then(function(data) {
            console.log(data.testo);
            return data.testo;
        })
        .catch(function(err) {
            console.log(err);
        });
};

