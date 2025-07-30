import logging
from typing import TypedDict

from telethon.errors import UserIsBlockedError
from telethon.helpers import get_running_loop
from telethon.network import connection

from folds import Bot, Message, ThisSender
from folds.rules.rule_builder_factory import abcdef

logging.basicConfig(level=logging.INFO)

bot = Bot(
    '818346669:AAEdMxSDl7JiueLDM9sWDfOQnvpDqqRpzrg',
    706892,
    '47e93a0906b7f34d1c7c390f78d774dd',
    connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
    proxy=('80.211.160.148', 14443, '7316c4fbc53fb9f4e6784f2a68c01461'),
)


@bot.added_to_group(regex='a')
async def greeting():
    return 'Hello! Thanks for adding me to your group.'


# @bot.group_commands.start
# async def


@bot.private_message
async def pm(user: ThisSender, m: Message):
    # client.send_message()
    return (
        f"Hello, {user.first_name}. I don't work in private chats. "
        "Please add me to your group to get started!"
    )

@bot.inline_query
async def f(command: Command, user: User | Chat, message: Message, state: State):
    check(state == State.Kek)

    if state != State.Kek:
        return

    return 'Hello!'


@bot.admin.group_message(regex=2)
async def f():
    return 'Lol'


@bot
async def hello_world(
    sender: Sender.User,
    chat: ThisChat.Private,
    state: State.Kek | State.Lol,
    message: ThisMessage,
):
    return 'Hello!'



@bot.private_message(state=State.Kek | State.Lol)
async def f(state: State.Kek | State.Lol):
    return 'Hello!'


@bot.private_message(state=State.Kek | State.Lol)
async def f(state: State.Kek | State.Lol):
    return 'Hello!'




@bot.admin_commands.lol
async def f(
    sender: ThisSender,
    message: Message,
    state: State.Kek | State.Lol,
):
    return 'Hello!'


#
# @bot.message('^варн (\w+)$')
# async def _(msg: Message, match: Match):
#     who = msg.group(1)

@bot.private_message / '^варн (\w+)$'
async def _(msg: Message, match: Match):
    who = msg.group(1)


async def on_start():
    try:
        await bot._client.send_message(
            'Не избранное',
            file='../../Downloads/Frame 1087-2.png'
        )
    except UserIsBlockedError:
        print(...)


class MyStates:
    class State1:
        info: str

    class State2:
        lol: int

    State3 = State()



if __name__ == '__main__':
    get_running_loop().run_until_complete(bot.app._run_test(on_start()))
    # bot.run()
