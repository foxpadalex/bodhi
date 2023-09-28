import datetime

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData


one_btn_cb = CallbackData('one_btn', 'action')
no_before_photo_cb = CallbackData('no_before_photo', 'action')
after_video_training_cb = CallbackData('after_video_training', 'action')
before_start_training_cb = CallbackData('before_start_training', 'action')
how_work_answer_cb = CallbackData('how_work_answer', 'action')
from_support_cb = CallbackData('from_support', 'user_id')
after_instruction_cb = CallbackData('after_instruction', 'action')
ready_training_cb = CallbackData('ready_training', 'action')
timezone_cb = CallbackData('timezone', 'action')

after_start_cb = CallbackData('after_start', 'action')

check_watched_video_cb = CallbackData('after_video_training_again', 'action')
no_photo_cb = CallbackData('no_photo', 'action')
after_photo_cb = CallbackData('after_photo', 'action')
use_photo_cb = CallbackData('use_photo', 'action')
before_photo_confirm_cb = CallbackData('before_photo_confirm', 'action')

start_day_cb = CallbackData('start_day', 'action')


# Общая часть
def generate_kb(row_width, btns) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=row_width)
    kb.add(*btns)
    return kb


def after_start() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Инструкция', callback_data=after_start_cb.new(action='instruction')),
        InlineKeyboardButton(text='Перейти к тренировкам', callback_data=after_start_cb.new(action='training'))
    ]
    return generate_kb(2, btns)


def timezone() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Да, МСК', callback_data=one_btn_cb.new(action='timezone_msk')),
        InlineKeyboardButton(text='Другое', callback_data=timezone_cb.new(action='another'))
    ]
    return generate_kb(2, btns)


def main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    btns = [
        KeyboardButton(text='Расписание'),
        KeyboardButton(text='Записи практик'),
        KeyboardButton(text='Фокус недели'),
        KeyboardButton(text='FAQ'),
        KeyboardButton(text='Красная кнопка 🚨'),
        KeyboardButton(text='Сменить часовой пояс'),
        KeyboardButton(text='Медитации')
        # KeyboardButton(text='Отправить фото')
        # KeyboardButton(text='Статистика')
    ]
    kb.add(*btns)
    return kb


def faq() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Часто задаваемы вопросы',
                             url='https://docs.google.com/spreadsheets/d/1wJVhWmB6233TaK0MJDPJC763sE90rWIVVlijAUK_h-Y/edit')
    ]
    return generate_kb(1, btns)


def one_btn(text, cb_data) -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text=text, callback_data=one_btn_cb.new(action=cb_data))
    ]
    return generate_kb(1, btns)


def how_work_answer() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Да', callback_data=how_work_answer_cb.new(action='yes')),
        InlineKeyboardButton(text='Есть вопросы', callback_data=how_work_answer_cb.new(action='support'))
    ]
    return generate_kb(2, btns)


def support_answer() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Да', callback_data=how_work_answer_cb.new(action='yes_support')),
        InlineKeyboardButton(text='Еще есть вопросы', callback_data=how_work_answer_cb.new(action='no_support'))
    ]
    return generate_kb(2, btns)


def use_photo() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Да', callback_data=use_photo_cb.new(action='yes')),
        InlineKeyboardButton(text='Да, без имени и лица', callback_data=use_photo_cb.new(action='yes_without')),
        InlineKeyboardButton(text='Нет, пожалуйста', callback_data=use_photo_cb.new(action='no'))
    ]
    return generate_kb(2, btns)


def reaction() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='🧡', callback_data='reaction'),
        InlineKeyboardButton(text='🦄', callback_data='reaction'),
        InlineKeyboardButton(text='👏🏻', callback_data='reaction')
    ]
    return generate_kb(3, btns)


def after_instruction() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Да, спасибо!', callback_data=after_instruction_cb.new(action='yes')),
        InlineKeyboardButton(text='Помощь саппорта',
                             callback_data=after_instruction_cb.new(action='support'))
    ]
    return generate_kb(1, btns)


def ready_training() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Я тоже', callback_data=ready_training_cb.new(action='ready')),
        InlineKeyboardButton(text='Помощь саппорта',
                             callback_data=ready_training_cb.new(action='support'))
    ]
    return generate_kb(1, btns)


def no_before_photo() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Хорошо', callback_data=no_before_photo_cb.new(action='yes')),
        InlineKeyboardButton(text='Пока не готов(а) общаться', callback_data=no_before_photo_cb.new(action='no'))
    ]
    return generate_kb(2, btns)


def schedule_training(vip) -> InlineKeyboardMarkup:
    btns = []
    if vip:
        btns.append(InlineKeyboardButton(text='Расписание', url='https://t.me/c/1910674437/6'))
    else:
        btns.append(InlineKeyboardButton(text='Расписание', url='https://t.me/c/1841093161/6'))
    return generate_kb(1, btns)


