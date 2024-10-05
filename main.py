from os import getenv
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv
# тут я тоже улучшаю код для pylint-а, так что задушу docstring-ами
# Your code has been rated at 8.62/10 (previous run: 8.62/10, +0.00)


load_dotenv()
BOT_TOKEN = getenv('TOKEN')
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
START_BUTTONS = ['to inches', 'to yards', 'to miles']
keyboard = ReplyKeyboardBuilder()
keyboard.add(*[KeyboardButton(text=i) for i in START_BUTTONS])


number = None
response = None
is_response_needed = False


"""
От себя добавлю что стейты или как их там умные назвали Конечные автоматы (FSM) это полный ужас 
я почти 3 часа просидел чтобы понять как я могу с аиограмом сделать так,
чтобы функция ждала сообщения, проверила то что оно инт, и потом уже начиналась другая функция,
 а как оказалось можно просто сделай 2 стейта,
и сделать функцию которая исполняется в состоянии ожидания числа,
 и ещё одна в состоянии обработки ответа.
Половина документаций на старой версии, в конце концов спасибо 2-м документациям 
[
'https://mastergroosha.github.io/aiogram-3-guide/fsm/#define-states',
 'https://docs.aiogram.dev/en/latest/dispatcher/finite_state_machine/index.html',
 ]
в общем всё, на момент написания этого текста я во-первых хочу спать,
во-вторых мне ещё доделывать код, по этому я пошёл
"""

# Здесь могла быть ваша реклама
# © 2024 https://github.com/3306512 (Program author) - All Rights Reserved.


class Form(StatesGroup):
    """
    Наследуется от StatesGroup - класс Form это класс для состояний
    """
    num = State()
    process = State()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext) -> None:
    """
        Функция запускается после команды /start в боте, так-сказать приветствие
    :param message: сообщения пользователя - /start
    :param state: состояние, в конце переключает его на Form.num
    :return: None
    """
    await state.set_state(Form.num)
    await message.answer('Hi... enter feets', reply_markup=ReplyKeyboardRemove())


@dp.message(Form.num)
async def number_input(message: Message, state: FSMContext) -> None:
    """
        После приветствия (start()) ожидает сообщения пользователя,
        работает в состояние Form.num
    :param message: число от пользователя, если не число, то обрабатывается как не правильное
    :param state: состояние, в конце переключает его на Form.process
    :return: None
    """
    if message.text.isdigit():
        await message.reply('now choose', reply_markup=keyboard.as_markup())
        global number
        number = message.text
        await state.set_state(Form.process)
    else:
        await message.reply('use nums')


# мне самому не нравится этот огромный блок if-а внизу
@dp.message(Form.process)
async def process_answer(message: Message, state: FSMContext) -> None:
    """
        Обработка ответа, высчитывание нужного значения ответа для пользователя (или просто функция для ответа)
        эта функция работает в состоянии Form.process
    :param message: сообщение пользователя, либо сообщение из START_BUTTONS, либо обрабатывается как не правильное
    :param state: состояние, в конце переключает его на Form.num
    :return: None
    """
    global number, response, is_response_needed
    if message.text == 'to inches':
        values = await calculate(number)
        response = values.get('inches')
        is_response_needed = True
    elif message.text == 'to yards':
        values = await calculate(number)
        response = values.get('yards')
        is_response_needed = True
    elif message.text == 'to miles':
        values = await calculate(number)
        response = values.get('miles')
        is_response_needed = True
    else:
        await message.answer('unknown option', reply_markup=keyboard.as_markup())
        is_response_needed = False
        await state.clear()
        await state.set_state(Form.process)
    if is_response_needed:
        await message.answer(str(response))
        await message.answer('enter another number', reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.num)


async def calculate(num: int) -> dict:
    """
    Функция для высчитывания нужного числа
    :param num: число, введенное пользователем в функции number_input()
    :return:
        dict: to_return - dict со значениями в дюймах, ярдах и милях
    """
    to_return = {
        'inches': int(num) * 12,
        'yards': round(int(num)*0.333333333, 2),
        'miles': round(int(num)*0.000189393939, 5),
    }
    return to_return


async def main() -> None:
    """
        Главная функция, вызывается в точке входа
    :return: None
    """
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    print('starting bot')
    asyncio.run(main())
