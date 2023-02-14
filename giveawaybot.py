import asyncio
import logging

import yaml
from telethon import TelegramClient, events, sync
from random import sample
from datetime import datetime


class User:
    def __init__(self, sender_id, name, message, dtime: datetime):
        self.sender_id = sender_id
        self.name = name
        self.message = message
        self.dtime = dtime


class ParsedData:
    def __init__(self, link_to_channel, post_id, total_winners, phrase_to_check):
        self.link_to_channel = link_to_channel
        self.post_id = post_id
        self.total_winners = total_winners
        self.phrase_to_check = phrase_to_check


class PostAddress:
    def __init__(self, link_to_channel, post_id):
        self.link_to_channel = link_to_channel
        self.post_number = post_id


class Rules:
    def __init__(self, total_winners, phrase_to_check):
        self.total_winners = total_winners
        self.phrase_to_check = phrase_to_check

    async def calc_result(self, users):
        if self.phrase_to_check:
            right_answered_arr = []
            for user in users:
                if user.message.lower().find(self.phrase_to_check.lower()) >= 0:
                    right_answered_arr.append(user)
            users = right_answered_arr

        users_map = dict()
        for user in users:
            users_map[user.sender_id] = user
        users = list(users_map.values())
        right_answered = len(users)
        winners = sample(users, min(right_answered, self.total_winners))
        winners = sorted(winners, key=lambda x: x.dtime)

        return Response(right_answered=right_answered, winners=winners, phrase_to_check=self.phrase_to_check)


class Response:
    def __init__(self, right_answered, winners, phrase_to_check):
        self.right_answered = right_answered
        self.winners = winners
        self.phrase_to_check = phrase_to_check

    def generate_response(self):
        x = "\n"
        if self.phrase_to_check:
            x += f'<b>Phrase checked: "{self.phrase_to_check}"</b>\n\n'
        else:
            x += "<b>No phrase was checked!</b>\n\n"
        x += f"Answered correctly: {self.right_answered}\n\nWinners:\n"
        for i in range(0, len(self.winners)):
            winner = self.winners[i]
            x += f'<b>{i+1}. {winner.name}</b> [{winner.dtime.strftime("%d/%m %H:%M:%S")}]:\n {winner.message}\n\n'
        return x


def parse_message(message: str):
    winners = 0
    phrase_to_check = ""
    link_to_channel = ""
    post_id = 0

    message = message.lower()
    message = message.splitlines()
    for line in message:
        line = line.strip()
        if line.startswith("https://t.me/"):
            splited = line.rsplit("/", 1)
            link_to_channel = splited[0]
            post_id_str = splited[1]
            try:
                post_id = int(post_id_str)
            except ValueError:
                return "post_id must be a non-negative number"
            continue

        if line.startswith("winners:"):
            line = line[len("winners:"):].strip()
            try:
                winners = int(line)
            except ValueError:
                return "winners must be a non-negative number"
            continue

        if line.startswith("phrase_to_check:"):
            phrase_to_check = line[len("phrase_to_check:"):].strip()
            continue

        if line:
            return f"unsupported command '{line}'"

    if winners == 0 or winners < 0:
        return "task must contains 'winners' > 0"
    if link_to_channel == "" or post_id <= 0:
        return "task must contains valid link of post"

    return ParsedData(link_to_channel, post_id, winners, phrase_to_check)


async def crawl_comments(bot, channel_link, post_id):
    users = []
    async for message in bot.iter_messages(channel_link, reply_to=post_id):
        users.append(User(message.sender_id, message.sender.first_name, message.text, message.date))
    return users


async def main():
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel("INFO")

    with open("config.yaml", "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        logger.info("config: %s", config)
    bot = TelegramClient(config["session_name"], config["api_id"], config["api_hash"])
    cms_giveaway_chat_id = config["cms_giveaway_chat_id"]

    @bot.on(events.NewMessage())
    async def handler(event):
        if event.message.chat_id != cms_giveaway_chat_id or \
                event.message.text.find('https://t.me/') < 0 or \
                event.message.text.find("winners:") < 0:
            return
        logger.info("Got a task: \n%s", event.message.text)

        parsed_data = parse_message(event.message.text)
        if type(parsed_data) == str:
            await event.reply("\n" + parsed_data)
            return
        logger.info("Parsed: \n%s", parsed_data.__dict__)

        users = await crawl_comments(bot, parsed_data.link_to_channel, parsed_data.post_id)
        rules = Rules(parsed_data.total_winners, parsed_data.phrase_to_check)
        response = await rules.calc_result(users)
        str_response = response.generate_response()

        logger.info("Response: %s", str_response)

        await event.reply("\n" + str_response, parse_mode='html')


    await bot.start()
    try:
        await bot.run_until_disconnected()
    except Exception as e:
        logger.exception("Got an exception: ", e)
    finally:
        await bot.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
