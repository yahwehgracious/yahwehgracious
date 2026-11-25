/**
 * Журнал помилок і відгуків ШІ-таргетолога.
 * Застосунок шле сюди POST з текстом помилки (ключі вже вирізані на телефоні).
 * Ми дописуємо рядок у перший лист таблиці і шлемо сповіщення в Telegram.
 *
 * Налаштування (один раз):
 * 1. Розширення → Apps Script → встав цей код → збережи.
 * 2. Налаштування проєкту (шестерня) → Властивості скрипта → додай:
 *    BOT_TOKEN = токен бота, CHAT_ID = твій Telegram ID.
 * 3. Розгорнути → Нове розгортання → тип «Вебзастосунок» →
 *    Виконувати як: «Я», Доступ: «Усі» → Розгорнути → дозволи → скопіюй URL (…/exec).
 */
function doPost(e) {
  var d = {};
  try { d = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (x) { d = { kind: 'bad', msg: String(e && e.postData && e.postData.contents).slice(0, 300) }; }
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheets()[0];
  if (sh.getLastRow() === 0) {
    sh.appendRow(['Час', 'Тип', 'Повідомлення', 'Деталі', 'Telegram ID', 'Нік', "Ім'я", 'Кабінет', 'ID кабінету', 'Екран', 'Версія', 'Пристрій']);
    sh.setFrozenRows(1);
  }
  var cut = function (v, n) { return String(v == null ? '' : v).slice(0, n); };
  sh.appendRow([new Date(), cut(d.kind, 20), cut(d.msg, 600), cut(d.extra, 600), cut(d.uid, 20), cut(d.user, 40), cut(d.name, 60),
                cut(d.cab, 80), cut(d.acc, 30), cut(d.screen, 40), cut(d.ver, 30), cut(d.ua, 140)]);

  var p = PropertiesService.getScriptProperties();
  var tok = p.getProperty('BOT_TOKEN'), chat = p.getProperty('CHAT_ID');
  // однакова помилка шле сповіщення не частіше ніж раз на годину
  var key = 'n_' + Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.MD5, cut(d.kind, 20) + cut(d.msg, 200)));
  var cache = CacheService.getScriptCache();
  if (tok && chat && (d.kind === 'feedback' || !cache.get(key))) {
    cache.put(key, '1', 3600);
    var icon = d.kind === 'feedback' ? '💬 Відгук' : '⚠️ Помилка';
    var who = d.user ? '@' + d.user : (d.name || d.uid || '—');
    UrlFetchApp.fetch('https://api.telegram.org/bot' + tok + '/sendMessage', {
      method: 'post', contentType: 'application/json', muteHttpExceptions: true,
      payload: JSON.stringify({ chat_id: chat, text: icon + ' · ' + (d.cab || '—') + ' · ' + who + '\n' + cut(d.msg, 900) + (d.screen ? '\nЕкран: ' + d.screen : '') })
    });
  }
  return ContentService.createTextOutput('ok');
}