# ADMIN
def admin_main_menu(role) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    btns = []
    if role == 1:
        btns.extend([
            KeyboardButton(text='Добавить куратора'),
            KeyboardButton(text='Тексты'),
            # KeyboardButton(text='Добавить видео'),
            KeyboardButton(text='Запись практики'),
            KeyboardButton(text='Рассылка по группе'),
            KeyboardButton(text='Статистика')
        ])
        if datetime.datetime.now() <= datetime.datetime.strptime('31.08.2023 1:00', '%d.%m.%Y %H:%M'):
            btns.append(KeyboardButton(text='Распределить участников'))
    elif role == 2:
        btns.extend([
            KeyboardButton(text='Добавить участника'),
            KeyboardButton(text='Список участников'),
            KeyboardButton(text='Рассылка по группе'),
            KeyboardButton(text='Статистика')
        ])
    elif role == 3:
        btns.extend([
            KeyboardButton(text='Добавить куратора'),
            KeyboardButton(text='Тексты'),
            # KeyboardButton(text='Добавить видео'),
            KeyboardButton(text='Статистика'),
            KeyboardButton(text='Запись практики'),
            KeyboardButton(text='Рассылка по группе'),
            KeyboardButton(text='Статистика по участнику'),
            KeyboardButton(text='Кружок')
        ])
    kb.add(*btns)
    return kb


def users2curators() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Загрузить список участников', callback_data='users2curators')
    ]
    return generate_kb(1, btns)


def from_support(text, user_id, status_curator) -> InlineKeyboardMarkup:
    if status_curator:
        btns = [InlineKeyboardButton(text=text, callback_data=from_support_cb.new(user_id=user_id))]
    else:
        btns = [
            InlineKeyboardButton(text=text, callback_data=from_support_cb.new(user_id=user_id)),
            InlineKeyboardButton(text='Спасибо', callback_data=from_support_cb.new(user_id='thanks'))
        ]
    return generate_kb(2, btns)


# До / После
def check_watched_video(again=0) -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Да🧡', callback_data=check_watched_video_cb.new(action='yes')),
        InlineKeyboardButton(text='Нужна помощь', callback_data=check_watched_video_cb.new(action='no'))
    ]
    if again:
        btns.append(InlineKeyboardButton(text='Нет времени это сделать сегодня',
                                         callback_data=check_watched_video_cb.new(action='not_today')))
    else:
        btns.append(InlineKeyboardButton(text='Хочу посмотреть позже',
                                         callback_data=check_watched_video_cb.new(action='later')))
    return generate_kb(2, btns)


def no_photo() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Да, все хорошо🧡', callback_data=no_photo_cb.new(action='yes')),
        InlineKeyboardButton(text='Есть вопросы!', callback_data=no_photo_cb.new(action='questions')),
    ]
    return generate_kb(1, btns)


def after_photo() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Хорошо', callback_data=after_photo_cb.new(action='yes')),
        InlineKeyboardButton(text='Пока не готов(а)',
                             callback_data=after_photo_cb.new(action='no')),
    ]
    return generate_kb(2, btns)


def before_photo_confirm() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Загружены', callback_data=before_photo_confirm_cb.new(action='confirm')),
        InlineKeyboardButton(text='Еще фото', callback_data=before_photo_confirm_cb.new(action='more'))
    ]
    return generate_kb(2, btns)


# ЦИКЛ ДНЯ
yestarday_cb = CallbackData('yestarday', 'answer')
sleep_cb = CallbackData('sleep', 'answer')
point_scale_cb = CallbackData('point_scale', 'points')
emotion_energy_cb = CallbackData('emotion_energy', 'answer')
eat_cb = CallbackData('eat', 'answer')
work_cb = CallbackData('eat', 'answer')
time_record_cb = CallbackData('time_record', 'action')
evening_practic_cb = CallbackData('evening_practic', 'action')
after_zoom_cb = CallbackData('after_zoom', 'action')


def start_day() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Буду онлайн', callback_data=start_day_cb.new(action='online')),
        InlineKeyboardButton(text='Буду в записи', callback_data=start_day_cb.new(action='time_record'))
    ]
    return generate_kb(2, btns)


def skip_training() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Получить тренировку', callback_data=start_day_cb.new(action='record'))
    ]
    return generate_kb(1, btns)


def already_start_training() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Войти на тренировку', callback_data=start_day_cb.new(action='online'))
    ]
    return generate_kb(1, btns)


def training_form_start() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='ГО', callback_data='training_form_start')
    ]
    return generate_kb(1, btns)


def sleep() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='до 22', callback_data=sleep_cb.new(answer='до 22')),
        InlineKeyboardButton(text='до 23', callback_data=sleep_cb.new(answer='до 23')),
        InlineKeyboardButton(text='до 00', callback_data=sleep_cb.new(answer='до 00')),
        InlineKeyboardButton(text='после 00', callback_data=sleep_cb.new(answer='после 00'))
    ]
    return generate_kb(2, btns)


