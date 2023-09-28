from aiogram.dispatcher.filters.state import StatesGroup, State


class Register(StatesGroup):
    timezone = State()


class Timezone(StatesGroup):
    change = State()


class BeforePhoto(StatesGroup):
    wait = State()
    next_photo = State()


class Users2Curators(StatesGroup):
    wait = State()


class Sticker(StatesGroup):
    code = State()


class Instruction(StatesGroup):
    wait_time = State()


class ToSupport(StatesGroup):
    msg = State()


class Video(StatesGroup):
    link = State()
    code = State()


class FormTraining(StatesGroup):
    record = State()
    start = State()
    yesterday = State()
    sleep = State()
    work = State()
    how_sleep = State()
    emotion_energy = State()
    eat = State()
    supermen = State()
    last = State()
    after_train = State()


class Record(StatesGroup):
    text = State()
    link = State()
    confirm = State()


class TimeRecord(StatesGroup):
    wait_time = State()


class WeekQuestions(StatesGroup):
    week_1 = State()
    week_2 = State()
    week_3 = State()
    week_4 = State()
    week_5 = State()
    week_6 = State()
    week_7 = State()


class VideoNote(StatesGroup):
    video = State()
    confirm = State()


class Statistic(StatesGroup):
    username = State()
