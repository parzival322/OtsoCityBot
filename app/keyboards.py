from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
import app.suits_manager as sm
 
class Suit(CallbackData, prefix="suit"):
    user_id: int = 0
    name: str
    action: str



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
    [InlineKeyboardButton(text='Отклонить действие', callback_data='cancel_fsm')]
])


accept_or_decline_sending_appealToMayor = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Подтвердить', callback_data='accept_sending_appealToMayor')
    ],
    [
        InlineKeyboardButton(text='Отклонить заполнение', callback_data='cancel_fsm')
    ],
])


def suits_list_builder():
    builder = InlineKeyboardBuilder()
    suits = sm.get_all_suits()
    for name in suits:
        builder.add(InlineKeyboardButton(text=name,
                                               callback_data=Suit(action='select',
                                                                  name=name,
                                                                  user_username='',
                                                                  user_id=0).pack()
                                               ))

    builder.add(InlineKeyboardButton(text='Назад в меню', callback_data='main'))

    builder.adjust(1)

    return builder.as_markup()

suits_list = suits_list_builder()
