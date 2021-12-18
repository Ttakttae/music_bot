const { Client, Intents, MessageActionRow, MessageButton } = require('discord.js');
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
        const voiceChannel = interaction.member
        if (voiceChannel){
            voiceChannel.join();
            await interaction.reply('통화방에 입장합니다');
        } else {
            await interaction.reply('통화방에 입장한 후 명령해주세요');
        }
    } else if (commandName === 'leave') {
        const voiceChannel = member.voice.channel;
        if (voiceChannel){
            voiceChannel.leave();
            await interaction.reply('통화방에서 나갑니다');
        } else {
            await interaction.reply('통화방에 입장한 후 명령해주세요');
        }
    } else if (commandName === 'play') {
        const song = interaction.options.getString('song');
        await interaction.reply('노래를 찾는중입니다');
    } else if (commandName === 'pause') {

    } else if (commandName === 'resume') {

    } else if (commandName === 'playlist') {

    } else if (commandName === 'skip') {

    } else if (commandName === 'delete') {
        const number = interaction.options.getNumber('number');

    } else if (commandName === 'loop') {
        const mode = interaction.options.getString('mode');

    } else if (commandName === 'language_change') {
        const language = new MessageActionRow().addComponents(new MessageButton().setCustomId('korean').setLabel('Korean').setStyle('PRIMARY')).addComponents(new MessageButton().setCustomId('english').setLabel('English').setStyle('SECONDARY')).addComponents(new MessageButton().setCustomId('chinese').setLabel('Chinese').setStyle('SUCCESS')).addComponents(new MessageButton().setCustomId('japanese').setLabel('Japanese').setStyle('DANGER'));
        await interaction.reply({ content: String(lng.tl(interaction.guildId, 'choose.lang')), components: [language] });
    } else if (commandName === 'billboard') {
        const number = interaction.options.getNumber('language');

    } else if (commandName === 'lyrics') {
        const artist = interaction.options.getString('artist');
        const title = interaction.options.getString('title');

    } else if (commandName === 'clear') {

    } else if (commandName === 'seek') {
        const number = interaction.options.getString('number');

    } else if (commandName === 'move') {
        const channel = interaction.options.getChannel('channel');

    }
});

client.on('interactionCreate', async interaction => {
    if (!interaction.isButton()) return;
    const { customId } = interaction;
    if (customId === 'korean'){
        interaction.component.setDisabled(true);
        interaction.update({
            components: [
                new MessageActionRow().addComponents(interaction.component)
            ]
        });
        lng.language_change(interaction.guildId, 'ko_KR');
    } else if (customId === 'english'){
        interaction.component.setDisabled(true);
        interaction.update({
            components: [
                new MessageActionRow().addComponents(interaction.component)
            ]
        });
        lng.language_change(interaction.guildId, 'en_US');
    } else if (customId === 'chinese'){
        interaction.component.setDisabled(true);
        interaction.update({
            components: [
                new MessageActionRow().addComponents(interaction.component)
            ]
        });
        lng.language_change(interaction.guildId, 'zh_CN');
    } else if (customId === 'japanese'){
        interaction.component.setDisabled(true);
        interaction.update({
            components: [
                new MessageActionRow().addComponents(interaction.component)
            ]
        });
        lng.language_change(interaction.guildId, 'ja_JP');
    }
});

client.login(token);