from aiogram import F, Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import os

from dotenv import load_dotenv

load_dotenv()

router = Router()

import app.keyboards as kb
import app.suits_manager as sm

class NewPlayer(StatesGroup):
    name=State()
    why=State()
    sides=State()
    career=State()


class AppealsToMayor(StatesGroup):
    appeals=State()


class Skin(StatesGroup):
    suit_name=State()
    save_path=State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(text='Привет! Слава OtsoCity!! Выбери, что тебе надо путник: ', reply_markup=kb.main)


@router.message(F.text == 'Назад в меню')
async def cmd_mainmenu(message: Message):
    await message.answer('Главное меню:', 
                         reply_markup=kb.main)

@router.callback_query(F.data == 'main')
async def cmd_mainmenu_callback(callback: CallbackQuery):
    await callback.message.answer('Главное меню:',
                         reply_markup=kb.main)
    await callback.answer()

@router.callback_query(F.data == 'cancel_fsm')
async def cmd_cancel_fsm(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await callback.message.edit_text("❌ Действие отменено")
        await callback.message.answer("Главное меню:", reply_markup=kb.main)
    else:
        await callback.answer("Нет активных действий")
    await callback.answer()

#================ПОДАЧА ЗАЯВКИ В ГОРОД================
@router.message(F.text == 'Подать заявку 📄')
async def cmd_applyToCity(message: Message, state: FSMContext):
    await state.set_state(NewPlayer.name)
    await message.answer(text='Вопрос 1: Какой у вас ник в игре?', 
                         reply_markup=kb.decline_operation)


@router.message(NewPlayer.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(NewPlayer.why)
    await message.answer("Вопрос 2: Почему именно вы?", reply_markup=kb.decline_operation)


@router.message(NewPlayer.why)
async def process_why(message: Message, state: FSMContext):
    await state.update_data(why=message.text)
    await state.set_state(NewPlayer.sides)
    await message.answer("Вопрос 3: Ваши сильные стороны (строительство, механизмы и тд)", reply_markup=kb.decline_operation)


@router.message(NewPlayer.sides)
async def process_sides(message: Message, state: FSMContext):
    await state.update_data(sides=message.text)
    await state.set_state(NewPlayer.career)
    await message.answer("Вопрос 4: Как представляешь свою карьеру у нас в городе?", reply_markup=kb.decline_operation)


@router.message(NewPlayer.career)
async def process_career(message: Message, state: FSMContext, bot: Bot):
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
        admin_ids_str = os.environ.get("ADMIN_IDS", "")
        admin_ids = [aid.strip() for aid in admin_ids_str.split(",") if aid.strip()]
        for admin_id in admin_ids:
            await bot.send_message(chat_id=admin_id, text=admin_text)
        await message.answer("Спасибо за заявку! В ближайшее время вам ответят в лс! ❤", reply_markup=kb.return_to_menu)
    except Exception as e:
        admin_ids_str = os.environ.get("ADMIN_IDS", "")
        admin_ids = [aid.strip() for aid in admin_ids_str.split(",") if aid.strip()]
        for admin_id in admin_ids:
            await bot.send_message(chat_id=admin_id, text=f"❗❗❗Произошла какая-то ошибка при ЗАПОЛНЕНИИ АНКЕТЫ у игрока @{message.from_user.username} (ID: {message.from_user.id})❗❗❗")
        await message.answer("Произошла какая-то ошибка, попробуйте заполнить анкету еще раз или ждите пока ошибкку исправят ❤🙏", reply_markup=kb.return_to_menu)
        print(f'Ошибка:{e}')

    await state.clear()


#================ОБРАЩЕНИЕ К МЭРУ================
@router.message(F.text == 'Обратиться к Мэру Города 💬')
async def cmd_appealtoMayor(message: Message, state: FSMContext):
    await state.set_state(AppealsToMayor.appeals)
    await state.update_data(user_messages=[])

    await message.answer(text='👋Привет! Вас приветствует бот-секретарь Мэра OtsoCity \n\nНапишите ваше обращение к Мэру OtsoCity. Мэр постарается вам ответить как можно скорее!')
    await message.answer(text='Что случилось?', reply_markup=kb.decline_operation)


@router.message(AppealsToMayor.appeals)
async def process_newmessageToMayor(message: Message, state: FSMContext):
    messages_list = await state.get_data()
    current_list = messages_list.get("user_messages", [])
    current_list.append(message.text)

    await state.update_data(user_messages=current_list)
    await message.answer(text=f'Ты можешь написать ещё текста или нажми на кнопку "Подтвердить" для завершения ввода \nВсего написано сообщений:{len(current_list)}', reply_markup=kb.accept_or_decline_sending_appealToMayor)

@router.callback_query(F.data == 'accept_sending_appealToMayor')
async def endproccesing__messagesToMayor(callback: CallbackQuery, state: FSMContext, bot: Bot):
    messages_list = await state.get_data()
    current_list = messages_list.get("user_messages", [])

    admin_text = (
        f"Новое обращение к Мэру!\n\n"
        f"❓ Обращение: {', '.join(current_list)}\n"
        f"--- \n"
        f"Отправил: @{callback.from_user.username} (ID: {callback.from_user.id})"
    )

    try:
        admin_ids_str = os.environ.get("ADMIN_IDS", "")
        admin_ids = [aid.strip() for aid in admin_ids_str.split(",") if aid.strip()]
        for admin_id in admin_ids:
            await bot.send_message(chat_id=admin_id, text=admin_text)
        await callback.message.answer("Спасибо за обращение! Мэр ответит вам в короткие сроки! ❤️", reply_markup=kb.return_to_menu)
    except Exception as e:
        admin_ids_str = os.environ.get("ADMIN_IDS", "")
        admin_ids = [aid.strip() for aid in admin_ids_str.split(",") if aid.strip()]
        for admin_id in admin_ids:
            await bot.send_message(chat_id=admin_id, text=f"произошла какая-то ошибка при ЗАПИСИ ОБРАЩЕНИЯ К МЭРУ у игрока @{callback.message.from_user.username} (ID: {callback.message.from_user.id})")
        await callback.message.answer("Произошла какая-то ошибка, попробуйте заполнить анкету еще раз или ждите пока ошибку исправят ❤🙏", reply_markup=kb.return_to_menu)
        print(f'Ошибка:{e}')
    
    await state.clear()


#================ПОЛУЧЕНИЕ ФОРМЫ================
@router.message(F.text == 'Получить форму 👨‍✈️')
async def cmd_getSuit(message: Message):
    await message.answer_photo(photo="AgACAgIAAxkBAAIE5WpZQDekjhVXAAEnJMCj8La1hA32YgACRBxrG9h7yUoJkns4dCWchwEAAwIAA3gAAz0E",
                               caption='Выберите форму из списка:',
                               reply_markup=kb.suits_list)


@router.callback_query(kb.Suit.filter(F.action=='list'))
async def cmd_getSuit_callback(callback: CallbackQuery):
    await callback.message.answer_photo(photo="AgACAgIAAxkBAAIE5WpZQDekjhVXAAEnJMCj8La1hA32YgACRBxrG9h7yUoJkns4dCWchwEAAwIAA3gAAz0E",
                                        caption='Выберите форму из списка:',
                                        reply_markup=kb.suits_list)
    await callback.answer()

@router.callback_query(kb.Suit.filter(F.action=='select'))
async def selected_Suit(callback: CallbackQuery, callback_data: kb.Suit, state: FSMContext):
    user = callback.from_user
    suit_name = callback_data.name
    await callback.answer()
    if not sm.has_access(user_id=user.id, suit_name=suit_name):

        request_access_for_suit = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Запросить доступ',
                                     callback_data=kb.Suit(action='ask-access',
                                                           name=callback_data.name,
                                                           user_id=user.id).pack())
            ],
            [
                InlineKeyboardButton(text='Назад',
                                     callback_data=kb.Suit(action='list',
                                                           name=callback_data.name,
                                                           user_id=user.id).pack())
            ]
        ])

        await callback.message.answer(text='У Вас нет доступа к этой форме. Запросите доступ у Мэра',
                                      reply_markup=request_access_for_suit)
    else:
        await state.set_state(Skin.suit_name)
        await state.update_data(suit_name=suit_name)
        await state.set_state(Skin.save_path)
        await callback.message.answer(text='Отправьте ваш скин в формате PNG и размером 64x64', reply_markup=kb.decline_operation)
        await callback.answer()


