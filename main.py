from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pymongo import MongoClient
from random import randint
from bson.objectid import ObjectId
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

TOKEN = '6878388643:AAHoB6rwcMCVJeHgY1t17IV1D53p7VISJ30'
BOT_USERNAME = '@savy2033Bot_bot'
client = MongoClient("localhost", 27017)
db = client.neuraldb
dquests = db.ql
wquests = db.wq
people = db.people
d  = ["login", "commands", "messages"]
dW = {"login": 1, "messages": 2, "commands": 2}
dD = {"login": "You need to use /login command", "messages": "You need to send required amount of messages", "commands": "You need to use required amount of commands"}

#СОЗДАНИЕ КВЕСТОВ
async def generate_daily_quest(update:Update, context: ContextTypes.DEFAULT_TYPE):
    task = randint(0, len(d) - 1)
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    user = check[0]
    qu = user.get("dailyQ")
    while d[task] in qu.keys():
        task = randint(1, len(d) - 1)
    print(f'Now task is {d[task]}')
    dqp = user.get("dailyQuestsProgress")
    mp = randint(dqp[d[task]] + 1,dqp[d[task]] + 10)
    cd = datetime.now()
    if d[task] == "login":
        quest_id = dquests.insert_one({"name": d[task], "description": dD[d[task]], "type": 1, "max_progress": 1, "current_progress": 0, "completed": False, "year" : cd.year, "month": cd.month, "day" : cd.day, "passed": 0}).inserted_id
        qu["login"] = quest_id
        people.update_one({"tgid": update.message.chat.id}, {"$set": {"dailyQ": qu}})
        print(dquests.find_one({"_id": ObjectId(quest_id)}))
    else:
        quest_id = dquests.insert_one({"name": d[task], "description": dD[d[task]], "type": 1, "max_progress": mp, "current_progress": 0, "completed": False, "year" : cd.year, "month": cd.month, "day" : cd.day, "passed": 0}).inserted_id
        qu[d[task]] = quest_id
        people.update_one({"tgid": update.message.chat.id}, {"$set": {"dailyQ": qu}})
        print(dquests.find_one({"_id": ObjectId(quest_id)}))
async def generate_weekly_quest(update:Update, context: ContextTypes.DEFAULT_TYPE):
    task = randint(0, len(d) - 1)
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    user = check[0]
    qu = user.get("weeklyQ")
    while d[task] in qu.keys():
        task = randint(1, len(d) - 1)
    print(f'Now task is {d[task]}')
    dqp = user.get("weeklyQuestsProgress")
    mp = randint(dqp[d[task]] + 1 * 7,dqp[d[task]] + 10 * 7)
    cd = datetime.now()
    if d[task] == "login":
        quest_id = wquests.insert_one({"name": d[task], "description": dD[d[task]], "type": 7, "max_progress": 1, "current_progress": 0, "completed": False, "year": cd.year, "month": cd.month ,"day" : cd.day, "passed": 0}).inserted_id
        qu["login"] = quest_id
        people.update_one({"tgid": update.message.chat.id}, {"$set": {"weeklyQ": qu}})
        print(wquests.find_one({"_id": ObjectId(quest_id)}))
    else:
        quest_id = wquests.insert_one({"name": d[task], "description": dD[d[task]], "type": 7, "max_progress": mp, "current_progress": 0, "completed": False, "year": cd.year, "month": cd.month ,"day" : cd.day, "passed": 0}).inserted_id
        qu[d[task]] = quest_id
        people.update_one({"tgid": update.message.chat.id}, {"$set": {"weeklyQ": qu}})
        print(wquests.find_one({"_id": ObjectId(quest_id)}))

#ПРОВЕРКА КВЕСТОВ НА СРОКИ
async def check_daily_quest_time(update:Update, context: ContextTypes.DEFAULT_TYPE, name: str):
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    user = check[0]
    qu = user.get("dailyQ")
    qid = qu[name]
    check2 = [q for q in dquests.find({"_id": ObjectId(qid)})]
    quest = check2[0]
    cd = datetime.now()
    if (quest["year"]!= cd.year) or (quest["month"]!= cd.month) or (quest["day"]!= cd.day):
        for a in qu.keys():
            dquests.delete_one({"_id": ObjectId(qu[a])})
        people.update_one({"tgid": update.message.chat.id}, {"$set": {"dailyQ": {}}})
        for i in range(0,2):
            await generate_daily_quest(update, context)
        print(f'Quests changed')
        await context.bot.send_message(update.message.chat.id, "Daily quests changed")
