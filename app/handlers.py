from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command, ChatMemberUpdatedFilter
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import os
from dotenv import load_dotenv

load_dotenv()

router = Router()

import app.keyboards as kb

class NewPlayer(StatesGroup):
    name=State()
    why=State()
    sides=State()
    career=State()


class AppealsToMayor(StatesGroup):
    appeals=State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(text='Привет! Слава Лунограду!! Выбери, что тебе надо путник: ', reply_markup=kb.main)


@router.message(F.text == 'Назад в меню')
async def cmd_mainmenu(message: Message):
    await message.answer('Главное меню:', 
                         reply_markup=kb.main)


#================ПОДАЧА ЗАЯВКИ В ГОРОД================
@router.message(F.text == 'Подать заявку 📄')
async def cmd_applyToCity(message: Message, state: FSMContext):
    await state.set_state(NewPlayer.name)
    await message.answer(text='Вопрос 1: Какой у вас ник в игре?', 
                         reply_markup=kb.return_to_menu)


@router.message(NewPlayer.name)
async def process_name(message: Message, state: FSMContext):
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('Заявка отменена', reply_markup=kb.return_to_menu)
        return
    else:
        await state.update_data(name=message.text)
        await state.set_state(NewPlayer.why)
        await message.answer("Вопрос 2: Почему именно вы?", reply_markup=kb.return_to_menu)


@router.message(NewPlayer.why)
async def process_why(message: Message, state: FSMContext):
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('Заявка отменена', reply_markup=kb.return_to_menu)
        return
    else:
        await state.update_data(why=message.text)
        await state.set_state(NewPlayer.sides)
        await message.answer("Вопрос 3: Ваши сильные стороны (строительство, механизмы и тд)", reply_markup=kb.return_to_menu)


@router.message(NewPlayer.sides)
async def process_sides(message: Message, state: FSMContext):
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('Заявка отменена', reply_markup=kb.return_to_menu)
        return
    else:
        await state.update_data(sides=message.text)
        await state.set_state(NewPlayer.career)
        await message.answer("Вопрос 4: Как представляешь свою карьеру у нас в городе?", reply_markup=kb.return_to_menu)


@router.message(NewPlayer.career)
async def process_career(message: Message, state: FSMContext, bot: Bot):
    if message.text == 'Назад в меню':
        await state.clear()
        await message.answer('Заявка отменена', reply_markup=kb.return_to_menu)
        return
    else:
        await state.update_data(career=message.text)
        data = await state.get_data()

        admin_text = (
            f"Новая заявка в город!\n\n"
            f"👤 Ник: {data['name']}\n"
            f"❓ Почему он: {data['why']}\n"
            f"💪 Сильные стороны: {data['sides']}\n"
            f"🚀 Карьера: {data['career']}\n"
            f"--- \n"
            f"Отправил: @{message.from_user.username} (ID: {message.from_user.id})"
        )
        try:
            for admin_id in os.environ.get("ADMIN_IDS"):
                await bot.send_message(chat_id=admin_id, text=admin_text)
            await message.answer("Спасибо за заявку! В ближайшее время вам ответят в лс! ❤", reply_markup=kb.return_to_menu)
        except Exception as e:
            for admin_id in os.environ.get("ADMIN_IDS"):
                await bot.send_message(chat_id=admin_id, text=f"Отпиши Феде, произошла какая-то ошибка при ЗАПОЛНЕНИИ АНКЕТЫ у игрока @{message.from_user.username} (ID: {message.from_user.id})")
            await message.answer("Произошла какая-то ошибка, попробуйте заполнить анкету еще раз или ждите пока ошибкку исправят ❤🙏", reply_markup=kb.return_to_menu)
            print(f'Ошибка:{e}')

        await state.clear()



@router.message(F.text == 'Получить форму 👨‍✈️')
async def cmd_getSuit(message: Message):
    await message.answer(text='Форма Коля Жепа 2', 
                         reply_markup=kb.return_to_menu)


#================ОБРАЩЕНИЕ К МЭРУ================
@router.message(AppealsToMayor.appeals | F.text == 'Обратиться к Мэру Города 💬')
async def cmd_appealtoMayor(message: Message, state: FSMContext):
    await state.set_state(AppealsToMayor.appeals)
    await state.update_data(user_messages=[])

    await message.answer(text='Привет! Вас приветствует бот секретарь Мэра Лунограда (Он оч занятой человек) \nНапишите ваше обращение к Мэру Лунограда. Мэр постарается вам ответить как можно скорее!')
    await message.answer(text='Что случилось?', reply_markup=kb.return_to_menu)



@router.message(AppealsToMayor.appeals | F.text != 'Подтвердить')
async def process_newmessageToMayor(message: Message, state: FSMContext):
    messages_list = await state.get_data()
    current_list = messages_list.get("user_messages", [])
    if message.text != 'Назад в меню':
        current_list.append(message.text)

        await state.update_data(user_messages=current_list)
        await message.answer(text=f'Ты можешь написать ещё текста или нажми на кнопку "Подтвердить" для завершения ввода \nВсего написано сообщений:{len(current_list)}', reply_markup=kb.accept_or_return_to_menu)
    else:
        await state.clear()
        await message.answer('Обращение отменено', reply_markup=kb.return_to_menu)
        return

@router.message(AppealsToMayor.appeals | F.text == 'Подтвердить')
async def endproccesing__messagesToMayor(message: Message, state: FSMContext, bot: Bot):
    messages_list = await state.get_data()
    current_list = messages_list.get("user_messages", [])
    if message.text != 'Назад в меню':
        await state.update_data(user_messages=current_list)
        data = state.get_data()
        admin_text = (
            f"Новое обращение к Мэру!\n\n"
            f"❓ Обращение: {data['appeals']}\n"
            f"--- \n"
            f"Отправил: @{message.from_user.username} (ID: {message.from_user.id})"
        )

        try:
            for admin_id in os.environ.get("ADMIN_IDS"):
                await bot.send_message(chat_id=admin_id, text=admin_text)
            await message.answer("Спасибо за обращение! Мэр ответит вам в короткие сроки! ❤️", reply_markup=kb.return_to_menu)
        except Exception as e:
            for admin_id in os.environ.get("ADMIN_IDS"):
                await bot.send_message(chat_id=admin_id, text=f"Отпиши Феде, произошла какая-то ошибка при ЗАПИСИ ОБРАЩЕНИЯ К МЭРУ у игрока @{message.from_user.username} (ID: {message.from_user.id})")
            await message.answer("Произошла какая-то ошибка, попробуйте заполнить анкету еще раз или ждите пока ошибкку исправят ❤🙏", reply_markup=kb.return_to_menu)
            print(f'Ошибка:{e}')
        
        await state.clear()
    else:
        await state.clear()
        await message.answer('Обращение отменено', reply_markup=kb.return_to_menu)
        return