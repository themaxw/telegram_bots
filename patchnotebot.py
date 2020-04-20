import telepot
from telepot.loop import MessageLoop
from patchnotes import getChanges
import time
import json

with open("patch_config.json", 'r', encoding="utf-8") as f:
    config = json.load(f)

    global bot
    bot = telepot.Bot(config['botToken'])


def buildMessage(changes, title, detailed=True):

    summary = ''
    if 'summary' in changes[title]:
        summary = changes[title]['summary']

    description = ''
    if 'description' in changes[title]:
        description = changes[title]['description']

    spells = []
    if 'spells' in changes[title]:
        spells = changes[title]['spells']

    message = "🔵 *{}*\n\n{}".format(title, summary)
    if detailed:
        message = message + "\n\n{}\n".format(description)
        for s in spells:
            message = message + "\n\n***{}***".format(s['name'])
            for ch in s['changes']:
                message = message + "_{}_".format(ch)

    return message


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text':

        print('Message received: {}'.format(msg['text']))

        if msg['text'].startswith('/detailed'):

            changes = getChanges()
            champion = ''
            commands = msg['text'].split(' ')

            if len(commands) > 1:
                champion = commands[1]

            for title in changes.keys():

                if champion and title != champion:
                    continue

                message = buildMessage(changes, title, detailed=True)

                bot.sendMessage(chat_id, message, parse_mode='Markdown')

        if msg['text'].startswith('/overview'):
            changes = getChanges()
            for title in changes.keys():

                message = buildMessage(changes, title, detailed=False)

                bot.sendMessage(chat_id, message, parse_mode='Markdown')

        elif msg['text'] == '/reee':
            bot.sendMessage(chat_id, '🥴')


MessageLoop(bot, handle).run_as_thread()
print('Waiting for Message...')
while 1:
    time.sleep(10)
