#!/usr/bin/python3
# -*- coding: utf-8 -*-
import logging
import subprocess
from telegram import ParseMode
from telegram.ext import Dispatcher, CallbackQueryHandler, CommandHandler

from utils.helper import alert_users
from utils.restricted import restricted

logger = logging.getLogger(__name__)


def init(dispatcher: Dispatcher):
    """Provide handlers initialization."""
    dispatcher.add_handler(CallbackQueryHandler(cancel, pattern=r'^cancel$'))
    dispatcher.add_handler(CommandHandler(['shell', 'sh', 'tr', 'term', 'terminal'], shell))


@restricted
def cancel(update, context):
    query = update.callback_query
    if query.message.chat_id < 0 and \
            (not query.message.reply_to_message or
             query.from_user.id != query.message.reply_to_message.from_user.id):
        alert_users(context, update.effective_user, 'invalid caller', query.data)
        query.answer(text='Yo-he!', show_alert=True)
        return
    # query.message.edit_reply_markup(reply_markup=None)
    query.message.delete()


@restricted
def shell(update, context):
    message = update.effective_message
    cmd = message.text.split(' ', 1)
    if len(cmd) == 1:
        message.reply_text('No command to execute was given.')
        return
    cmd = cmd[1]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    reply = ''
    stderr = stderr.decode()
    stdout = stdout.decode()
    if stdout:
        reply += f"*Stdout*\n`{stdout}`\n"
        logger.info(f"Shell - {cmd} - {stdout}")
    if stderr:
        reply += f"*Stderr*\n`{stderr}`\n"
        logger.error(f"Shell - {cmd} - {stderr}")
    if len(reply) > 3000:
        with open('shell_output.txt', 'w') as file:
            file.write(reply)
        with open('shell_output.txt', 'rb') as doc:
            context.bot.send_document(
                document=doc,
                filename=doc.name,
                reply_to_message_id=message.message_id,
                chat_id=message.chat_id)
    else:
        message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
