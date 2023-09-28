"""
    2 версия файла (до/после и цикл дня) основной функционал работы с ботом
"""
import asyncio
import logging
import os
import random
import time
from datetime import datetime, timedelta
import gspread
import sqlalchemy

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

import config as cfg
import keyboards as kb
import utils as fsm
from db import DataBase

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=cfg.USER_BOT_TOKEN, parse_mode='HTML')
admin_bot = Bot(token=cfg.ADMIN_BOT_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot=bot, storage=storage)
db = DataBase('bodhi.db')
# db = DataBase('../bodhi.db')

job_stores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
# scheduler = AsyncIOScheduler(job_stores=job_stores)
scheduler = AsyncIOScheduler(job_stores=job_stores, timezone='Europe/Moscow')

deleted_msgs = list()


async def delete_msgs(chat_id) -> None:
    already_deleted_msg = list()
    for msg in deleted_msgs:
        if msg['chat_id'] == chat_id:
            try:
                await bot.delete_message(chat_id=msg['chat_id'], message_id=msg['message_id'])
                already_deleted_msg.append(msg)
            except Exception as ex:
                print(ex)
    for msg in already_deleted_msg:
        deleted_msgs.remove(msg)
    already_deleted_msg.clear()


def run_date_func(date, timezone):
    if timezone <= 0:
        run_date = date + timedelta(hours=abs(timezone))
    else:
        run_date = date - timedelta(hours=abs(timezone))
    return run_date


# Проверка функционала
@dp.message_handler(commands=['check'], state='*')
async def cmd_check(msg: types.Message, state: FSMContext) -> None:
    pass
    # await evening_practic(msg.from_user.id)
    # await start_day(msg.from_user.id, 'hour', msg)
    # await msg.answer(db.get_msg('start_week_questions'), reply_markup=kb.one_btn('Ответить', 'start_week_questions'))
    # await msg.answer(db.get_msg('before_photo_start'), reply_markup=kb.one_btn('ГО', 'before_photo_start'))


# @dp.message_handler(state=fsm.Check.first)
# async def text_check(msg: types.Message, state: FSMContext) -> None:
#     await send_comment_partner(msg, state)
#     await state.finish()


@dp.message_handler(commands=['stop'])
async def stop_state(msg: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await msg.answer(db.get_msg('menu_msg'), reply_markup=kb.main_menu())


MENU = ['Расписание', 'Записи практик', 'Фокус недели', 'FAQ', 'Красная кнопка 🚨', 'Сменить часовой пояс', 'Медитации', 'Отправить фото']


async def support_answer(user_id) -> None:
    await bot.send_message(chat_id=user_id, text=db.get_msg('support_answer'), reply_markup=kb.support_answer())


@dp.message_handler(Text(equals=MENU), state='*')
async def menu(msg: types.Message, state: FSMContext) -> None:
    item_menu = msg.text
    if item_menu == 'Расписание':
        user = db.get_user(msg.from_user.id)
        await msg.answer('Перейди по ссылке, чтобы увидеть расписание', reply_markup=kb.schedule_training(user[9]))
    elif item_menu == 'Записи практик':
        records = db.get_training_records()
        text = '<b>Записи практик:</b>\n\n'
        for record in records:
            text = text + f'<a href="{record[1]}">Практика от {record[2]}</a>\n'
        await msg.answer(text, disable_web_page_preview=True)
    elif item_menu == 'Фокус недели':
        await msg.answer(db.get_msg('week_focus'))
    elif item_menu == 'FAQ':
        await msg.answer('Ответы на часто задаваемые вопросы ты можешь найти по ссылке ниже 👇🏻', reply_markup=kb.faq())
    elif item_menu == 'Красная кнопка 🚨':
        await bot.send_message(chat_id=msg.from_user.id, text=db.get_msg('to_support'))
        await fsm.ToSupport.msg.set()
        run_date = datetime.now() + timedelta(hours=1)
        job_id = 'tosupport_' + str(msg.from_user.id)
        scheduler.add_job(support_answer, 'date', run_date=run_date, id=job_id, kwargs={'user_id': msg.from_user.id})
    elif item_menu == 'Сменить часовой пояс':
        await fsm.Timezone.change.set()
        await bot.send_message(chat_id=msg.from_user.id, text=db.get_msg('timezone'))
    elif item_menu == 'Отправить фото':
        await start_before(msg.from_user.id)
    elif item_menu == 'Медитации':
        await bot.send_message(chat_id=msg.from_user.id, text=db.get_msg('meditation'))
    else:
        print('ERROR Menu')
    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)


@dp.message_handler(commands=['start'], state='*')
async def cmd_start(msg: types.Message, state: FSMContext) -> None:
    ref = msg.text[7:]
    if not db.user_exists_username(msg.from_user.username):
        if ref != '':
            last_msg = await msg.answer('YO!', reply_markup=kb.main_menu())
            await bot.delete_message(chat_id=last_msg.chat.id, message_id=last_msg.message_id)
            db.add_user(msg.from_user.id, msg.from_user.username, msg.from_user.first_name, msg.from_user.last_name, int(ref))
            await msg.answer_sticker(sticker=db.get_sticker('start'), reply_markup=kb.one_btn('Привет', 'hello'))
        else:
            await msg.answer(db.get_msg('not_member'))
    else:
        if not db.user_exists(msg.from_user.id):
            last_msg = await msg.answer('YO!', reply_markup=kb.main_menu())
            await bot.delete_message(chat_id=last_msg.chat.id, message_id=last_msg.message_id)
            db.add_user_id(msg.from_user.id, msg.from_user.username)
            await msg.answer_sticker(sticker=db.get_sticker('start'), reply_markup=kb.one_btn('Привет', 'hello'))
        else:
            await msg.answer(db.get_msg('menu_msg'), reply_markup=kb.main_menu())
    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)


