from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
#from aiogram.filters.callback_data import CallbackData
import asyncio
 

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Подать заявку 📄')
        ],
        [
            KeyboardButton(text='Получить форму 👨‍✈️')
        ],
        [
            KeyboardButton(text='Обратиться к Мэру Города 💬')
        ]],
        resize_keyboard=True
)


return_to_menu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='Назад в меню')
    ],
], resize_keyboard=True)


decline_operation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отклонить заполнение', callback_data='cancel_fsm')]
])


accept_or_decline_sending_appealToMayor = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Подтвердить', callback_data='accept_sending_appealToMayor')
    ],
    [
        InlineKeyboardButton(text='Отклонить заполнение', callback_data='cancel_fsm')
    ],
])