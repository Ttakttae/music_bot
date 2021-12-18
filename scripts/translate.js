const ko_KR = require('../language_data/ko-KR.json');
const en_US = require('../language_data/en-US.json');
const zh_CN = require('../language_data/zh-CN.json');
const ja_JP = require('../language_data/ja-JP.json');
const fs = require('fs');
const tl = require("./translate");
const server_langs = require("../language_data/server_language.json");

var channel_languages = require('../language_data/server_language.json');

exports.tl = function (server_id, language_keyword) {
    var language_type = channel_languages[server_id];
    if (language_type) {
        var result = translate(language_type, language_keyword);
        return result;
    } else {
        set_language(server_id, "en_US");
        var result = translate(channel_languages[server_id], language_keyword);
        return result;
    }
}

function translate(language_type, language_keyword) {
    if (language_type === 'ko_KR'){
        var result = ko_KR[language_keyword];
    } else if (language_type === 'en_US'){
        var result = en_US[language_keyword];
    } else if (language_type === 'zh_CN'){
        var result = zh_CN[language_keyword];
    } else if (language_type === 'ja_JP'){
        var result = ja_JP[language_keyword];
    }
    return result;
}

exports.language_change = function (server_id, lang_to_change) {
    if (lang_to_change === 'korean'){
        set_language(server_id, "ko_KR");
    } else if (lang_to_change === 'english'){
        set_language(server_id, "en_US");
    } else if (lang_to_change === 'chinese'){
        set_language(server_id, "zh_CN");
    } else if (lang_to_change === 'japanese'){
        set_language(server_id, "ja_JP");
    }
}

function set_language(server_id, lang_to_set) {
    var a = JSON.parse(fs.readFileSync('./language_data/server_language.json', 'utf-8'));
    a[server_id] = lang_to_set;
    fs.writeFileSync('./language_data/server_language.json', JSON.stringify(a), "utf-8");
    channel_languages[server_id] = lang_to_set;
}