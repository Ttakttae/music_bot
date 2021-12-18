const { Client, Intents } = require('discord.js');
const { token } = require("./token.json");
const ytdl = require('ytdl-core');
const clientId = '882994932221116417';
const lng = require('./scripts/translate.js');

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
        await interaction.reply(String(lng.tl(interaction.guildId, 'made_by')));
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
    } else if (commandName === 'language_change') {
        const language = interaction.options.getString('language');
        lng.language_change(interaction.guildId, language);
        await interaction.reply(String(lng.tl(interaction.guildId, 'voice.set_language')))
    }
});

client.login(token);