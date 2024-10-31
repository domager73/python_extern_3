import asyncio
import logging

from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile, ReplyKeyboardRemove

from app.models.weather import WeatherData
from app.service.remote.api.accu_weather_api import WeatherAPI
from tg_bot.models.trase_dto import KeysLocalStorage
from tg_bot.utils.consts import Consts
from tg_bot.utils.functions import UtilFunctions
from weather_model.weather_model import WeatherEvaluator

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token="7685419351:AAH42_EDpwx0eA4Ts6KvEIBERrehiU5u59U")
# Диспетчер
dp = Dispatcher()
form_router = Router()


class Form(StatesGroup):
    city_start = State()
    city_end = State()
    forecast_days = State()
    weather_variables = State()

    coordinates_start = State()
    coordinates_end = State()
    forecast_cor_days = State()
    weather_cor_variables = State()


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для прогноза погоды. Используй команду /help для знакомства с ботом")


@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    await message.reply(
        "Добро пожаловать в WeatherBot!\n\n"
        "Вот, что вы можете сделать:\n"
        "- Используйте команду /weather_for_trip для получения прогноза погоды по маршруту (введите начальную и конечную точки).\n"
        "- Команда /weather_evalation_by_coordinates запросит вашу текущую геолокацию и рассчитает погоду на основе координат.\n"
        "- Посетите веб-приложение для визуализации и более детального анализа погоды. http://127.0.0.1:5001"
    )

# Ввод по городу ------------------------------------------------------
@dp.message(Command('weather_for_trip'))
async def cmd_weather(message: types.Message, state: FSMContext):
    await message.answer("Введите начальную точку маршрута (название места):")
    await state.set_state(Form.city_start)


@form_router.message(Form.city_start)
async def process_city_start(message: types.Message, state: FSMContext):
    await state.update_data(departure_city=message.text)

    await message.answer("Введите конечную точку маршрута (название места):")
    await state.set_state(Form.city_end)


@form_router.message(Form.city_end)
async def process_weather_variables(message: types.Message, state: FSMContext):
    data = await state.update_data(destination_city=message.text)
    if message.text == data['departure_city']:
        await message.answer("Города совпадают наверное вы ошиблись")

        await state.set_state(Form.city_end)
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Температура (°C)"),
                KeyboardButton(text="Влажность (%)"),
            ],
            [
                KeyboardButton(text="Дождь (мм)"),
                KeyboardButton(text="Облачность (%)"),
            ],
            [
                KeyboardButton(text="Атмосферное давление (гПа)"),
                KeyboardButton(text="Скорость ветра (м/с)"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer("Выберете критерий по которому строить график",
                         reply_markup=keyboard)
    await state.set_state(Form.weather_variables)


@form_router.message(Form.weather_variables)
async def process_weather_variables(message: types.Message, state: FSMContext):
    selected_param = message.text

    if selected_param not in Consts.weather_variables.values():
        await message.reply("Пожалуйста, выберите корректный параметр.")
        return

    await state.update_data(weather_variables=UtilFunctions.label_to_key(selected_param))

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Прогноз на 3 дня"),
                KeyboardButton(text="Прогноз на 7 дней"),
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer("Выберите временной интервал прогноза:",
                         reply_markup=keyboard)
    await state.set_state(Form.forecast_days)


@form_router.message(Form.forecast_days)
async def process_forecast_days(message: types.Message, state: FSMContext):
    if message.text == "Прогноз на 3 дня":
        days = 3
    elif message.text == "Прогноз на 7 дней":
        days = 7
    else:
        await message.reply("Пожалуйста, выберите корректный временной интервал.")
        return

    await state.update_data(forecast_days=days)

    data = await state.get_data()

    departure_city = data[KeysLocalStorage.departure_city]
    destination_city = data[KeysLocalStorage.destination_city]
    forecast_days = data[KeysLocalStorage.forecast_days]
    hourly = data[KeysLocalStorage.weather_variables]

    try:
        start_coords = WeatherAPI.get_coordinates_by_city(departure_city)
        end_coords = WeatherAPI.get_coordinates_by_city(destination_city)

        if not start_coords or not end_coords:
            await message.answer("Один из городов не найден. Пожалуйста, проверьте названия.")
            return

        start_weather = WeatherAPI.get_weather_variables_by_time(start_coords.lat, start_coords.lon,
                                                                 hourly, forecast_days)
        end_weather = WeatherAPI.get_weather_variables_by_time(end_coords.lat, end_coords.lon, hourly,
                                                               forecast_days)

        # Генерация графика
        UtilFunctions.create_plot(departure_city, destination_city, start_weather, end_weather,
                                  UtilFunctions.key_to_label(hourly))

        # Отправляем график в Telegram
        await message.answer_photo(FSInputFile('weather_plot.png'), keyboard=ReplyKeyboardRemove())

    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}", keyboard=ReplyKeyboardRemove())

    await state.set_state()


# Конец ввода по городу ------------------------------------------------------

@dp.message(Command('weather_evalation_by_coordinates'))
async def cmd_weather_by_coordinates(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить текущую геолокацию", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer("Пожалуйста, отправьте начальную точку маршрута (вашу геолокацию).", reply_markup=keyboard)
    await state.set_state(Form.coordinates_start)


@form_router.message(Form.coordinates_start)
async def process_start_location(message: types.Message, state: FSMContext):
    if message.location:
        await state.update_data(departure_coords=(message.location.latitude, message.location.longitude))

        await message.answer("Теперь отправьте конечную точку маршрута. в виде (число:число)")
        await state.set_state(Form.coordinates_end)
    else:
        await message.reply("Пожалуйста, отправьте геолокацию с помощью кнопки.")


@form_router.message(Form.coordinates_end)
async def process_forecast_days_coordinates(message: types.Message, state: FSMContext):
    if UtilFunctions.is_number_colon_number(message.text):
        data = await state.update_data(destination_coords=(tuple(map(float, message.text.split(':')))))

        if data["departure_coords"] == data["destination_coords"]:
            await message.answer("Координаты совпадают. Проверьте ввод.")
            await state.set_state(Form.coordinates_end)
            return

    data = await state.get_data()

    departure_coords = data['departure_coords']
    destination_coords = data['destination_coords']

    try:
        start_weather = WeatherAPI.get_weather_by_coordinates(departure_coords[0], departure_coords[1])
        end_weather = WeatherAPI.get_weather_by_coordinates(destination_coords[0], destination_coords[1])

        evalation_start_weather = WeatherEvaluator().evaluate(start_weather)
        evalation_end_weather = WeatherEvaluator().evaluate(end_weather)

        await message.answer(
            f"Город отправления: {evalation_start_weather}\n"
            "   \n"
            f"Город прибытия: {evalation_end_weather}"
            , reply_markup=ReplyKeyboardRemove())

    except Exception as e:
        await message.reply(f"Произошла ошибка: {str(e)}", reply_markup=ReplyKeyboardRemove())

    await state.clear()


# Регистрация маршрутизатора
dp.include_router(form_router)


async def main():
    await dp.start_polling(bot)


asyncio.run(main())
