const { SlashCommandBuilder } = require('@discordjs/builders');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const { token } = require("../token.json");
const clientId = '882994932221116417';

const commands = [
    new SlashCommandBuilder().setName('ping').setDescription('Pong!'),
    new SlashCommandBuilder().setName('madeby').setDescription('만든이'),
    new SlashCommandBuilder().setName('join').setDescription('음성 채널에 입장합니다'),
    new SlashCommandBuilder().setName('leave').setDescription('음성채널에서 나갑니다'),
    new SlashCommandBuilder().setName('play').setDescription('노래를 재생합니다').addStringOption(option => option.setName('song').setDescription('유튜브 링크나 검색 키워드(라이브 스트리밍, 플레이리스트, 그냥 동영상 모두 가능)').setRequired(true)),
    new SlashCommandBuilder().setName('pause').setDescription('노래를 잠시 중지합니다'),
    new SlashCommandBuilder().setName('resume').setDescription('노래를 다시 재생합니다'),
    new SlashCommandBuilder().setName('playlist').setDescription('재생목록을 보여줍니다'),
    new SlashCommandBuilder().setName('skip').setDescription('노래를 건너뜁니다'),
    new SlashCommandBuilder().setName('delete').setDescription('노래를 삭제합니다').addNumberOption(option => option.setName('number').setDescription('삭제할 노래의 숫자(재생목록에 나온 숫자 기준)').setRequired(true)),
    new SlashCommandBuilder().setName('loop').setDescription('노래 한곡이나 전체를 반복하거나, 반복을 끕니다').addStringOption(option => option.setName('mode').setDescription('한곡: single, 전체: all, 셔플(무작위 재생): shuffle, 끄기: off').setRequired(true)),
    new SlashCommandBuilder().setName('language_change').setDescription('출력되는 언어(slash command 이름이나 설명 아님)를 변경합니다').addStringOption(option => option.setName('language').setDescription('다음중 선택(korean, english, chinese, japanese)').setRequired(true)),
    new SlashCommandBuilder().setName('billboard').setDescription('빌보드 차트를 출력합거나, 숫자를 입력하면 그 숫자에 해당하는 노래를 재생합니다').addNumberOption(option => option.setName('number').setDescription('빌보드 차트 숫자(중복 선택 가능 ex: 30, 20, 15 또는 1~4)').setRequired(false)),
    new SlashCommandBuilder().setName('lyrics').setDescription('현재 재생중인 곡(플레이 리스트의 가장 상위 곡)의 가사를 보여줍니다(링크 사용했을시 작동 거의 안됨)').addStringOption(option => option.setName('artist').setDescription('더 정확한 검색을 위한 아티스트 변수').setRequired(false)).addStringOption(option => option.setName('title').setDescription('더 정확한 검색을 위한 제목 변수(키워드 검색 사용자들은 필요 없음)').setRequired(false)),
    new SlashCommandBuilder().setName('clear').setDescription('재생목록의 노래들을 초기화합니다'),
    new SlashCommandBuilder().setName('seek').setDescription('입력한 초에 해당하는 시간으로 이동합니다').addNumberOption(option => option.setName('number').setDescription('이동할 초').setRequired(true)),
    new SlashCommandBuilder().setName('move').setDescription('채널을 이동합니다(플레이 리스트 유지)').addChannelOption(option => option.setName('channel').setDescription('이동할 채널').setRequired(true))
]
    .map(command => command.toJSON());

const rest = new REST({ version: '9' }).setToken(token);

rest.put(Routes.applicationCommands(clientId), { body: commands },)
    .then(() => console.log('Successfully registered application commands.'))
    .catch(console.error);