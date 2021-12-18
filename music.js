const { Client, Intents } = require('discord.js');
const { token } = require("./token.json");
const ytdl = require('ytdl-core');
const clientId = '882994932221116417';
const KO_KR = require('./language_data/ko-KR.json');
const EN_US = require('./language_data/en-US.json');
const ZH_CN = require('./language_data/zh-CN.json');
const JA_JP = require('./language_data/ja-JP.json');
const server_langs = require('./language_data/server_language.json');

const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

client.once('ready', () => {
    client.user.setActivity('/명령어', { type: 'LISTENING' })
    console.log('Ready!');
});

client.on('interactionCreate', async interaction => {
    if (!interaction.isCommand()) return;
    const { commandName } = interaction;
    if (commandName === 'ping') {
        await interaction.reply('Pong!');
    } else if (commandName === 'madeby') {
        await interaction.reply('만든이 : MBP16#3062, 쿠로#8927');
    } else if (commandName === 'join') {
        const voiceChannel = interaction.member.voice.channel;
        if (voiceChannel){
            voiceChannel.join()
            await interaction.reply('통화방에 입장합니다')
        } else {
            await interaction.reply('통화방에 입장한 후 명령해주세요')
        }
    } else if (commandName === 'leave') {
        const voiceChannel = member.voice.channel;
        if (voiceChannel){
            voiceChannel.leave()
            await interaction.reply('통화방에서 나갑니다')
        } else {
            await interaction.reply('통화방에 입장한 후 명령해주세요')
        }
    } else if (commandName === 'play') {
        await interaction.reply('노래를 찾는중입니다')
    }
});

client.login(token);