async def check_weekly_quest_time(update:Update, context: ContextTypes.DEFAULT_TYPE, name: str):
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    user = check[0]
    qu = user.get("weeklyQ")
    qid = qu[name]
    check2 = [q for q in wquests.find({"_id": ObjectId(qid)})]
    quest = check2[0]
    cd = datetime.now()
    if quest["passed"] > 7:
        for a in qu.keys():
            wquests.delete_one({"_id": ObjectId(qu[a])})
        people.update_one({"tgid": update.message.chat.id}, {"$set": {"weeklyQ": {}}})
        for i in range(0, 2):
            await generate_weekly_quest(update, context)
        print(f'Quests changed')
        await context.bot.send_message(update.message.chat.id, "Weekly quests changed")
    elif quest["year"] != cd.year or quest["month"]!= cd.month or quest["day"]!= cd.day:
        quest["passed"] += 1
        wquests.update_one({"_id": ObjectId(qid)}, {"$set": {"passed": quest["passed"]}})
        wquests.update_one({"_id": ObjectId(qid)}, {"$set": {"year": cd.year}})
        wquests.update_one({"_id": ObjectId(qid)}, {"$set": {"month": cd.month}})
        wquests.update_one({"_id": ObjectId(qid)}, {"$set": {"day": cd.day}})

#ОБНОВЛЕНИЕ ПРОГРЕССА КВЕСТОВ
async def update_daily_quest_progress(update:Update, context: ContextTypes.DEFAULT_TYPE, name: str, change: int):
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    user = check[0]
    if check != []:
        qu = user.get("dailyQ")
        qid = qu[name]
        check2 = [q for q in dquests.find({"_id": ObjectId(qid)})]
        quest = check2[0]
        cd = datetime.now()
        if quest["completed"] == False:
            quest["current_progress"] += change
            dquests.update_one({"_id": ObjectId(qid)}, {"$set": {"current_progress": quest["current_progress"]}})
            if quest["day"] == cd.day:
                print(f'Daily quest {name} updated. Current progress is {quest["current_progress"]}')
                await check_daily_quest_progress(update, context, name)
            else:
                await check_daily_quest_time(update, context, name)
        else:
            await check_daily_quest_time(update, context, name)
async def update_weekly_quest_progress(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str, change: int):
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    if check!= []:
        user = check[0]
        await check_weekly_quest_time(update, context, name)
        qu = user.get("weeklyQ")
        if name in qu.keys():
            qid = qu[name]
            check2 = [q for q in wquests.find({"_id": ObjectId(qid)})]
            quest = check2[0]
            cd = datetime.now()
            if not(quest["completed"]):
                quest["current_progress"] += change
                wquests.update_one({"_id": ObjectId(qid)}, {"$set": {"current_progress": quest["current_progress"]}})
                print(f'Weekly quest {name} updated. Current progress is {quest["current_progress"]}')
                await check_weekly_quest_progress(update, context, name)
        else:
            pass
    else:
        await context.bot.send_message(update.message.chat.id, "You need to create an account first.\nPlease use command /start to create account")
    pass

#ПРОВЕРКА КВЕСТОВ НА ВЫПОЛНЕНИЕ
async def check_daily_quest_progress(update:Update, context: ContextTypes.DEFAULT_TYPE, name: str):
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    user = check[0]
    qu = user.get("dailyQ")
    qid = qu[name]
    check2 = [q for q in dquests.find({"_id": ObjectId(qid)})]
    quest = check2[0]
    if quest["current_progress"] >= quest["max_progress"]:
        if quest["completed"] == False:
            xp = quest["max_progress"] * quest["type"] * dW[quest["name"]] + user["xp"]
            dqp = user.get("dailyQuestsProgress")
            dqp[name] = quest["max_progress"]
            dquests.update_one({"_id": ObjectId(qid)}, {"$set": {"completed": True}})
            people.update_one({"tgid": update.message.chat.id}, {"$set": {"xp": xp}})
            people.update_one({"tgid": update.message.chat.id}, {"$set": {"dailyQuestsProgress": dqp}})
            print(f'Daily quest {name} completed. Earned {xp} XP')
            await context.bot.send_message(update.message.chat.id, f'Daily quest {name} completed. Earned {xp} XP')