def yesterday() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='да, в записи', callback_data=yestarday_cb.new(answer='в записи')),
        InlineKeyboardButton(text='да, онлайн', callback_data=yestarday_cb.new(answer='онлайн')),
        InlineKeyboardButton(text='нет', callback_data=yestarday_cb.new(answer='нет'))
    ]
    return generate_kb(2, btns)


def point_scale() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='1', callback_data=point_scale_cb.new(points='1')),
        InlineKeyboardButton(text='2', callback_data=point_scale_cb.new(points='2')),
        InlineKeyboardButton(text='3', callback_data=point_scale_cb.new(points='3')),
        InlineKeyboardButton(text='4', callback_data=point_scale_cb.new(points='4')),
        InlineKeyboardButton(text='5', callback_data=point_scale_cb.new(points='5')),
        InlineKeyboardButton(text='6', callback_data=point_scale_cb.new(points='6')),
        InlineKeyboardButton(text='7', callback_data=point_scale_cb.new(points='7')),
        InlineKeyboardButton(text='8', callback_data=point_scale_cb.new(points='8')),
        InlineKeyboardButton(text='9', callback_data=point_scale_cb.new(points='9')),
        InlineKeyboardButton(text='10', callback_data=point_scale_cb.new(points='10'))
    ]
    return generate_kb(5, btns)


def emotion_energy() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='1',
                             callback_data=emotion_energy_cb.new(answer='1')),
        InlineKeyboardButton(text='2',
                             callback_data=emotion_energy_cb.new(answer='2')),
        InlineKeyboardButton(text='3',
                             callback_data=emotion_energy_cb.new(answer='3'))
    ]
    return generate_kb(3, btns)


def eat() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='до 18', callback_data=eat_cb.new(answer='до 18')),
        InlineKeyboardButton(text='с 18 до 19', callback_data=eat_cb.new(answer='с 18 до 19')),
        InlineKeyboardButton(text='с 19 до 20', callback_data=eat_cb.new(answer='с 19 до 20')),
        InlineKeyboardButton(text='после 20', callback_data=eat_cb.new(answer='после 20'))
    ]
    return generate_kb(2, btns)


def work() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='до 18', callback_data=work_cb.new(answer='до 18')),
        InlineKeyboardButton(text='с 18 до 19', callback_data=work_cb.new(answer='с 18 до 19')),
        InlineKeyboardButton(text='с 19 до 20', callback_data=work_cb.new(answer='с 19 до 20')),
        InlineKeyboardButton(text='после 20', callback_data=work_cb.new(answer='после 20'))
    ]
    return generate_kb(2, btns)


def last_btn() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Нет', callback_data='last_btn_no')
    ]
    return generate_kb(1, btns)


def time_record() -> InlineKeyboardMarkup:
    btns = []
    btns.append(InlineKeyboardButton(text='Укажу время 🕖', callback_data=time_record_cb.new(action='time')))
    btns.append(InlineKeyboardButton(text='Использую меню 👌🏻', callback_data=start_day_cb.new(action='record')))
    return generate_kb(1, btns)


# def after_zoom() -> InlineKeyboardMarkup:
#     btns = [
#         InlineKeyboardButton(text='Был(а)', callback_data=after_zoom_cb.new(action='yes')),
#         InlineKeyboardButton(text='Не был(а)', callback_data=after_zoom_cb.new(action='no'))
#     ]
#     return generate_kb(2, btns)


def did_train() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Выполнил(а)', callback_data='did_train'),
        InlineKeyboardButton(text='Не выполнил(а)', callback_data='no_did_train')
    ]
    return generate_kb(1, btns)


def evening_practic() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Сегодня нет времени', callback_data=evening_practic_cb.new(action='no')),
        InlineKeyboardButton(text='Скинь ее, пожалуйста', callback_data=evening_practic_cb.new(action='yes'))
    ]
    return generate_kb(1, btns)


record_confirm_cb = CallbackData('record_confirm', 'action')
video_note_confirm_cb = CallbackData('video_note_confirm', 'action')


def record_confirm() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Подтвердить', callback_data=record_confirm_cb.new(action='yes')),
        InlineKeyboardButton(text='Отменить', callback_data=record_confirm_cb.new(action='no'))
    ]
    return generate_kb(2, btns)


def video_note_confirm() -> InlineKeyboardMarkup:
    btns = [
        InlineKeyboardButton(text='Подтвердить', callback_data=video_note_confirm_cb.new(action='yes')),
        InlineKeyboardButton(text='Отменить', callback_data=video_note_confirm_cb.new(action='no'))
    ]
    return generate_kb(2, btns)