# До После
async def start_before(user_id: int) -> None:
    await bot.send_message(chat_id=user_id, text=db.get_msg('before_photo_start'),
                           reply_markup=kb.one_btn('ГО', 'before_photo_start'))


# ЦИКЛ ДНЯ
async def evening_practic(user_id: int) -> None:
    await bot.send_sticker(chat_id=user_id, sticker=db.get_sticker('evening_practic'),
                           reply_markup=kb.evening_practic())


@dp.callback_query_handler(kb.evening_practic_cb.filter(), state='*')
async def evening_practic_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    if cb_data == 'yes':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('evening_practic'))
        await bot.send_audio(chat_id=callback_query.from_user.id, audio=types.InputFile('files/Новая запись 84.m4a'))
        await asyncio.sleep(20)
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('good_evening'))
    elif cb_data == 'no':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('good_evening'))
    else:
        print('ERROR evening_practic_cb')


async def skip_training(user_id: int, msg: types.Message) -> None:
    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    await bot.send_message(chat_id=user_id, text=db.get_msg('skip_training'),
                           reply_markup=kb.skip_training())


async def already_start_training(user_id: int, msg: types.Message) -> None:
    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
    last_msg = await bot.send_message(chat_id=user_id, text=db.get_msg('already_start_training'),
                                      reply_markup=kb.already_start_training())
    job_id = 'skip_training_' + str(user_id)
    # run_date = datetime.now() + timedelta(seconds=5)
    run_date = datetime.now() + timedelta(minutes=15)
    scheduler.add_job(skip_training, 'date', run_date=run_date, id=job_id,
                      kwargs={'user_id': user_id, 'msg': last_msg})


async def start_day(user_id: int, time: str, msg: types.Message) -> None:
    text_msg = db.get_msg('start_day')
    if time == '30':
        try:
            await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
        except Exception as ex:
            print(ex)
        text = str(text_msg).replace('час', 'полчаса')
        try:
            last_msg = await bot.send_message(chat_id=user_id, text=text, reply_markup=kb.start_day())
            job_id = 'start_day_' + str(user_id)
            # run_date = datetime.now() + timedelta(seconds=5)
            run_date = datetime.now() + timedelta(minutes=15)
            scheduler.add_job(start_day, 'date', run_date=run_date, id=job_id,
                              kwargs={'user_id': user_id, 'time': '15', 'msg': last_msg})
        except Exception as ex:
            print(ex)
    elif time == '15':
        try:
            await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
        except Exception as ex:
            print(ex)
        text = str(text_msg).replace('час', '15 минут')
        try:
            last_msg = await bot.send_message(chat_id=user_id, text=text, reply_markup=kb.start_day())
            job_id = 'already_start_training_' + str(user_id)
        # run_date = datetime.now() + timedelta(seconds=5)
            run_date = datetime.now() + timedelta(minutes=15)
            scheduler.add_job(already_start_training, 'date', run_date=run_date, id=job_id,
                              kwargs={'user_id': user_id, 'msg': last_msg})
        except Exception as ex:
            print(ex)
    else:
        text = str(text_msg)
        try:
            last_msg = await bot.send_message(chat_id=user_id, text=text, reply_markup=kb.start_day())
            job_id = 'start_day_' + str(user_id)
            # run_date = datetime.now() + timedelta(seconds=5)
            run_date = datetime.now() + timedelta(minutes=30)
            scheduler.add_job(start_day, 'date', run_date=run_date, id=job_id,
                              kwargs={'user_id': user_id, 'time': '30', 'msg': last_msg})
            date = datetime.now().strftime('%d.%m.%Y') + ' ' + '20:00'
            timezone = db.get_user(user_id)[5]
            run_date = run_date_func(datetime.strptime(date, '%d.%m.%Y %H:%M'), timezone)
            scheduler.add_job(evening_practic, 'date', run_date=run_date, kwargs={'user_id': user_id})
        except Exception as ex:
            print(ex)


@dp.callback_query_handler(kb.time_record_cb.filter(), state='*')
async def time_record_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    if cb_data == 'time':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('what_time_record'))
        await fsm.TimeRecord.wait_time.set()
    else:
        print('ERROR time_record_cb')


