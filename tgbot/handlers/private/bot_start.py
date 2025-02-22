import html

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from infrastructure.database.repositories.users_repo import UsersRepository
from l10n.translator import Translator
from tgbot.keyboards.inline import SetUserLanguageFactory
from tgbot.keyboards.reply import main_menu_kb
from tgbot.services.setup_bot_commands import update_user_commands

start_router = Router()


@start_router.message(CommandStart())
async def bot_start(message: Message):
    await message.reply("Hello!")


@start_router.callback_query(SetUserLanguageFactory.filter())
@inject
async def set_user_language(
        call: CallbackQuery,
        callback_data: SetUserLanguageFactory,
        users_repo: FromDishka[UsersRepository],
        l10n: FromDishka[Translator],
):
    language_code = callback_data.language_code

    # user = await users_repo.get_user(telegram_id=call.from_user.id)

    await users_repo.add_user(
        telegram_id=call.from_user.id,
        full_name=call.from_user.full_name,
        language_code=language_code,
        username=call.from_user.username,
    )
    l10n.change_locale(language_code)
    await call.answer()
    await call.message.delete()
    await update_user_commands(bot=call.bot, l10n=l10n)
    args = {
        "name": html.escape(call.from_user.full_name),
        "terms_of_use": f"<a href='{l10n.get_text(key='terms-of-use-link')}'>"
                        f"<b>{l10n.get_text(key='terms-of-use-name')}</b></a>"
    }
    text = l10n.get_text(key="hello", args=args)
    await call.message.answer(text, reply_markup=main_menu_kb(l10n=l10n), disable_web_page_preview=True)
    await call.message.answer(l10n.get_text(key='hello-info'))
