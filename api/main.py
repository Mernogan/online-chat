import asyncio
from flask import Flask
from pywebio.platform.flask import webio_view
from pywebio.input import *
from pywebio.output import *
from pywebio.session import run_async, set_env

app = Flask(__name__)
app.secret_key = '\x17\xdd\x86/\x023\xe2\x14\x15\x9c\x891\x8a\x81a\x8dO\x1b\xb6\x84\xf6\xd4'

chat_msgs = []
online_users = set()
MAX_MESSAGES_COUNT = 100

async def main():
    global chat_msgs

    set_env(title="Just chatting", output_animation=False)
    put_markdown("## Добро пожаловать в Mernogan chat")

    msg_box = output()
    put_scrollable(msg_box, height=300, keep_bottom=True)

    nickname = await input("Войти в чат", required=True, placeholder="Ваше имя",
                           validate=lambda n: "Такой ник уже используется!" if n in online_users or n == 'Объявление' else None)
    online_users.add(nickname)

    chat_msgs.append(('Объявление', f'`{nickname}` подключился'))
    msg_box.append(put_markdown(f'`{nickname}` подключился'))

    refresh_task = run_async(refresh_msg(nickname, msg_box))

    try:
        while True:
            data = await input_group("Новое сообщение", [
                input(placeholder="Сообщение", name="msg"),
                actions(name="cmd", buttons=["Отправить", {'label': "Выход из чата", 'type': 'cancel'}])
            ], validate=lambda m: ('msg', "Введите текст сообщения") if m["cmd"] == "Отправить" and not m['msg'] else None)

            if data is None:
                break

            msg_box.append(put_markdown(f"`{nickname}`: {data['msg']}"))
            chat_msgs.append((nickname, data['msg']))

    finally:
        # Cancel the refresh task
        refresh_task.cancel()
        try:
            await refresh_task  # Await cancellation
        except asyncio.CancelledError:
            pass  # Handle the cancellation gracefully

        online_users.remove(nickname)
        toast("Вы покинули чат")
        msg_box.append(put_markdown(f'Пользователь `{nickname}` покинул чат!'))
        chat_msgs.append(('Объявление', f'Пользователь `{nickname}` покинул чат!'))

        put_buttons(['Перезайти'], onclick=lambda btn: run_js('window.location.reload()'))

async def refresh_msg(nickname, msg_box):
    global chat_msgs
    last_idx = len(chat_msgs)

    while True:
        await asyncio.sleep(1)

        for m in chat_msgs[last_idx:]:
            if m[0] != nickname:  # if not a message from current user
                msg_box.append(put_markdown(f"`{m[0]}`: {m[1]}"))

        # Remove expired messages
        if len(chat_msgs) > MAX_MESSAGES_COUNT:
            chat_msgs = chat_msgs[len(chat_msgs) // 2:]

        last_idx = len(chat_msgs)

@app.route('/')
def index():
    return webio_view(main)()

if __name__ == "__main__":
    app.run(debug=False)

Найти еще