@dp.message_handler(state=fsm.TimeRecord.wait_time)
async def what_time_record(msg: types.Message, state: FSMContext) -> None:
    time = msg.text
    date = datetime.now().strftime('%d.%m.%Y') + f' {time}'
    try:
        run_date = datetime.strptime(date, '%d.%m.%Y %H:%M')
        if time > '10:00':
            scheduler.add_job(link_record, 'date', run_date=run_date, kwargs={'user_id': msg.from_user.id})
        #     await msg.answer('Хорошо 🧡\n\nОтправлю тебе ссылку на запись в указанное время')
        # else:
        #     await msg.answer('Хорошо 🧡\n\nСсылка на запись появится до 10 по МСК.')
        await asyncio.sleep(5)
        date = datetime.now().strftime('%d.%m.%Y')
        form_id = db.add_training_form(msg.from_user.id, 0, date)
        await bot.send_message(chat_id=msg.from_user.id, text=db.get_msg('record_training'),
                               reply_markup=kb.training_form_start())
        await fsm.FormTraining.start.set()
        await state.update_data(form_id=form_id)
    except Exception as ex:
        print(ex)
        await msg.answer('Неверно указано время. Попробуй снова в формате 18:00')


@dp.callback_query_handler(kb.start_day_cb.filter(), state='*')
async def start_day_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    job_list = list()
    job_list.append('start_day_' + str(callback_query.from_user.id))
    job_list.append('skip_training_' + str(callback_query.from_user.id))
    job_list.append('already_start_training_' + str(callback_query.from_user.id))
    for job_id in job_list:
        try:
            scheduler.remove_job(job_id=job_id)
        except Exception as ex:
            print(ex)
    if cb_data == 'online':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('record_training'),
                               reply_markup=kb.training_form_start())
        date = datetime.now().strftime('%d.%m.%Y')
        form_id = db.add_training_form(callback_query.from_user.id, 1, date)
        await fsm.FormTraining.start.set()
        await state.update_data(form_id=form_id)
        date = datetime.now().strftime('%d.%m.%Y') + ' 07:55'
        run_date = datetime.strptime(date, '%d.%m.%Y %H:%M')
        scheduler.add_job(link_zoom, 'date', run_date=run_date,
                          kwargs={'user_id': callback_query.from_user.id, 'msg': msg})
    elif cb_data == 'time_record':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('time_record'),
                               reply_markup=kb.time_record())
    elif cb_data == 'record':
        date = datetime.now().strftime('%d.%m.%Y')
        form_id = db.add_training_form(callback_query.from_user.id, 0, date)
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('record_training'),
                               reply_markup=kb.training_form_start())
        await fsm.FormTraining.start.set()
        await state.update_data(form_id=form_id)
    else:
        print('ERROR start_day_cb')


@dp.callback_query_handler(lambda c: c.data == 'training_form_start', state=fsm.FormTraining.start)
async def training_form_start_btn(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('yesterday'),
                           reply_markup=kb.yesterday())
    await fsm.FormTraining.yesterday.set()


@dp.callback_query_handler(kb.yestarday_cb.filter(), state=fsm.FormTraining.yesterday)
async def sleep_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    db.add_answer_trainig(callback_query.from_user.id, data['form_id'], 'yesterday', callback_data['answer'])
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('sleep'), reply_markup=kb.sleep())
    await fsm.FormTraining.sleep.set()


@dp.callback_query_handler(kb.sleep_cb.filter(), state=fsm.FormTraining.sleep)
async def sleep_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    db.add_answer_trainig(callback_query.from_user.id, data['form_id'], 'sleep', callback_data['answer'])
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('how_sleep'),
                           reply_markup=kb.point_scale())
    await fsm.FormTraining.how_sleep.set()


@dp.callback_query_handler(kb.point_scale_cb.filter(), state=fsm.FormTraining.how_sleep)
async def point_scale_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    points = callback_data['points']
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    db.add_answer_trainig(callback_query.from_user.id, data['form_id'], 'how_sleep', points)
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('work'),
                           reply_markup=kb.work())
    await fsm.FormTraining.work.set()


@dp.callback_query_handler(kb.work_cb.filter(), state=fsm.FormTraining.work)
async def work_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    answer = callback_data['answer']
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    db.add_answer_trainig(callback_query.from_user.id, data['form_id'], 'work', answer)
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('emotion_energy'),
                           reply_markup=kb.emotion_energy())
    await fsm.FormTraining.emotion_energy.set()


@dp.callback_query_handler(kb.emotion_energy_cb.filter(), state=fsm.FormTraining.emotion_energy)
async def emotion_energy_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    answer = callback_data['answer']
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    db.add_answer_trainig(callback_query.from_user.id, data['form_id'], 'emotion_energy', answer)
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('eat'),
                           reply_markup=kb.eat())
    await fsm.FormTraining.eat.set()


@dp.callback_query_handler(kb.eat_cb.filter(), state=fsm.FormTraining.eat)
async def eat_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    answer = callback_data['answer']
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    db.add_answer_trainig(callback_query.from_user.id, data['form_id'], 'eat', answer)
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('supermen'),
                           reply_markup=kb.point_scale())
    await fsm.FormTraining.supermen.set()


@dp.callback_query_handler(kb.point_scale_cb.filter(), state=fsm.FormTraining.supermen)
async def point_scale_btn_2(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    points = callback_data['points']
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    db.add_answer_trainig(callback_query.from_user.id, data['form_id'], 'supermen', points)
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('last'),
                           reply_markup=kb.last_btn())
    await fsm.FormTraining.last.set()
    await state.update_data(msg=msg)


