import os

from dotenv import load_dotenv

load_dotenv()

USER_BOT_NAME = str(os.getenv("USER_BOT_NAME"))
USER_BOT_TOKEN = str(os.getenv("USER_BOT_TOKEN"))
ADMIN_BOT_NAME = str(os.getenv("ADMIN_BOT_NAME"))
ADMIN_BOT_TOKEN = str(os.getenv("ADMIN_BOT_TOKEN"))


class Texts:
    how_it_work = 'Моя задача создать такие условия, где <b>мы сможем в легкости пройти путь веллнесс-коучинга от начала ' \
                  'до конца без напряжения.</b>\nИ качественно помочь тебе решить твой запрос на этот месяц 🧡\n\n' \
                  'Поэтому ниже я поделюсь, как будет выстроено наше с тобой взаимодействие, смотри 👇🏻\n\n' \
                  '1️⃣ Каждое утро я буду интересоваться готов(а) ли ты пройти занятие онлайн. Если нет, то в какое время' \
                  ' прислать тебе запись.\n\n' \
                  '2️⃣ Чтобы попасть на тренировку я попрошу тебя ответить на перечень вопросов, которые нам помогут ' \
                  'максимально эффективно прийти к реализации твоего запроса.\n\n' \
                  '<i>Если ты на них отвечаешь, я высылаю тебе сообщение с ссылкой на тренировку-практику. ' \
                  'Если нет — не высылаю. Все максимально просто.</i>\n\n' \
                  '3️⃣ После тренировки попрошу тебя оценить, как ты себя чувствуешь.\n' \
                  'И у тебя будет возможность поделиться обратной связью, если захочешь.\n\n' \
                  '4️⃣ Перед сном предложу выполнить вечернюю практику, которая позволяет перепрошить мышление, ' \
                  'снизить уровнь обесценивания,убрать  внутреннего критика и синдром самозванца.\n\n' \
                  '<i>Ее делаем по желанию.</i>\n\n' \
                  '5️⃣Чтобы попасть на онлайн-разбор с практикой (который проходит раз в неделю) я попрошу заполнить ' \
                  'перечень открытых вопросов, которые помогут нам зафиксировать динамику изменений, твое состояние. ' \
                  'Мы увидим паттерны, отнимающие энергию. И четко сформулируем твой запрос на разбор.\n\n' \
                  '6️⃣Мы сделали удобное меню. В нем ты найдешь дополнительные материалы, расписание, ' \
                  'кнопку связи с саппортом и записи тренировок.\n\n' \
                  '<b>Такая методология позволит нам встроить веллнесс-привычки в жизнь мягко, без напряжения и мы получим ' \
                  'качественный результат от веллнесс-коучинга.</b>\n\n' \
                  '<i>Нормально, если ты будешь пропускать занятие, если у тебя что-то не получается. Не волнуйся. ' \
                  'Просто напиши об этом веллнесс-сапорту.</i>\n\n' \
                  '<b><u>Согласен(-на) с тем, что я выше проговорил?</u></b>'
    instruction_before = 'Держи видео-инструкцию от Тимура о том, как проходят тренировки-практики'
    instruction_after = '.\n\nПодготовь, пожалуйста, к тренировке:\n' \
                        '— <b>коврик</b> (его можно заменить пледом)\n' \
                        '— <b>подушку</b> (можно декоративную)\n' \
                        '— <b>стакан воды</b>\n' \
                        '— и <b>удобную одежду</b>, которая не стесняет движения\n\n' \
                        '<i>Будет круто, если у тебя получится создать пространство, где ты сможешь позаниматься в одиночестве. ' \
                        'Чтобы максимально сфокусироваться на процессе. И получить 100 из 100 пользы от тренировки-практики.</i>'
