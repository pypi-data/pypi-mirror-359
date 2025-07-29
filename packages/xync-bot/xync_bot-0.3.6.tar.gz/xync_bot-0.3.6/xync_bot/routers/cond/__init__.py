import re
from asyncio import iscoroutinefunction
from enum import IntEnum
from inspect import isclass
from typing import Coroutine

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, ReplyKeyboardRemove
from cyrtranslit import to_latin
from xync_schema import models
from xync_schema.enums import SynonymType, Party, Slip, AbuserType, NameType, Boundary

r = Router()

async def wrap_cond(txt: str):
    bnks = await models.Synonym.filter(typ=SynonymType.bank)
    bnks = '|'.join('\\b'+b.txt+('\\b' if b.boundary&Boundary.right else '') for b in bnks)
    for syn in await models.Synonym.all():
        lb, rb = "\\b" if syn.boundary&Boundary.left else "", "\\b" if syn.boundary&Boundary.right else ""
        if syn.typ == SynonymType.bank_side:
            syn.txt.replace('#banks#', f'({bnks})')
        if syn.is_re or syn.txt in txt:
            pattern = re.compile(lb+syn.txt+rb)
            if match := re.search(pattern, txt):
                g = match.group()
                val, hval = await get_val(syn.typ, syn.val)
                val = syn.typ.name + (f'="{hval}"' if hval else '')
                txt = re.sub(pattern, f"<code>{g}</code><tg-spoiler>[{val}]</tg-spoiler>", txt)
    return txt

async def cbanks(bnid: str) -> list[tuple[int, str]]:
    beginning = to_latin(bnid[:2], lang_code='ru')
    return await models.Pm.filter(norm__startswith=beginning, bank=True).values_list('id', 'norm')

async def cppo(txt: str) -> list[tuple[int, str]]:
    opts = re.findall(r'\d+', txt) or [1, 2, 3, 5, 10]
    return [(o, str(o)) for o in opts]

synopts: dict[SynonymType, list[str] | type(IntEnum) | None | Coroutine] = {
    SynonymType.name: ["not_slavic", "slavic"],
    SynonymType.ppo: cppo,
    SynonymType.from_party: Party,
    SynonymType.to_party: Party,
    SynonymType.slip_req: Slip,
    SynonymType.slip_send: Slip,
    SynonymType.abuser: AbuserType,
    SynonymType.scale: ["1", "10", "100", "1000"],
    SynonymType.slavic: NameType,
    SynonymType.mtl_like: None,
    SynonymType.bank: cbanks,
    SynonymType.bank_side: ["except", "only"],
}
rkm = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="ppo"), KeyboardButton(text="abuser")],
    [KeyboardButton(text="from_party"), KeyboardButton(text="to_party")],
    [KeyboardButton(text="slip_send"), KeyboardButton(text="slip_req")],
    [KeyboardButton(text="name"), KeyboardButton(text="slavic")],
    [KeyboardButton(text="scale"), KeyboardButton(text="mtl_like")],
    [KeyboardButton(text="bank"), KeyboardButton(text="bank_side")],
], one_time_keyboard=True)

async def get_val(typ: SynonymType.__class__, val: str) -> tuple[SynonymType | int | bool, str]:
    if isinstance(val, str) and val.isnumeric():
        val = int(val)
    if isclass(lst := synopts[typ]) and issubclass(lst, IntEnum):
        return (v:=lst(val)), v.name
    elif isinstance(lst, list):
        return val, lst[val]
    elif typ == SynonymType.bank:
        return val, (await models.Pm[val]).norm
    return val, val

async def btns(typ: SynonymType.__class__, txt: str = None) -> InlineKeyboardMarkup | None:
    if lst := synopts[typ]:
        if isinstance(lst, list):
            kb = [[InlineKeyboardButton(text=n, callback_data=f'st:{typ.name}:{i}')] for i, n in enumerate(lst)]
        elif isclass(lst) and issubclass(lst, IntEnum):
            kb = [[InlineKeyboardButton(text=i.name, callback_data=f'st:{typ.name}:{i.value}')] for i in lst]
        else:
            kb = [[InlineKeyboardButton(text=n, callback_data=f'st:{typ.name}:{i}')] for i, n in await lst(txt)]
        return InlineKeyboardMarkup(inline_keyboard=kb)
    else:
        return lst

@r.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    cond = await models.Cond.filter(parsed__isnull=True).order_by("-created_at").first().prefetch_related('parsed')
    await state.set_data({"cid": cond.id, "cond_txt": cond.raw_txt})
    await msg.reply(await wrap_cond(cond.raw_txt), reply_markup=rkm)


@r.message(F.quote)
async def got_synonym(msg: Message, state: FSMContext):
    if not (msg.text in {st.name for st in SynonymType} and SynonymType[msg.text]):
        return await msg.reply_text(f'Нет раздела "{msg.text}", не пиши текст сам, выдели кусок из моего сообщения,'
                                    f'ответь на него, выбери кнопку раздела')
    if not msg.quote:
        return await msg.reply_text(f'Вы забыли выделить кусок текста для {msg.text}')
    if typ := SynonymType[msg.text]:
        await state.update_data({"syntext": msg.quote.text, "cmsg": msg.reply_to_message})
        await models.Synonym.update_or_create({"typ": typ}, txt=msg.quote.text)
        if rm := await btns(typ, msg.quote.text):
            return await msg.answer("Уточните", reply_markup=rm, reply_to_message_id=msg.message_id)
        await syn_result(msg, f'st:{typ.name}:1', state)
    return None

@r.callback_query()
async def got_synonym_val(cbq: CallbackQuery, state: FSMContext):
    await syn_result(cbq.message, cbq.data, state)

async def syn_result(msg: Message, data: str, state: FSMContext):
    t, st, sv = data.split(':')
    if t == "st":
        typ = SynonymType[st]
        val, hval = await get_val(typ, sv)
        syntext = await state.get_value('syntext')
        cid = await state.get_value('cid')
        syn, _ = await models.Synonym.update_or_create({"val": val}, typ=typ, txt=syntext)
        await models.CondParsed.update_or_create({typ.name: val}, cond_id=cid)
        await msg.reply(
            f'Текст "{syntext}" определен как синоним для `{typ.name}` со значением {hval}',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text='Готово! Давай новый', callback_data=f'cond:complete:{cid}'),
                InlineKeyboardButton(text='Продолжить с этим текстом', callback_data=f'cond:process:{cid}')
            ]])
        )
        # await msg.reply_to_message.delete()
        # await msg.delete()
        # await cmsg.edit_text(wrapped_txt)

    elif t == "cond":
        if st == 'complete':
            await models.CondParsed.update_or_create({"parsed": True}, cond_id=int(sv))
            await start(msg, state)
        else:
            wrapped_txt = await wrap_cond(await state.get_value('cond_txt'))
            # cmsg: Message = await state.get_value('cmsg')
            await msg.reply(wrapped_txt, reply_markup=rkm)
    else:
        await msg.reply("Где я?")

@r.message(F.reply_to_message)
async def clear(msg: Message):
    await msg.reply_to_message.delete_reply_markup()
    await msg.delete()

@r.message()
async def unknown(msg: Message):
    # user = await User.get(username_id=msg.from_user.id)
    await msg.delete()