@dp.message_handler(state=fsm.FormTraining.last)
async def last_question_form(msg: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    db.add_answer_trainig(msg.from_user.id, data['form_id'], 'last', msg.text)
    await state.finish()
    await link_zoom(msg.from_user.id, msg)


@dp.callback_query_handler(lambda c: c.data == 'last_btn_no', state=fsm.FormTraining.last)
async def last_question_form_no(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    data = await state.get_data()
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    db.add_answer_trainig(callback_query.from_user.id, data['form_id'], 'last', 'Нет')
    await link_zoom(callback_query.from_user.id, msg)
    await state.finish()


async def link_zoom(user_id: int, msg: types.Message) -> None:
    history_date = datetime.now().strftime("%d.%m.%Y")
    status_training = db.get_status_training_form(user_id, history_date)
    if status_training:
        print(1)
        if datetime.now().__format__('%H:%M') >= '07:54':
            try:
                link = db.get_training_links(datetime.now().strftime("%d.%m.%Y"))
                text = f'<i>Приглашаю тебя на тренировку практику:\n<a href="{link}">ССЫЛКА НА ЗУМ</a></i>'
            except:
                text = f'<i>Приглашаю тебя на тренировку практику:\n<a href="">ССЫЛКА НА ЗУМ</a></i>'
            text = text + '\n\n<i>*Если ты задерживаешься более, чем на 15 минут. Лучше пройди практику в записи. ' \
                          'Так лучше для твоего же здоровья.</i>'
            last_msg = await bot.send_message(chat_id=user_id, text=text,
                                              disable_web_page_preview=True)
            # date = datetime.now().strftime('%d.%m.%Y') + ' 09:30'
            # run_date = datetime.strptime(date, '%d.%m.%Y %H:%M')
            # scheduler.add_job(delete_link_training, 'date', run_date=run_date,
            #                   kwargs={'user_id': user_id, 'msg': last_msg})
        else:
            await bot.send_message(chat_id=user_id, text='Спасибо за ответы 🙏🏻🧘🏽‍♂️🧡\n\n<i>Скоро придет ссылка на ZOOM.</i>')
    else:
        try:
            link = db.get_training_record(datetime.now().strftime('%d.%m.%Y'))
            text = f'Спасибо за ответы 🙏🏻🧘🏽‍♂️🧡\n\n<a href="{link[1]}">ссылка на запись тренировки</a>\n\n'
            await bot.send_message(chat_id=user_id, text=text, disable_web_page_preview=True)
            # last_msg = await bot.send_message(chat_id=user_id, text=text, disable_web_page_preview=True)
            # run_date = datetime.now() + timedelta(minutes=90)
            # scheduler.add_job(delete_link_training, 'date', run_date=run_date,
            #                   kwargs={'user_id': user_id, 'msg': last_msg})
        except Exception as ex:
            print(ex)
            await bot.send_message(chat_id=user_id, text='Спасибо за ответы 🙏🏻🧘🏽‍♂️🧡\n\nСсылка на запись будет у тебя в меню')


async def link_record(user_id: int) -> None:
    date = datetime.now().strftime('%d.%m.%Y')
    link = db.get_training_record(date)
    if bool(len(link)):
        text = db.get_msg('training_record') + '\n\n' + f'🔗<a href="{link[1]}">ССЫЛКА  НА ЗАПИСЬ</a>\n\n'
        # text = text + db.get_msg('did_train')
        text = text
        await bot.send_message(chat_id=user_id, text=text)


@dp.callback_query_handler(lambda c: c.data == 'did_train', state='*')
async def did_train_btn(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    db.add_did_train(callback_query.from_user.id, 1, datetime.now().strftime('%d.%m.%Y'))
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('after_train'),
                           reply_markup=kb.point_scale())
    await fsm.FormTraining.after_train.set()


@dp.callback_query_handler(lambda c: c.data == 'no_did_train', state='*')
async def no_did_train_btn(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    db.add_did_train(callback_query.from_user.id, 0, datetime.now().strftime('%d.%m.%Y'))
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('no_did_train'))


@dp.callback_query_handler(kb.point_scale_cb.filter(), state=fsm.FormTraining.after_train)
async def point_scale_btn_3(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    points = callback_data['points']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    form_id = db.get_form_id(callback_query.from_user.id, datetime.now().strftime('%d.%m.%Y'))
    db.add_answer_trainig(callback_query.from_user.id, form_id, 'after_train', points)
    stickers = db.get_stickers('befriend')
    await bot.send_sticker(chat_id=msg.from_user.id, sticker=random.choice(stickers)[0])
    await state.finish()


async def delete_link_training(user_id: int, msg: types.Message) -> None:
    await bot.send_message(chat_id=user_id, text=db.get_msg('did_train'), reply_markup=kb.did_train())


# @dp.callback_query_handler(kb.after_zoom_cb.filter(), state='*')
# async def after_zoom_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
#     await bot.answer_callback_query(callback_query.id)
#     msg = callback_query.message
#     await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
#     cb_data = callback_data['action']
#     if cb_data == 'yes':
#         db.add_after_zoom(callback_query.from_user.id, 1, datetime.now().strftime('%d.%m.%Y'))
#     elif cb_data == 'no':
#         db.add_after_zoom(callback_query.from_user.id, 0, datetime.now().strftime('%d.%m.%Y'))
#     else:
#         print('ERROR after_zoom_cb')
#     await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('after_train'),
#                            reply_markup=kb.point_scale())
#     await fsm.FormTraining.after_train.set()


@dp.message_handler(state=fsm.Register.timezone)
async def get_timezone(msg: types.Message, state: FSMContext) -> None:
    timezone = msg.text.lower().replace('мск', '').replace('+', '').replace(' ', '').replace('msk', '')
    if timezone.replace('-', '').isnumeric():
        db.add_timezone(int(timezone), msg.from_user.id)
        await msg.answer(db.get_msg('how_work_question'), reply_markup=kb.one_btn('Ок', 'how_work_question'))
        await state.finish()
    else:
        await msg.answer('Неверно введен часовой пояс, укажи снова. Формат: <code>МСК+5</code>')
    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)


@dp.message_handler(state=fsm.Timezone.change)
async def change_timezone(msg: types.Message, state: FSMContext) -> None:
    timezone = msg.text.lower().replace('мск', '').replace('+', '').replace(' ', '').replace('msk', '')
    if timezone.replace('-', '').isnumeric():
        db.add_timezone(int(timezone), msg.from_user.id)
        await msg.answer(text=f'Часовой пояс изменен на {msg.text}')
        await state.finish()
    else:
        await msg.answer('Неверно введен часовой пояс, укажи снова. Формат: <code>МСК+5</code>')
    await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)


@dp.callback_query_handler(kb.one_btn_cb.filter(), state='*')
async def one_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    if cb_data == 'hello':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('register'),
                               reply_markup=kb.timezone())
    elif cb_data == 'how_work_question':
        await bot.send_message(chat_id=callback_query.from_user.id, text=cfg.Texts.how_it_work,
                               reply_markup=kb.how_work_answer())
    elif cb_data == 'timezone_msk':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('how_work_question'),
                               reply_markup=kb.one_btn('Ок', 'how_work_question'))
        await state.finish()
    elif cb_data == 'before_photo_start':
        link = db.get_video('before_video')
        text = db.get_msg('before_photo_instruction')
        if bool(link):
            text = str(text).replace('Мы записали видео с информацией:',
                                     f'<a href="{link}">Мы записали видео с информацией:</a>')
        await bot.send_message(chat_id=callback_query.from_user.id, text=text)
        run_date = datetime.now() + timedelta(minutes=10)
        # run_date = datetime.now() + timedelta(seconds=5)
        job_id = 'watched_' + str(callback_query.from_user.id)
        scheduler.add_job(check_watched_video, 'date', run_date=run_date, id=job_id,
                          kwargs={'user_id': callback_query.from_user.id})
    # elif cb_data == 'start_week_questions':
    #     await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_question('week_1'))
    #     await fsm.WeekQuestions.week_1.set()
    #     form_id = db.add_week_questions_form(callback_query.from_user.id, datetime.now().strftime('%d.%m.%Y'))
    #     await state.update_data(form_id=form_id)
    else:
        print('ERROR one_btn')


