import sqlite3
import telebot
from telebot import types
from datetime import datetime, date
from time import sleep

def create_db():
    try:
        # подключаем базу данных
        conn = sqlite3.connect('meeting_reminder.db')

        # курсор для работы с таблицами
        cursor = conn.cursor()

        # try:
        #     query = 'DROP TABLE "meeting_reminder"'
        #     cursor.execute(query)
        # except:
        #     pass
        #     raise

        try:
            # sql запрос для создания таблицы
            query = 'CREATE TABLE "meeting_reminder" ("ID" INTEGER UNIQUE, "chat_id" INTEGER, "meet_time" TEXT, "meet_location" TEXT, "meet_name" TEXT, "meet_schedule" TEXT, "meet_text_msg" TEXT, PRIMARY KEY ("ID"))'
            cursor.execute(query)
        except:
            pass
    except:
        pass
    
#--------------------------------------------------------------------    
def dop_meet_add(message, bot):
    print('1------')
    try:
        meet_time = message.text.split(';')[0].strip()
        meet_location = message.text.split(';')[1].strip()
        meet_name = message.text.split(';')[2].strip()
        meet_schedule = message.text.split(';')[3].strip()
        
        #Доп преобразования
        meet_time = '0'+ meet_time if len(meet_time.split(':')[0]) < 2 else meet_time 
        
        if meet_location.startswith('dion'):
            meet_location = meet_location.replace('dion','').strip()
            meet_location = f'https://dion.vc/event/{meet_location}'
            meet_name = f'Встреча "{meet_name}"'
        else:
            meet_name = f'Событие "{meet_name}"'
            
            
        print(meet_time, meet_location, meet_name, meet_schedule )
        
        print('2------')
        with sqlite3.connect('meeting_reminder.db') as con:
            cursor = con.cursor()
            cursor.execute('INSERT INTO meeting_reminder (chat_id, meet_time, meet_location, meet_name, meet_schedule, meet_text_msg) VALUES (?, ?, ?, ?, ?, ?)',
                           (message.chat.id, meet_time, meet_location, meet_name, meet_schedule, message.text.strip()))
            con.commit()
        print('3------')
        text = 'Встреча добавлена в "календарь"'
        bot.send_message(message.chat.id, text, reply_markup=keyboard_start)
    
    except:
        text = 'Строка имеет неверный формат'
        bot.send_message(message.chat.id, text, reply_markup=keyboard_start)
        return None

#--------------------------------------------------------------------
# просто функция, которая делает нам красивые строки для отправки пользователю
def get_meets_string(tasks):
    try:
        print('6------')
        tasks_str = []
        for val in list(enumerate(tasks)): 
            print(f'val = {val}')
            print(val[0])
            print(val[1][0])
            if (val[1][3] == 'every day') \
                or (val[1][3] == 'every day on weekdays' and datetime.today().isocalendar().weekday in (1,2,3,4,5)) \
                or (val[1][3] == 'every monday' and datetime.today().isocalendar().weekday == 1) \
                or (val[1][3] == 'every tuesday' and datetime.today().isocalendar().weekday == 2) \
                or (val[1][3] == 'every wednesday' and datetime.today().isocalendar().weekday == 3) \
                or (val[1][3] == 'every thursday' and datetime.today().isocalendar().weekday == 4) \
                or (val[1][3] == 'every friday' and datetime.today().isocalendar().weekday == 5) \
                or (val[1][3] == 'every saturday' and datetime.today().isocalendar().weekday == 6) \
                or (val[1][3] == 'every sunday' and datetime.today().isocalendar().weekday == 7):
            
                tasks_str.append(f'{val[1][0]};{val[1][1]};{val[1][2]};{val[1][3]}\n')
            elif not(val[1][3].startswith('every')):
                try:
                    if date.fromisoformat(val[1][3]) == date.today():
                        tasks_str.append(f'{val[1][0]} {val[1][1]} {val[1][2]} {val[1][3]}\n')
                except:
                    print('Error get_meets_stringtry fromisoformat')
                    pass
    except:
        print('Error get_meets_string')
        pass
        
    return ''.join(tasks_str)    
                
                
def dop_meet_show(message):
    print('5------')
    with sqlite3.connect('meeting_reminder.db') as con:
        cursor = con.cursor()
        cursor.execute('SELECT meet_time, meet_location, meet_name, meet_schedule, meet_text_msg FROM meeting_reminder WHERE chat_id=={}'.format(message.chat.id))
        tasks = get_meets_string(cursor.fetchall())
    print('7------')    
    bot.send_message(message.chat.id, tasks, reply_markup=keyboard_start)

    
#--------------------------------------------------------------------    
# выделяет одну встречу, которую пользователь хочет удалить
def dop_meet_del(message):
    print('10--------------')
    keyboard_meet_delete = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    with sqlite3.connect('meeting_reminder.db') as con:
        cursor = con.cursor()
        # достаем все встречи 
        cursor.execute("SELECT cast(ID as TEXT) || ') ' || meet_text_msg FROM meeting_reminder WHERE chat_id=={}".format(message.chat.id))
        # достанем результат запроса
        tasks = cursor.fetchall()
        for value in tasks:
            keyboard_meet_delete.add(types.KeyboardButton(value[0]))
            
        msg = bot.send_message(message.chat.id, 'Выбери одну встречу из списка', reply_markup=keyboard_meet_delete)
                                 
        bot.register_next_step_handler(msg, dop_meet_del_)

# удаляет одну встречу
def dop_meet_del_(message):
    try:
        msg_text = int(message.text.split(') ')[0])
        with sqlite3.connect('meeting_reminder.db') as con:
            cursor = con.cursor()
            cursor.execute('DELETE FROM meeting_reminder WHERE chat_id==? AND ID==?', (message.chat.id, msg_text))
            con.commit()
            bot.send_message(message.chat.id, 'Ура, минус одна встреча!', reply_markup=keyboard_start)
    except:
        print('Error dop_meet_del_')
        pass