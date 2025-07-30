from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from xync_schema import models
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

pay = Router()


class Cred(StatesGroup):
    detail = State()
    extra = State()


class Addr(StatesGroup):
    name = State()


@pay.message(Command("pay"))
async def main(msg: Message):
    start = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="крипта"), KeyboardButton(text="валюта (фиат)")]], resize_keyboard=True
    )
    await msg.answer("что нужно?", reply_markup=start)


@pay.message(F.text == "валюта (фиат)")
async def cur(msg: types.Message):
    currencies = await models.Cur.all()
    buttons = [[InlineKeyboardButton(text=cur.ticker, callback_data=f"cur_{cur.id}")] for cur in currencies]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await msg.answer("Выберите валюту:", reply_markup=keyboard)


@pay.message(F.text == "крипта")
async def coin(msg: types.Message):
    crypt = await models.Coin.all()
    buttons = [[InlineKeyboardButton(text=coin.ticker, callback_data=f"coin_{coin.id}")] for coin in crypt]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await msg.answer("Выберите крипту:", reply_markup=keyboard)


@pay.callback_query(F.data.startswith("coin_"))
async def coinex(query: types.CallbackQuery):
    ticker = query.data.replace("coin_", "")
    ex_id = await models.Coinex.filter(coin_id=ticker).values_list("ex_id", flat=True)
    ex = await models.Ex.filter(id__in=ex_id).values_list("name", flat=True)
    if not ex:
        await query.message.answer("Такой биржи нет")
    else:
        buttons = [[InlineKeyboardButton(text=i, callback_data=f"ad_{i}")] for i in ex]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.answer("Выберите биржу", reply_markup=keyboard)


@pay.callback_query(F.data.startswith("cur_"))
async def pm(query: types.CallbackQuery, state: FSMContext):
    ticker = query.data.replace("cur_", "")
    pmcur = await models.Pmcur.filter(cur_id=ticker).values_list("pm_id", flat=True)
    pmex = await models.Pmex.filter(pm_id__in=pmcur).values_list("id", flat=True)
    pm = await models.PmexBank.filter(pmex_id__in=pmex).values_list("name", flat=True)
    if not pm:
        await query.message.answer("Такой платежки нет")
    else:
        buttons = [[InlineKeyboardButton(text=i, callback_data=f"pm_{i}")] for i in pm]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await query.message.answer("Выберите платежку", reply_markup=keyboard)


# 4) для cur
@pay.callback_query(F.data.startswith("pm_"))
async def cred(query: types.CallbackQuery, state: FSMContext):
    name = query.data.replace("pm_", "")
    await state.update_data(name=name)
    pmex_id = await models.PmexBank.filter(name=name).values_list("pmex_id", flat=True)
    pm_id = await models.Pmex.filter(id__in=pmex_id).values_list("pm_id", flat=True)
    pmcur = await models.Pmcur.get(id__in=pm_id)
    await state.update_data(pmcur_id=pmcur.id)
    await query.message.answer("Введите реквизиты")
    await state.set_state(Cred.detail)


@pay.message(Cred.detail)
async def cred_detail(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    # user_id = 193017646
    person_id = await models.User.get(username_id=user_id)
    await state.update_data(person_id=person_id.person_id)
    await state.update_data(detail=msg.text)
    await msg.answer("Введите доп информацию")
    await state.set_state(Cred.extra)


@pay.message(Cred.extra)
async def create_cred(msg: types.Message, state: FSMContext):
    await state.update_data(extra=msg.text)
    data = await state.get_data()
    await state.clear()
    # print(data)
    data_create = {
        "detail": data["detail"],
        "name": data["name"],
        "extra": data["extra"],
        "person_id": data["person_id"],
        "pmcur_id": data["pmcur_id"],
    }
    await models.Cred.create(**data_create)


# 4) для coin
@pay.callback_query(F.data.startswith("ad_"))
async def addr(query: types.CallbackQuery, state: FSMContext):
    name = query.data.replace("ad_", "")
    ex = await models.Ex.filter(name=name).values_list("id", flat=True)
    await state.update_data(ex_id=ex)
    await query.message.answer("Введите имя")
    await state.set_state(Addr.name)


@pay.message(Addr.name)
async def addr_name(msg: types.Message, state: FSMContext):
    # user_id = msg.from_user.id
    user_id = 193017646
    person_id = await models.User.get(username_id=user_id)
    await state.update_data(person_id=person_id.person_id)
    await state.update_data(name=msg.text)
    await state.get_data()
    await state.clear()