# Блок с недельными вопросами
# @dp.message_handler(state=fsm.WeekQuestions)
# async def week_question_first(msg: types.Message, state: FSMContext) -> None:
#     current_state = await state.get_state()
#     question_code = current_state.replace('WeekQuestions:', '')
#     data = await state.get_data()
#     db.add_week_questions_answer(msg.from_user.id, data['form_id'], question_code, msg.text)
#     if question_code != 'week_7':
#         await fsm.WeekQuestions.next()
#         next_state = await state.get_state()
#         next_question_code = next_state.replace('WeekQuestions:', '')
#         await bot.send_message(chat_id=msg.from_user.id, text=db.get_question(next_question_code))
#     else:
#         await state.finish()
#         await bot.send_message(chat_id=msg.from_user.id, text=db.get_msg('thanks_week'))


async def check_watched_video(user_id: int, status=None) -> None:
    if status == 'again':
        await bot.send_message(chat_id=user_id, text=db.get_msg('check_watched_video'),
                               reply_markup=kb.check_watched_video(1))
    else:
        await bot.send_message(chat_id=user_id, text=db.get_msg('check_watched_video'),
                               reply_markup=kb.check_watched_video(0))


@dp.callback_query_handler(kb.check_watched_video_cb.filter(), state='*')
async def check_watched_video_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    if cb_data == 'yes':
        media = types.MediaGroup()
        file_dir = 'media/before_photo'
        photos = os.listdir(file_dir)
        text = db.get_msg('before_photo')
        for i in range(len(photos)):
            file_path = file_dir + f'/{photos[i]}'
            if os.path.isfile(file_path):
                if i == len(photos) - 1:
                    media.attach_photo(types.InputFile(file_path), caption=text)
                else:
                    media.attach_photo(types.InputFile(file_path))
        await bot.send_media_group(chat_id=callback_query.from_user.id, media=media)
        await fsm.BeforePhoto.wait.set()
        job_id = 'job_photo_' + str(callback_query.from_user.id)
        await state.update_data(job_id=job_id)
        # поменять время
        # run_date = datetime.now() + timedelta(seconds=5)
        run_date = datetime.now() + timedelta(hours=6)
        scheduler.add_job(no_photo, 'date', run_date=run_date, id=job_id, kwargs={'user_id': callback_query.from_user.id})
    elif cb_data == 'no':
        user = db.get_user(callback_query.from_user.id)
        curator_id = user[6]
        text = f'Участник (@{user[2]} | {user[1]} просит связаться с ним (этап просмотра видео до/после)'
        await admin_bot.send_message(chat_id=curator_id, text=text,
                                     reply_markup=kb.from_support('Связаться', msg.from_user.id, 1))
        await bot.send_message(chat_id=callback_query.from_user.id, text='Хорошо. Саппорт уже спешит к тебе')
    elif cb_data == 'later':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('later_instruction'))
        await fsm.Instruction.wait_time.set()
    elif cb_data == 'not_today':
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text='Спасибо за ответ. Ты сможешь посмотреть видео позже')
        user = db.get_user(callback_query.from_user.id)
        curator_id = user[6]
        text = f'Участник (@{user[2]} | {user[1]}) не может сегодня посмотреть видео (из блока До/После)\n\n' \
               f'Если нужно свяжитесь с ним'
        await admin_bot.send_message(chat_id=curator_id, text=text,
                                     reply_markup=kb.from_support('Связаться', msg.from_user.id, 1))
    else:
        print('ERROR after_video_training')
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