async def check_weekly_quest_progress(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str):
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    user = check[0]
    qu = user.get("weeklyQ")
    qid = qu[name]
    check2 = [q for q in wquests.find({"_id": ObjectId(qid)})]
    quest = check2[0]
    if quest["current_progress"] >= quest["max_progress"]:
        if quest["completed"] == False:
            xp = quest["max_progress"] * quest["type"] * dW[quest["name"]] + user["xp"]
            dqp = user.get("weeklyQuestsProgress")
            dqp[name] = quest["max_progress"]
            wquests.update_one({"_id": ObjectId(qid)}, {"$set": {"completed": True}})
            people.update_one({"tgid": update.message.chat.id}, {"$set": {"xp": xp}})
            people.update_one({"tgid": update.message.chat.id}, {"$set": {"weeklyQuestsProgress": dqp}})
            print(f'Weekly quest {name} completed. Earned {xp} XP')
            await context.bot.send_message(update.message.chat.id, f'Weekly quest {name} completed. Earned {xp} XP')

#КОМАНДА ДЛЯ НАЧАЛА РАБОТЫ С БОТОМ
async def start(update:Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    if check == []:
        people.insert_one({"tgid": update.message.chat.id, "dailyQ": {}, "weeklyQ": {}, "xp": 0, "dailyQuestsProgress":{}, "weeklyQuestsProgress": {}})
        print("Created one")
        dqt = {}
        wqt = {}
        for t in d:
            dqt[t] = 0
            wqt[t] = 0
        people.update_one({"tgid": update.message.chat.id}, {"$set": {"dailyQuestsProgress": dqt}})
        people.update_one({"tgid": update.message.chat.id}, {"$set": {"weeklyQuestsProgress": wqt}})
        for i in range(0,2):
            await generate_daily_quest(update, context)
            await generate_weekly_quest(update, context)
        print('Quest created')
    else:
        user = check[0]
        dq = user.get("dailyQ")
        for a in dq.keys():
            await check_daily_quest_time(update, context, a)
        dq = user.get("dailyQ")
        wq = user.get("weeklyQ")
        for b in wq.keys():
            await check_weekly_quest_time(update, context, b)
        wq = user.get("weeklyQ")
        if "commands" in check[0].get("dailyQ").keys():
            await update_daily_quest_progress(update, context, "commands", 1)
        if "commands" in check[0].get("weeklyQ").keys():
            await update_weekly_quest_progress(update, context, "commands", 1)
        print("Already exists")
    await context.bot.send_message(chat_id, "Hello!")
    await context.bot.send_message(chat_id, "How are you?")
    print('=' * 50)

#КОМАНДА ДЛЯ ВЫПОЛНЕНИЯ ЗАДАНИЯ НА ЛОГИН
async def login_check(update:Update, context: ContextTypes.DEFAULT_TYPE):
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    if check != []:
        user = check[0]
        if "login" in user.get("dailyQ").keys():
            await update_daily_quest_progress(update, context, "login", 1)
            await check_daily_quest_progress(update, context, "login")
        else:
            await context.bot.send_message(update.message.chat.id, "You have no login quest today")
        if "login" in user.get("weeklyQ").keys():
            await update_weekly_quest_progress(update, context, "login", 1)
            await check_weekly_quest_progress(update, context, "login")
            pass
        else:
            await context.bot.send_message(update.message.chat.id, "You have no login quest this week")
        if "commands" in user.get("dailyQ").keys():
            await update_daily_quest_progress(update, context, "commands", 1)
            await check_daily_quest_progress(update, context, "commands")
        if "commands" in user.get("weeklyQ").keys():
            await update_daily_quest_progress(update, context, "commands", 1)
            await check_daily_quest_progress(update, context, "commands")
    else:
        await context.bot.send_message(update.message.chat.id, "You have no account. Please use command /start to create one")

#КОМАНДА ДЛЯ ВЫВОДА ИНФОРМАЦИИ О ПОЛЬЗОВАТЕЛЕ
async def status(update:Update, context: ContextTypes.DEFAULT_TYPE):
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    if check!= []:
        user = check[0]
        dq = user.get("dailyQ")
        for a in dq.keys():
            await check_daily_quest_time(update, context, a)
        dq = user.get("dailyQ")
        daily_count = len(dq.keys())
        wq = user.get("weeklyQ")
        for b in wq.keys():
            await check_weekly_quest_time(update, context, b)
        wq = user.get("weeklyQ")
        weekly_count = len(wq.keys())
        if "commands" in check[0].get("dailyQ").keys():
            await update_daily_quest_progress(update, context, "commands", 1)
        if "commands" in check[0].get("weeklyQ").keys():
            await update_weekly_quest_progress(update, context, "commands", 1)
        await context.bot.send_message(update.message.chat.id, f"Your current xp: {user['xp']}\nYou have {daily_count} daily quests.\nYou have {weekly_count} weekly quests")
        pass
    else:
        await context.bot.send_message(update.message.chat.id, "You have no account. Please use command /start to create one")

#КОМАНДА ДЛЯ ВЫВОДА КВЕСТОВ
async def your_quests(update:Update, context: ContextTypes.DEFAULT_TYPE):
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    if check!= []:
        user = check[0]
        dq = user.get("dailyQ")
        for a in dq.keys():
            await check_daily_quest_time(update, context, a)
        dq = user.get("dailyQ")
        dkeys = dq.keys()
        wq = user.get("weeklyQ")
        for b in wq.keys():
            await check_weekly_quest_time(update, context, b)
        wq = user.get("weeklyQ")
        if "commands" in check[0].get("dailyQ").keys():
            await update_daily_quest_progress(update, context, "commands", 1)
        if "commands" in check[0].get("weeklyQ").keys():
            await update_weekly_quest_progress(update, context, "commands", 1)
        wkeys = wq.keys()
        await context.bot.send_message(update.message.chat.id, f"Your daily quests:")
        for name in dkeys:
            check2 = [q for q in dquests.find({"_id": ObjectId(dq[name])})]
            d = check2[0]
            await status_photo(update, context, name, d["description"], d["current_progress"], d["max_progress"], d["type"], d["passed"])
        await context.bot.send_message(update.message.chat.id, "Your weekly quests")
        for name in wkeys:
            check2 = [q for q in wquests.find({"_id": ObjectId(wq[name])})]
            d = check2[0]
            await status_photo(update, context, name, d["description"], d["current_progress"], d["max_progress"], d["type"], d["passed"])
    else:
        await context.bot.send_message(update.message.chat.id, "You have no account. Please use command /start to create one")

#КОММАНДА ДЛЯ ВЫВОДА СПРАВКИ
async def help(update:Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(update.message.chat.id, '/start - use this command to start working with bot\n/status - use this command to check your status\n/quests - use this command to check your quests\n/login - use this command to complete login type quest\n/delete_account - use this command to delete your account (all progress will be lost)')

#КОММАНДА ДЛЯ УДАЛЕНИЯ СВОЕГО АККАУНТА
async def delete_account(update:Update, context: ContextTypes.DEFAULT_TYPE):
    check = [p for p in people.find({"tgid": update.message.chat.id})]
    if check!= []:
        user = check[0]
        dq = user.get("dailyQ")
        wq = user.get("weeklyQ")
        for a in dq.keys():
            dquests.delete_one({"_id": ObjectId(dq[a])})
        for a in wq.keys():
            wquests.delete_one({"_id": ObjectId(wq[a])})
        people.delete_one({"tgid": update.message.chat.id})
        await context.bot.send_message(update.message.chat.id, "Your account has been deleted")
    else:
        await context.bot.send_message(update.message.chat.id, "You have no account. Please use command /start to create one")

#ОБРАБОТКА СООББЩЕНИЙ (НЕ КОМАНД)
async def handle_message(update:Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    check = [p for p in people.find({"tgid": update.message.chat.id})]
    if check != []:
        user = check[0]
        dq = user.get("dailyQ")
        for a in dq.keys():
            await check_daily_quest_time(update, context, a)
        dq = user.get("dailyQ")
        daily_count = len(dq.keys())
        wq = user.get("weeklyQ")
        for b in wq.keys():
            await check_weekly_quest_time(update, context, b)
        wq = user.get("weeklyQ")
        if "messages" in user.get("dailyQ").keys():
            await update_daily_quest_progress(update, context, "messages", 1)
        if "messages" in user.get("weeklyQ").keys():
            await update_weekly_quest_progress(update, context, "messages", 1)

    if BOT_USERNAME in text:
        new_text = text.replace(BOT_USERNAME, "").strip()
        response = handle_response(new_text)
    else:
        response = handle_response(text)

    await context.bot.send_message(update.message.chat.id, response)

#ВЫБОР ОТВЕТА НА СООБЩЕНИЕ
def handle_response(text: str):
    processed = text.lower()
    if 'hello' in processed or 'hi' in processed:
        return 'Hey there!'

    if 'how are you?' in processed:
        return 'I am good!'

    if 'What are you doing?' in processed:
        return 'I am answering you :)'
    return 'I do not understand you :('

#ГЕНЕРАЦИЯ ФОТОГРАФИЙ С ИНФОРМАЦИЕЙ О КВЕСТАХ
async def status_photo(update:Update, context: ContextTypes.DEFAULT_TYPE, name: str, description: str, current_progress: int, max_progress: int, type:int, passed:int):
    new_img = Image.new('RGB', (1040, 300), 'white')
    img_path = 'photo.jpg'
    pencil = ImageDraw.Draw(new_img)
    font = ImageFont.truetype('arial.ttf', 30)
    pencil.text((50, 10), f'Quest name: {name}', font = font, fill = 'black')
    pencil.text((50, 60), f'Quest desription: {description}', font=font, fill='black')
    pencil.text((50, 110), f'Quest progress: {current_progress} out of {max_progress}', font=font, fill='black')
    pencil.text((50, 160), f'Days left: {type - passed}', font=font, fill='black')
    numb = int(((100/max_progress) * current_progress)//10)
    for i in range(1, numb + 1):
        pencil.rectangle((20 + 100 * (i - 1), 210, 100 + 100 * (i - 1), 290), fill='green')
    for i in range(numb + 1, 11):
        pencil.rectangle((20 + 100 * (i - 1), 210, 100 + 100 * (i - 1), 290), fill='red')
    new_img.save(img_path)
    await context.bot.send_photo(update.message.chat.id, open(img_path, 'rb'))

#ДЕБАГ КОММАНДА ДЛЯ ВЫВОДА БАЗЫ ДАННЫХ В КОНСОЛЬ
async def print_data(update:Update, context: ContextTypes.DEFAULT_TYPE):
    print("People")
    for person in people.find():
        print(person)
    print("Daily Quests")
    for q in dquests.find():
        print(q)
    print("Weekly Quests")
    for q in wquests.find():
        print(q)
    print('=' * 50)

#ДЕБАГ КОМАНДА ДЛЯ ПОЛНОГО УДАЛЕНИЯ БАЗЫ ДАННЫХ
async def delete_all(update:Update, context: ContextTypes.DEFAULT_TYPE):
    people.delete_many({})
    dquests.delete_many({})
    wquests.delete_many({})
    print("Deleted")
    print('=' * 50)

if __name__ == '__main__':
    print('Starting bot')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("quests", your_quests))
    app.add_handler(CommandHandler("login", login_check))
    app.add_handler(CommandHandler("delete_account", delete_account))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("print_data", print_data))
    app.add_handler(CommandHandler("delete_all", delete_all))

    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("Polling")
    print('=' * 50)
    app.run_polling(poll_interval = 1)
