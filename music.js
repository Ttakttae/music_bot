const { Client, Intents } = require('discord.js');
const { SlashCommandBuilder } = require('@discordjs/builders');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const { token } = require("./token.json");
const ytdl = require('ytdl-core');
const clientId = '882994932221116417';

const client = new Client({ intents: [Intents.FLAGS.GUILDS] });

const commands = [
    new SlashCommandBuilder().setName('ping').setDescription('Pong!으로 대답합니다'),
    new SlashCommandBuilder().setName('madeby').setDescription('만든이를 보여줍니다'),
    new SlashCommandBuilder().setName('join').setDescription('통화방에 입장합니다'),
    new SlashCommandBuilder().setName('leave').setDescription('통화방에서 나갑니다'),
    new SlashCommandBuilder().setName('play').setDescription('음악을 재생합니다').addStringOption(option => option.setName('url').setDescription('url').setRequired(true)),
    new SlashCommandBuilder().setName('pause').setDescription('음악을 일시중지합니다'),
    new SlashCommandBuilder().setName('resume').setDescription('음악을 다시 재생합니다'),
    new SlashCommandBuilder().setName('playlist').setDescription('재생목록을 보여줍니다'),
    new SlashCommandBuilder().setName('skip').setDescription('노래를 건너 띕니다'),
    new SlashCommandBuilder().setName('delete').setDescription('노래를 삭제합니다'),

]
    .map(command => command.toJSON());

const rest = new REST({ version: '9' }).setToken(token);

rest.put(Routes.applicationCommands(clientId), { body: commands },)
    .then(() => console.log('Successfully registered application commands.'))
    .catch(console.error);

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