async def later_video(user_id: int) -> None:
        link = db.get_video('before_video')
        text = db.get_msg('video_again')
        if bool(link):
            text = text + f' <a href="{link}">видео-инструкцию </a>🙏🏻'
        await bot.send_message(chat_id=user_id, text=text)
        # run_date = datetime.now() + timedelta(seconds=5)
        run_date = datetime.now() + timedelta(minutes=10)
        scheduler.add_job(check_watched_video, 'date', run_date=run_date, kwargs={'user_id': user_id, 'status': 'again'})


@dp.message_handler(state=fsm.Instruction.wait_time)
async def later_time(msg: types.Message, state: FSMContext) -> None:
    try:
        time = datetime.strptime((datetime.now().strftime('%d.%m.%Y') + ' ' + msg.text.replace(' ', '')), '%d.%m.%Y %H:%M')
        await msg.answer('Спасибо! Пришлю видео в указанное время!')
        user = db.get_user(msg.from_user.id)
        run_date = run_date_func(time, user[5])
        # run_date = run_date_func(time, 0)
        scheduler.add_job(later_video, 'date', run_date=run_date, kwargs={'user_id': msg.from_user.id})
        await state.finish()
    except Exception as ex:
        print(ex)
        await msg.answer('Неверно указано время. Укажи его в формате: "18:00"')


photo_delivered = set()


async def photo_next(user_id: int) -> None:
    if user_id in photo_delivered:
        return
    photo_delivered.add(user_id)
    await fsm.BeforePhoto.next_photo.set()
    await bot.send_message(user_id, 'Подтверди, пожалуйста, что все фото загружены 🙏🏻',
                           reply_markup=kb.before_photo_confirm())


@dp.callback_query_handler(kb.before_photo_confirm_cb.filter(), state=fsm.BeforePhoto.next_photo)
async def before_photo_confirm_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    if cb_data == 'confirm':
        await bot.send_sticker(chat_id=callback_query.from_user.id, sticker=db.get_sticker('before_photo'))
        await asyncio.sleep(5)
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('use_photo'),
                               reply_markup=kb.use_photo())
        await state.finish()
    elif cb_data == 'more':
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text='👉 После того, как фото будут готовы, просто отправь мне их сюда.')
        await fsm.BeforePhoto.wait.set()
    else:
        print('ERROR before_photo_confirm_cb')


@dp.message_handler(content_types=['photo'], state=fsm.BeforePhoto.all_states)
async def before_photo(msg: types.Message, state: FSMContext) -> None:
    await photo_next(msg.from_user.id)
    file_path = f'media/{msg.from_user.id}'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    data = await state.get_data()
    try:
        scheduler.remove_job(job_id=data['job_id'])
    except Exception as ex:
        print(ex)
    try:
        number = data['number']
    except:
        number = 1
    await state.update_data(number=(number+1))
    photo = msg.photo.pop()
    filename = f'before_{msg.from_user.id}_{number}.png'
    await photo.download(destination_file=f'{file_path}/{filename}')


