import applescript
import time
import yaml

from subprocess import call
from pathlib import Path

from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty, ChatForbidden
 
# Считываем учетные данные
with open(Path(__file__).parent / 'config.yaml') as f:
    config = yaml.safe_load(f)

# Присваиваем значения внутренним переменным
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
username = config['Telegram']['username']
proxy = None  # (proxy_server, proxy_port, proxy_key)

last_message = {'id': None}

client = TelegramClient(username, api_id, api_hash)
client.start()

def alarm_until_dead():
    call(['say', 'Wake up!'])

    try:
        applescript.run("set volume output volume 100")
    except:
        pass

    sleep_time = 10.
    time.sleep(sleep_time)

    while True:
        call(['say', 'Wake up!'])
        if sleep_time > 0.1:
            sleep_time /= 2

        time.sleep(sleep_time)


async def check_for_new_messages(channel):
    messages = await client(GetHistoryRequest(
        peer=channel,
        limit=1,
        offset_date=None,
        offset_id=0,
        max_id=0,
        min_id=0,
        add_offset=0,
        hash=0
    ))
    if last_message['id'] is None:
        last_message['id'] = messages.messages[0].id

    return last_message['id'] != messages.messages[0].id


result = client(GetDialogsRequest(
            offset_date=None,
            offset_id=0,
            offset_peer=InputPeerEmpty(),
            limit=100,
            hash=0))

entities = result.chats
entity = None
for e in entities:
    if str(config['chat']['name']) in str(e) and not isinstance(e, ChatForbidden):
        entity = e
        break


async def main():
    if entity is None:
        chat = await client.get_entity(config['chat']['name'])
    else:
        chat = entity

    print('start polling on entity:', chat.__dict__.get('title', chat.__dict__.get('username')))
    while True:
        if await check_for_new_messages(chat):
            alarm_until_dead()

        time.sleep(20.)

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())