@router.callback_query(kb.Suit.filter(F.action=='ask-access'))
async def askSuit(callback: CallbackQuery, callback_data: kb.Suit, bot: Bot):

    give_access_for_suit = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Дать доступ',
                                 callback_data=kb.Suit(action='allow-access',
                                                       name=callback_data.name,
                                                       user_id=callback_data.user_id).pack())
        ],
        [
            InlineKeyboardButton(text='Отказать',
                                 callback_data=kb.Suit(action='deny-access',
                                                       name=callback_data.name,
                                                       user_id=callback_data.user_id).pack())
        ]
    ])

    admin_ids_str = os.environ.get("ADMIN_IDS", "")
    admin_ids = [aid.strip() for aid in admin_ids_str.split(",") if aid.strip()]
    for admin_id in admin_ids:
        if callback.from_user.username != None:
            await bot.send_message(chat_id=admin_id,
                                   text=f"Пользователь @{callback.from_user.username} (ID: {callback.from_user.id}) запрашивает доступ на форму {callback_data.name}. Выберите действие:",
                                   reply_markup=give_access_for_suit)
        else:
            await bot.send_message(chat_id=admin_id,
                                   text=f"<a href='tg://user?id={callback.from_user.id}'>Пользователь</a> (ID : {callback.from_user.id}) запрашивает доступ на форму {callback_data.name}. Выберите действие:",
                                   parse_mode="HTML",
                                   reply_markup=give_access_for_suit)


    await callback.answer()