@dp.callback_query_handler(kb.use_photo_cb.filter(), state='*')
async def use_photo(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    text_use = ''
    if cb_data == 'yes':
        text_use = 'можно использовать фото'
        db.add_before_photo(callback_query.from_user.id, 1, 'Можно')
    elif cb_data == 'yes_without':
        text_use = 'можно использовать без имени и лица'
        db.add_before_photo(callback_query.from_user.id, 1, 'Без имени и лица')
    elif cb_data == 'no':
        text_use = 'нельзя использовать фото'
        db.add_before_photo(callback_query.from_user.id, 1, 'Нельзя')
    else:
        print('ERROR use_photo_cb')
    media = types.MediaGroup()
    file_dir = f'media/{callback_query.from_user.id}'
    photos = os.listdir(file_dir)
    user = db.get_user(callback_query.from_user.id)
    for i in range(len(photos)):
        file_path = file_dir + f'/{photos[i]}'
        if os.path.isfile(file_path) and 'before' in file_path:
            if i == len(photos) - 1:
                media.attach_photo(types.InputFile(file_path),
                                   caption=f'Фото ДО от (@{user[2]} | {user[1]})\n\n{text_use}')
            else:
                media.attach_photo(types.InputFile(file_path))
    await admin_bot.send_media_group(chat_id=user[6], media=media)
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await state.finish()
    await bot.send_message(chat_id=callback_query.from_user.id, text='Спасибо за фото 🙏')


async def no_photo(user_id: int) -> None:
    db.add_before_photo(user_id, 0, 'нет фото')
    await bot.send_sticker(chat_id=user_id, sticker=db.get_sticker('no_photo'),
                           reply_markup=kb.no_photo())
    user = db.get_user(user_id)
    await admin_bot.send_message(chat_id=user[6], text=f'Участник (@{user[2]} | {user[1]}) не скинул фото ДО')


@dp.callback_query_handler(kb.no_photo_cb.filter(), state='*')
async def no_photo_btns(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    await state.finish()
    if cb_data == 'yes':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('after_photo'),
                               reply_markup=kb.after_photo())
    elif cb_data == 'questions':
        user = db.get_user(callback_query.from_user.id)
        curator_id = user[6]
        text = f'У участника (@{user[2]} | {user[1]} есть вопросы (участник не скинул фото и хочет что-то уточнить)'
        await admin_bot.send_message(chat_id=curator_id, text=text,
                                     reply_markup=kb.from_support('Связаться', msg.from_user.id, 1))
        await bot.send_message(chat_id=callback_query.from_user.id, text='Хорошо. Саппорт уже спешит к тебе')
    else:
        print('ERROR no_photo_cb')


@dp.callback_query_handler(kb.after_photo_cb.filter(), state='*')
async def after_photo_btns(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    if cb_data == 'yes':
        user = db.get_user(callback_query.from_user.id)
        curator_id = user[6]
        text = f'Участник (@{user[2]} | {user[1]} не против связаться по поводу фото (конец цепочки по фото)'
        await admin_bot.send_message(chat_id=curator_id, text=text,
                                     reply_markup=kb.from_support('Связаться', msg.from_user.id, 1))
        await bot.send_message(chat_id=callback_query.from_user.id, text='Супер! Саппорт уже спешит к тебе')
    elif cb_data == 'no':
        user = db.get_user(callback_query.from_user.id)
        curator_id = user[6]
        text = f'Участник (@{user[2]} | {user[1]} пока не готов общаться по поводу фото (конец цепочки по фото)'
        await admin_bot.send_message(chat_id=curator_id, text=text)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text='Хорошо. С саппортом всегда можно связаться через меню')
    else:
        print('ERROR after_photo_cb')


@dp.callback_query_handler(kb.timezone_cb.filter(), state='*')
async def one_btn(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    if cb_data == 'another':
        await fsm.Register.timezone.set()
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('timezone'))
    else:
        print('ERROR timezone_cb')


@dp.callback_query_handler(kb.after_start_cb.filter(), state='*')
async def after_start(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    if cb_data == 'instruction':
        link = db.get_video('video_training')
        text = cfg.Texts.instruction_before + f' <a href="{link}">(посмотреть видео)</a>' + cfg.Texts.instruction_after
        await bot.send_message(chat_id=callback_query.from_user.id, text=text, reply_markup=kb.reaction())
    elif cb_data == 'training':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('go_to_train'),
                               reply_markup=kb.main_menu())
    else:
        print('ERROR after_start_cb')


@dp.callback_query_handler(lambda c: c.data == 'reaction', state='*')
async def reaction_instruction(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('go_to_train'),
                           reply_markup=kb.main_menu())


@dp.callback_query_handler(kb.how_work_answer_cb.filter(), state='*')
async def how_work_answer(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    cb_data = callback_data['action']
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    if cb_data == 'yes':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('after_start'),
                               reply_markup=kb.after_start())
    elif cb_data == 'support':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('to_support'))
        await fsm.ToSupport.msg.set()
        run_date = datetime.now() + timedelta(hours=1)
        job_id = 'tosupport_' + str(callback_query.from_user.id)
        scheduler.add_job(support_answer, 'date', run_date=run_date, id=job_id,
                          kwargs={'user_id': callback_query.from_user.id})
    elif cb_data == 'yes_support':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('yes_support'))
    elif cb_data == 'no_support':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('to_support'))
        await fsm.ToSupport.msg.set()
        run_date = datetime.now() + timedelta(hours=1)
        job_id = 'tosupport_' + str(callback_query.from_user.id)
        scheduler.add_job(support_answer, 'date', run_date=run_date, id=job_id,
                          kwargs={'user_id': callback_query.from_user.id})
    else:
        print('ERROR how_work_answer_cb')


@dp.message_handler(state=fsm.ToSupport.msg)
async def to_support(msg: types.Message, state: FSMContext) -> None:
    user = db.get_user(msg.from_user.id)
    curator_id = user[6]
    text = f'Сообщение от участника (@{user[2]} | {user[1]}):\n\n{msg.text}'
    await admin_bot.send_message(chat_id=curator_id, text=text,
                                 reply_markup=kb.from_support('Ответить', msg.from_user.id, 1))
    db.add_support_msg(msg.from_user.id, user[1], msg.text, 'from')
    await state.finish()


