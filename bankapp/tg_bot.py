from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from config import Token
from main import main
import json


bot = Bot(token = Token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

id_ = 0

class Reg(StatesGroup):
    pin = State()

class Auth(StatesGroup):
    auth1, auth2 = State(), State()

class AppMoney(StatesGroup):
    appm1, appm2 = State(), State()

class DelMoney(StatesGroup):
    delm1, delm2 = State(), State()

@dp.message_handler(commands = 'start')
async def start(message: types.Message):
    
    global id_
    id_ = message.from_user.id

    with open("bankbook.json", encoding="utf-8") as file:
        bankbook = json.load(file)
        bankbook = dict(bankbook)
        if str(id_) in bankbook:
            start_text = 'Здравствуйте! Это новое банковское приложение! У Вас уже есть карта, желаете авторизоваться?'
            start_buttons = ['Авторизация']
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.add(*start_buttons)
            await message.answer(start_text, reply_markup=keyboard)
        else:
            start_text = 'Здравствуйте! Это новое банковское приложение! У Вас еще нет карты? Нажмите кнопку Регистрация!'
            start_buttons = ['Регистрация']
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.add(*start_buttons)
            await message.answer(start_text, reply_markup=keyboard)
    return id_


@dp.message_handler(Text(equals='Регистрация'))
async def reg1(message: types.Message, state: FSMContext):
    card_number = main()
    await state.update_data(
        {
            'card': card_number
        }
    )
    await message.answer('Номер Вашей новой карты: ' + card_number)
    await message.answer('Придумайте и введите новый Pin-код (4 цифры): ')
    await Reg.next()

@dp.message_handler(state=Reg.pin)
async def reg2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item = data.get('card')
    pincode = message.text
    user = {}
    user[id_] = {
        "card_number": item,
        "pincode": pincode
    }
    with open("bankbook.json", "w", encoding="utf-8") as file:
        json.dump(user, file, indent=4, ensure_ascii=False)
    
    m_count = 0
    money = {}
    money[id_] = {
        "money_count": m_count,
    }
    with open("money.json", "w", encoding="utf-8") as file:
        json.dump(money, file, indent=4, ensure_ascii=False)

    start_buttons = ['Авторизация']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer('Ваш аккаунт был создан! Вы можете авторизоваться!', reply_markup=keyboard)
    await state.finish()

@dp.message_handler(Text(equals='Авторизация'), state=None)
async def auth1(message: types.Message, state: FSMContext):
    await message.answer('Вы были найдены в системе. Введите Pin-код: ')
    await Auth.next()

@dp.message_handler(state=Auth.auth1)
async def auth2(message: types.Message, state: FSMContext):
    pin_Auth = message.text
    await state.update_data(
        {
            'pin_Auth': pin_Auth
        }
    )
    await message.answer('Введите Pin-код еще раз: ')
    await Auth.next()

@dp.message_handler(state=Auth.auth2)
async def auth3(message: types.Message, state: FSMContext):
    with open("bankbook.json", encoding="utf-8") as file:
        log = json.load(file)
    data = await state.get_data()
    item = int(data.get('pin_Auth'))
    log = dict(log)

    for i in log.values():
        i = dict(i)
        j = int(i.get("pincode"))
        if item != j:
            await message.answer('Вы ввели неверный Pin-код. Повторите попытку')
            await state.finish()
        else: 
            await message.answer('Вы успешно авторизовались!')
            start_buttons = ['Посмотреть баланс', 'Пополнить баланс', 'Снять деньги', 'Выход']
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.add(*start_buttons)
            await message.answer('Выберите функцию', reply_markup=keyboard)
            await state.finish()

@dp.message_handler(Text(equals='Посмотреть баланс'))
async def chk(message: types.Message):
    with open("money.json", encoding="utf-8") as file:
        log = json.load(file)
    log = dict(log)

    for i in log.values():
        i = dict(i)
        j = i.get("money_count")
    await message.answer("Ваш баланс: " + str(j))
    
    start_buttons = ['Пополнить баланс', 'Снять деньги', 'Выход']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer('Выберите функцию', reply_markup=keyboard)

@dp.message_handler(Text(equals='Пополнить баланс'), state=None)
async def append1(message: types.Message):
    await message.answer('Введите сумму, которую хотите положить на счет')
    await AppMoney.next()

@dp.message_handler(state=AppMoney.appm1)
async def append2(message: types.Message, state: FSMContext):
    m_app = message.text
    await state.update_data(
        {
            'money': m_app
        }
    )
    await message.answer('Введите Pin-код повторно: ')
    await AppMoney.next()

@dp.message_handler(state=AppMoney.appm2)
async def append3(message: types.Message, state: FSMContext):
    with open("money.json", encoding="utf-8") as file:
        log = json.load(file)
    data = await state.get_data()
    item = int(data.get('money'))
    log = dict(log)

    for i in log.values():
        i = dict(i)
        j = int(i.get("money_count"))
        j += item
        log[f"{id_}"]["money_count"] = j
        with open('money.json', "w",encoding="utf-8") as file:
            json.dump(log, file, indent=4, ensure_ascii=False)

    await message.answer('Вы успешно пополнили баланс!')
    start_buttons = ['Посмотреть баланс', 'Снять деньги', 'Выход']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer('Выберите функцию', reply_markup=keyboard)
    await state.finish()

@dp.message_handler(Text(equals='Снять деньги'), state=None)
async def del1(message: types.Message):
    await message.answer('Введите сумму, которую хотите снять со своего счета')
    await DelMoney.next()

@dp.message_handler(state=DelMoney.delm1)
async def del2(message: types.Message, state: FSMContext):
    m_del = message.text
    await state.update_data(
        {
            'd_money': m_del
        }
    )
    await message.answer('Введите Pin-код повторно: ')
    await DelMoney.next()

@dp.message_handler(state=DelMoney.delm2)
async def del3(message: types.Message, state: FSMContext):
    with open("money.json", encoding="utf-8") as file:
        log = json.load(file)
    data = await state.get_data()
    item = int(data.get('d_money'))
    log = dict(log)

    for i in log.values():
        i = dict(i)
        j = int(i.get("money_count"))
        if j < item:
            await message.answer('У Вас недостаточно средств. Введите другую сумму для снятия')
            await state.finish()
        else:
            j -= item
            log[f"{id_}"]["money_count"] = j
            with open('money.json', "w",encoding="utf-8") as file:
                json.dump(log, file, indent=4, ensure_ascii=False)
            await message.answer('Вы успешно сняли средства баланс!')
            start_buttons = ['Посмотреть баланс', 'Пополнить баланс', 'Выход']
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            keyboard.add(*start_buttons)
            await message.answer('Выберите функцию', reply_markup=keyboard)
            await state.finish()


@dp.message_handler(Text(equals='Выход'))
async def exit(message: types.Message):
    await message.answer("Вы успешно вышли!")
    start_buttons = ['Авторизация']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer('Ваш аккаунт был найден в системе! Вы можете авторизоваться!', reply_markup=keyboard)


if __name__ == '__main__':
    executor.start_polling(dp)