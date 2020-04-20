import pickle
import time, sched
import json
import telepot
from telepot.loop import MessageLoop

from patchnotes import getChanges

from random import randint

from os.path import isfile

from riotwatcher import RiotWatcher, ApiError


chats = set()
inter = {}
messages = []

def init():
    if isfile("inter_chats.pkl"):
        with open("inter_chats.pkl", 'rb') as f:
            chats.update(pickle.load(f))
    if isfile("inter.pkl"):
        with open("inter.pkl", 'rb') as f:
            inter.update(pickle.load(f))
    with open("int_messages.txt", 'r', encoding='utf-8') as f:
        for msg in f:
            messages.append(msg)
        
    with open("int_config.json", 'r', encoding="utf-8") as f:
        config = json.load(f)

        global watcher 
        watcher = RiotWatcher(config['apiKey'])
        global bot 
        bot = telepot.Bot(config['botToken'])

    global scheduler
    scheduler = sched.scheduler(time.time, time.sleep)


def add_inter(username):
    if username not in inter:
        try:
            id = watcher.summoner.by_name('euw1', username)['accountId']
        except Exception:
            return
        
        inter[username] = id
        with open("inter.pkl", 'wb') as f:
            pickle.dump(inter, f)

def remove_inter(username):
    if username in inter:
        del inter[username]
        with open("inter.pkl", 'wb') as f:
            pickle.dump(inter, f)

def add_chats(chat_id):
    chats.add(chat_id)
    with open("inter_chats.pkl", 'wb') as f:
        pickle.dump(chats, f)

def remove_chats(chat_id):
    chats.discard(chat_id)
    with open("inter_chats.pkl", 'wb') as f:
        pickle.dump(chats, f)

def handle(msg):

    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':

        print('Message received: {}'.format(msg['text']))

        if msg['text'].startswith('/inter'):
            commands = msg['text'].split(' ', 1)

            if len(commands)>1:
                neuer_inter = commands[1]        
                add_inter(neuer_inter)
                bot.sendMessage(chat_id, "Du bist ein Inter, {neuer_inter} 🥴".format(neuer_inter=neuer_inter))
            else:
                bot.sendMessage(chat_id, "nutzung: /inter [username des inters] 🥴")

        elif msg['text'].startswith('/keinInter'):
            commands = msg['text'].split(' ', 1)
            if len(commands)>1:
                neuer_inter = commands[1]        
                remove_inter(neuer_inter)
                bot.sendMessage(chat_id, "Du bist definitiv trotzdem ein Inter, {neuer_inter} 🥴".format(neuer_inter=neuer_inter))
            else:
                bot.sendMessage(chat_id, "nutzung: /keinInter [username des inters] 🥴")

        elif msg['text'].startswith('/hierGibtsInter'):
            add_chats(chat_id)
            bot.sendMessage(chat_id, "OP.GG overrated, long have we waited, intbot activated 🥴")

        elif msg['text'].startswith('/hierGibtsKeineInter'):
            remove_chats(chat_id)
            bot.sendMessage(chat_id, "Das glaube ich dir nicht ")

        elif msg['text'] == '/reee':
            bot.sendMessage(chat_id, '🥴')


def sendIntMessage(userName, k, d, a, champ, win):
    msg = messages[randint(0, len(messages)-1)].format(player=userName, champ=champ, k=k, d=d, a=a)
    print(msg)
    for chat_id in chats:
        bot.sendMessage(chat_id, msg)

def isInt(kills, deaths, assists):
    return False if deaths < 3 else (kills+0.8*assists)/deaths < 1        

def getKDAs(userName):
    kdas = []
    games = watcher.match.matchlist_by_account('euw1', inter[userName], begin_time=int((time.time()-3600*24)*1000))['matches']
    for g in games:
        champion = g['champion']
        gameId = g['gameId']
        game = watcher.match.by_id('euw1', gameId)
        for participant in game['participantIdentities']:
            if participant['player']['summonerName'] == userName:
                pId = participant['participantId']
                break

        for p in game['participants']:
            if p['participantId'] == pId:
                stats = p['stats']
                k = stats['kills']
                a = stats['assists']
                d = stats['deaths']
                win = stats['win']
                kdas.append((k, d, a, champion, win))
        print(game)


    return kdas

def checkInt(userName):
    print("Checking games for {}".format(userName))
    for k, d, a, champ, win in getKDAs(userName):
        if isInt(k, d, a):
            sendIntMessage(userName, k, d, a, champ, win)

def regulerIntWatch():
    print("Checking for inters...")
    for user in inter:
        checkInt(user)
    scheduler.enter(60*30, 1, regulerIntWatch)


if __name__ == "__main__":
    init()
    scheduler.enter(1, 1, regulerIntWatch)

    MessageLoop(bot, handle).run_as_thread()
    scheduler.run()
    print('Waiting for Message...')
    while 1:
        time.sleep(10)
