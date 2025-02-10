#!/usr/bin/env python

import logging
import os

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.constants import ParseMode

from credentials.credentials import TOKEN, ADMINS_ID
from constants.constants import START_TEXT, WAITING_FOR_MESSAGE, WAITING_FOR_QUESTION
import keyboards.keyboards

# ----------------------------
# Enable logging
# ----------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# ----------------------------
# Commands settings
# ----------------------------
#
async def post_init(application: Application) -> None:
    await application.bot.set_my_commands(
        [
            ("start", "Bot restart"),
            ("help", "Help")
        ]
    )


def get_img_path(file_name: str):
    dir_path = os.path.join(os.path.abspath(os.getcwd()), "img")
    pic_path = os.path.join(dir_path, file_name)
    return pic_path


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    effective_user = update.effective_user
    effective_chat = update.effective_chat
    args = context.args
    logger.info(f"New user! Id: {effective_user.id} | username: {effective_user.username} | first name: {effective_user.first_name} | last_name: {effective_user.last_name} | language: {effective_user.language_code} | is bot? {effective_user.is_bot}")
    logger.info(f"{effective_chat=}")
    logger.info(f"{args=}")
    if not effective_user.is_bot:
        if effective_user.id in ADMINS_ID:
            logger.info("Admin")
        else:
            logger.info("not Admin")
    keyboard = keyboards.start_keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(get_img_path("about.jpg"), "rb"),
        caption=f"{START_TEXT}",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt same text & keyboard as `start` does but not as new message"""
    keyboard = keyboards.start_keyboard
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=open(get_img_path("about.jpg"), "rb"),
        caption=f"{START_TEXT}",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  """Send a message when the command /help is issued."""
  await update.message.reply_text("Help!")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles button presses."""
    query = update.callback_query
    await query.answer()
    if query.data == "start_over":
        await start_over(update, context)


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles text messages, based on the current user state."""
    state = context.user_data.get("state")
    if state == "waitng_for_message":
        keyboard = keyboards.start_keyboard
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{WAITING_FOR_MESSAGE}",
            reply_markup=reply_markup,
        )
        del context.user_data["state"]
    elif state == "waiting_for_question":
        keyboard = keyboards.start_keyboard
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{WAITING_FOR_QUESTION}",
            reply_markup=reply_markup,
        )
        del context.user_data["state"]


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    # buttons
    application.add_handler(CallbackQueryHandler(button))

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)