@router.callback_query(kb.Suit.filter(F.action=='allow-access'))
async def Allow_access_to_Suit(callback: CallbackQuery, callback_data: kb.Suit, bot: Bot):
    status_of_allowing_access = sm.set_access(user_id=callback_data.user_id, suit_name=callback_data.name, allow=True)

    if status_of_allowing_access[0] == 'OK':
        await callback.message.edit_text(text=f"Вы успешно выдали доступ <a href='tg://user?id={callback_data.user_id}'>Пользователь</a> (ID : {callback_data.user_id}) к форме {callback_data.name}", parse_mode="HTML")

        await bot.send_message(chat_id=callback_data.user_id, text=f'3opka положительно ответил на вашу долгую мольбу о форме {callback_data.name}\n\nТеперь повторно нажмите "Получить форму 👨‍✈️"')
    elif status_of_allowing_access[0] == "ERROR":
        if status_of_allowing_access[1] == 1:
            await callback.message.edit_text(
                text=f"Произошла ошибка 1 при выдаче доступа <a href='tg://user?id={callback_data.user_id}'>Пользователь</a> (ID : {callback_data.user_id}) к форме {callback_data.name}",
                parse_mode="HTML")
        elif status_of_allowing_access[1] == 2:
            await callback.message.edit_text(
                text=f"Произошла ошибка 2 при выдаче доступа <a href='tg://user?id={callback_data.user_id}'>Пользователь</a> (ID : {callback_data.user_id}) к форме {callback_data.name}",
                parse_mode="HTML")

    await callback.answer()


@router.callback_query(kb.Suit.filter(F.action=='deny-access'))
async def Deny_access_to_suit(callback: CallbackQuery, callback_data: kb.Suit, bot: Bot):
    await callback.message.edit_text(
        text=f"Вы отказали в доступе <a href='tg://user?id={callback_data.user_id}'>Пользователь</a> (ID : {callback_data.user_id}) к форме {callback_data.name}", parse_mode="HTML")

    await bot.send_message(chat_id=callback_data.user_id,
                           text=f"3opka отрицательно ответил на вашу мольбу о форме {callback_data.name}. Вы теперь иноагент и враг OtsoCity")

    await callback.answer()


#================ОБРАБОТКА СКИНА================
@router.message(Skin.save_path)
async def process_skin(message: Message, state: FSMContext, bot: Bot):
    if message.document and message.document.file_name.lower().endswith('.png'):
        skin_file_id = message.document.file_id
        skin_file_name = message.document.file_name
        if not os.path.exists(sm.TEMP_DIR):
            os.makedirs(sm.TEMP_DIR)
        skin_path = os.path.join(sm.TEMP_DIR, skin_file_name)
        await bot.download(skin_file_id, destination=skin_path)

        await state.update_data(save_path=skin_path)
        data = await state.get_data()

        suit_name = data['suit_name']
        suit_file = suit_name + '.png'
        suit_path = sm.DATA_DIR+f'/{suit_file}'

        output_path = sm.RESULTS_DIR+f"/{skin_file_name.split('.')[0]}_{suit_name}.png"

        result = sm.blend_skin_with_suit(skin_path=skin_path, suit_path=suit_path, output_path=output_path)

        if result == 'OK':
            from aiogram.types import FSInputFile
            document_to_send = FSInputFile(output_path)

            await bot.send_document(chat_id=message.chat.id, document=document_to_send)
            await message.answer('На ваш скин была успешно надета форма, пользуйтесь с удовольствием!')

            await state.clear()

            if os.path.exists(skin_path):
                os.remove(skin_path)
        else:
            await message.answer('Произошла какая-то ошибка при обработке скина')
    else:
        await message.answer('Отправьте ваш скин в формате PNG и разрешением 64x64. Также при отправке выберите параметр БЕЗ СЖАТИЯ или ОТПРАВИТЬ КАК ДОКУМЕНТ')


@router.message(F.photo)
async def get_photo_id(message: Message):
    await message.answer(f'Photo ID: {message.photo[-1].file_id}')