@dp.callback_query_handler(kb.from_support_cb.filter(), state='*')
async def from_support(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext) -> None:
    await bot.answer_callback_query(callback_query.id)
    msg = callback_query.message
    await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=None)
    job_id = 'tosupport_' + str(callback_query.from_user.id)
    scheduler.remove_job(job_id)
    user_id = callback_data['user_id']
    if user_id == 'thanks':
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('support_thanks'))
    else:
        await bot.send_message(chat_id=callback_query.from_user.id, text=db.get_msg('to_support'))
        await fsm.ToSupport.msg.set()
        run_date = datetime.now() + timedelta(hours=1)
        job_id = 'tosupport_' + str(callback_query.from_user.id)
        scheduler.add_job(support_answer, 'date', run_date=run_date, id=job_id,
                          kwargs={'user_id': callback_query.from_user.id})


@dp.message_handler(commands=['start_day'], state='*')
async def add_start_day_fn(msg: types.Message) -> None:
    users = db.get_users()
    date = datetime.now()
    # date = datetime.now() + timedelta(days=1)
    run_date = datetime.strptime(date.strftime('%d.%m.%Y') + ' 07:00', '%d.%m.%Y %H:%M')
    for user in users:
        time.sleep(1)
        try:
            scheduler.add_job(start_day, 'date', run_date=run_date,
                              kwargs={'user_id': user[1], 'time': 'hour', 'msg': msg})
            await msg.answer(f'{user[1]} запланирован')
        except Exception as ex:
            print(ex)
            await msg.answer(ex)
            await msg.answer(f'{user[1]} запланирован')
    await msg.answer('Все запланировано!')


@dp.message_handler(commands=['start_before'], state='*')
async def start_before_command(msg: types.Message, state: FSMContext) -> None:
    users = db.get_users()
    date = datetime.now()
    run_date = datetime.strptime(date.strftime('%d.%m.%Y') + ' 10:00', '%d.%m.%Y %H:%M')
    for user in users:
        time.sleep(1)
        try:
            scheduler.add_job(start_before, 'date', run_date=run_date, kwargs={'user_id': user[1]})
            await msg.answer(f'{user[1]} запланирован')
        except Exception as ex:
            print(ex)
            await msg.answer(ex)
            await msg.answer(f'{user[1]} запланирован')
    await msg.answer('Все запланировано!')


@dp.message_handler(commands=['start_evening'], state='*')
async def start_evening_fn(msg: types.Message) -> None:
    users = db.get_users()
    date = datetime.now().strftime('%d.%m.%Y') + ' ' + '20:00'
    for user in users:
        timezone = user[5]
        run_date = run_date_func(datetime.strptime(date, '%d.%m.%Y %H:%M'), timezone)
        await msg.answer(f'{user[1]} запланирован')
        scheduler.add_job(evening_practic, 'date', run_date=run_date, kwargs={'user_id': user[1]})
    await msg.answer('Все запланировано!')


@dp.message_handler(commands=['must_start_day'])
async def add_start_day(msg: types.Message) -> None:
    users = db.get_users()
    for user in users:
        await start_day(user[1], '15', msg)
        await msg.answer(f'{user[1]} отправлено!')
    await msg.answer('Все отправлено!')


@dp.message_handler(commands=['msg_to_user'], state='*')
async def msg_to_user(msg: types.Message, state: FSMContext) -> None:
    user_id = msg.text[13:]
    try:
        await bot.send_message(chat_id=user_id, text=db.get_msg('before_photo_start'),
                               reply_markup=kb.one_btn('ГО', 'before_photo_start'))
    except Exception as ex:
        print(ex)
        await msg.answer(ex)


@dp.message_handler(commands=['week_question'], state='*')
async def week_question(msg: types.Message, state: FSMContext) -> None:
    users = db.get_users()
    for user in users:
        try:
            await bot.send_message(chat_id=user[1], text=db.get_msg('week_question'))
            await fsm.WeekQuestions.week_1.set()
        except Exception as ex:
            print(ex)
    await msg.answer('Отправлено')


@dp.message_handler(state=fsm.WeekQuestions.week_1)
async def week_answer(msg: types.Message, state: FSMContext) -> None:
    user = db.get_user(msg.from_user.id)
    curator_id = user[6]
    db.add_week_answer(msg.from_user.id, msg.text)
    await admin_bot.send_message(chat_id=curator_id,
                                 text=f'Вопрос на практику-разбор от участника (@{user[2]} | {user[1]})\n\n{msg.text}')
    await msg.answer('Спасибо!')
    await state.finish()


async def on_startup(_):
    print('Клиент-Бот запущен!')
    scheduler.start()


# Эхо функция
@dp.message_handler(state='*')
async def echo(msg: types.Message) -> None:
    user = db.get_user(msg.from_user.id)
    curator_id = user[6]
    text = f'Эхо-сообщение от участника (@{user[2]} | {user[1]}):\n\n{msg.text}\n\n' \
           f'Возможно он отправил его случайно!'
    await admin_bot.send_message(chat_id=curator_id, text=text,
                                 reply_markup=kb.from_support('Ответить', msg.from_user.id, 1))
    await msg.answer('Сообщние отправлено в поддержку', reply_markup=kb.main_menu())
    db.add_support_msg(msg.from_user.id, user[1], msg.text, 'from')


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
