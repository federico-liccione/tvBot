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
bot.command('ora', (ctx) => {
    let htmlTemplate = getCurrentSchedule();
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
    console.log(jsonResponse.template);
    return jsonResponse.template;
};

const fetchData = (date) => {
    let options = {
        // uri: process.env.API_URL.replace('{DATE_MACRO}', date),
        uri: process.env.NEW_API_URL,
        json: true
    };
    return requestPromise(options)
        .then(function(data) {
            return data;
        })
        .catch(function(err) {
            console.log(err);
        });
};

const formatResponse = () => {

};

getCurrentSchedule();