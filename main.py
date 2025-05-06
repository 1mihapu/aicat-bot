import telebot
import random
import os
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

user_balances = {}
user_stats = {}  # Формат: {user_id: {"level": 1, "xp": 0}}

# Ваш токен от BotFather сюда:
TOKEN = '7613886086:AAH0cAW5ADaFpFwSrFdQVpvLKEYJ-oXy8fo'

bot = telebot.TeleBot(TOKEN)

# Список мемов и фраз кота
memes = [
    "Meow! I'm feeling awesome today!", "Who's the best cat? AICAT is!",
    "Purr... Feed me memes and tokens!",
    "I hid 10 tokens under your keyboard... just kidding.",
    "Chase the dream... or the red dot.",
    "I opened a capsule and found another capsule inside!"
]

# Состояния настроения
moods = ["Happy", "Angry", "Sleepy", "Curious", "Hungry"]
current_mood = {"state": random.choice(moods)}


# Получить или создать данные пользователя
def get_user_stats(user_id):
    if user_id not in user_stats:
        user_stats[user_id] = {"level": 1, "xp": 0}
    return user_stats[user_id]


# Добавить опыт и проверить повышение уровня
def add_experience(user_id, amount):
    stats = get_user_stats(user_id)
    stats["xp"] += amount
    level_up_threshold = stats["level"] * 100
    if stats["xp"] >= level_up_threshold:
        stats["xp"] -= level_up_threshold
        stats["level"] += 1
        return True
    return False


def calculate_reward(base_reward, level):
    multiplier = 1 + (level * 0.05)
    return int(base_reward * multiplier)


from telebot import types

@bot.message_handler(commands=['start'])
def start(message):
    try:
        print(f"User {message.from_user.id} started the bot")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            types.KeyboardButton('🎁 /capsule'),
            types.KeyboardButton('🐾 /pet'),
            types.KeyboardButton('😺 /mood'),
            types.KeyboardButton('🎤 /meow'),
            types.KeyboardButton('💰 /balance'),
            types.KeyboardButton('🎯 /bonus'),
            types.KeyboardButton('🛍️ /shop'),
            types.KeyboardButton('📊 /stats'),
            types.KeyboardButton('📆 /daily'),
            types.KeyboardButton('ℹ️ /help'),
        )

        user_id = message.from_user.id
        if user_id not in user_balances:
            user_balances[user_id] = 100
            user_stats[user_id] = {"level": 1, "xp": 0}

        bot.send_message(
            message.chat.id,
            "Meow! Welcome to the AICAT world!\n\nHere’s what you can do:\n"
            "🎁 /capsule – Open a surprise capsule!\n"
            "🐾 /pet – Pet the cat and earn rewards!\n"
            "😺 /mood – Check the cat’s mood.\n"
            "🎤 /meow – Hear what the cat has to say.\n"
            "💰 /balance – Check your token balance.\n"
            "🎯 /bonus – Try to catch a flying token.\n"
            "🛍️ /shop – Buy items for the cat.\n"
            "📊 /stats – View your XP and level.\n"
            "📆 /daily – Claim your daily reward.\n"
            "ℹ️ /help – Show this help menu anytime.",
            reply_markup=markup
        )
    except Exception as e:
        print(f"⚠️ Error in /start: {e}")

# 🎯 Универсальный обработчик команд с эмодзи
@bot.message_handler(func=lambda message: message.text and '/' in message.text)
def handle_emoji_command(message):
    clean_text = message.text.split()[-1]  # Получаем только /команду без эмодзи
    bot.process_new_messages([types.Message(
        message_id=message.message_id,
        from_user=message.from_user,
        chat=message.chat,
        date=message.date,
        content_type='text',
        options={},
        json_string='',
        text=clean_text
    )])


@bot.message_handler(commands=['help'])
def help_command(message):
    try:
        print(f"User {message.from_user.id} used /help")
        help_text = ("Meow! Welcome to the AICAT world!\n\n"
                     "Here’s what you can do:\n"
                     "🎁 /capsule – Open a surprise capsule!\n"
                     "🐾 /pet – Pet the cat and earn rewards!\n"
                     "😺 /mood – Check the cat’s mood.\n"
                     "🗯️ /meow – Hear what the cat has to say.\n"
                     "💰 /balance – Check your token balance.\n"
                     "🎯 /bonus – Try to catch a flying token.\n"
                     "🛍️ /shop – Buy items for the cat.\n"
                     "📊 /stats – View your XP and level.\n"
                     "📅 /daily – Claim your daily reward!")
        bot.reply_to(message, help_text)
    except Exception as e:
        print(f"⚠️ Error in /help: {e}")


# Команда настроения
@bot.message_handler(commands=['mood'])
def mood(message):
    try:
        user_id = message.from_user.id
        print(f"User {message.from_user.id} used /mood")
        stats = get_user_stats(user_id)
        add_experience(user_id, 4)  # +4 XP за просмотр настроения
        mood = current_mood['state']

        text = (f"The cat is currently: {mood}\n"
                f"Level: {stats['level']} | XP: {stats['xp']}")

        bot.reply_to(message, text)

    except Exception as e:
        print(f"⚠️ Error in /mood command: {e}")


# Команда daily
@bot.message_handler(commands=['daily'])
def daily(message):
    try:
        user_id = message.from_user.id
        print(f"User {message.from_user.id} used /daily")
        now = time.time()
        last_claim = last_daily_claim.get(user_id, 0)
        cooldown = 86400  # 24 часа в секундах

        if now - last_claim >= cooldown:
            stats = get_user_stats(user_id)
            leveled_up = add_experience(user_id, 15)
            reward = calculate_reward(100, stats["level"])
            user_balances[user_id] = user_balances.get(user_id, 0) + reward
            last_daily_claim[user_id] = now

            text = f"You claimed your daily reward: +{reward} AICAT tokens!\nLevel: {stats['level']} | XP: {stats['xp']}"
            if leveled_up:
                text += "\nMeow! You leveled up!"
        else:
            remaining = int(cooldown - (now - last_claim))
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            text = f"You already claimed your daily reward. Try again in {hours}h {minutes}m."

        bot.reply_to(message, text)
    except Exception as e:
        print(f"⚠️ Error in /daily command: {e}")


# Команда meow
@bot.message_handler(commands=['meow'])
def meow(message):
    try:
        user_id = message.from_user.id
        print(f"User {message.from_user.id} used /meow")
        stats = get_user_stats(user_id)
        leveled_up = add_experience(user_id, 3)  # +3 XP за мяуканье

        meme = random.choice(memes)
        text = f"{meme}\nLevel: {stats['level']} | XP: {stats['xp']}"
        if leveled_up:
            text += "\nMeow! You leveled up!"

        bot.reply_to(message, text)

    except Exception as e:
        print(f"⚠️ Error in /meow command: {e}")


# Команда для просмотра баланса
@bot.message_handler(commands=['balance'])
def balance(message):
    try:
        user_id = message.from_user.id
        print(f"User {message.from_user.id} used /balance")
        balance = user_balances.get(user_id, 0)
        bot.reply_to(message,
                     f"Your current AICAT balance is: {balance} tokens!")
    except Exception as e:
        print(f"⚠️ Error in /balance command: {e}")


# Команда статистики игрока
@bot.message_handler(commands=['stats'])
def stats(message):
    try:
        user_id = message.from_user.id
        print(f"User {message.from_user.id} used /stats")
        stats = get_user_stats(user_id)
        level = stats['level']
        xp = stats['xp']
        xp_to_next = level * 100 - xp

        bot.reply_to(
            message,
            f"Your current level: {level}\nXP: {xp} / {level * 100}\nTo next level: {xp_to_next} XP"
        )
    except Exception as e:
        print(f"⚠️ Error in /stats: {e}")


# Команда бонус
@bot.message_handler(commands=['bonus'])
def bonus(message):
    try:
        user_id = message.from_user.id
        print(f"User {message.from_user.id} used /bonus")
        stats = get_user_stats(user_id)
        add_experience(user_id, 6)  # +6 XP за бонус
        bonus_chance = random.randint(1, 100)

        if bonus_chance <= 70:
            base_reward = random.randint(1, 10)
            reward = calculate_reward(base_reward, stats["level"])
            user_balances[user_id] = user_balances.get(user_id, 0) + reward
            bot.reply_to(
                message,
                f"You caught {reward} AICAT tokens! Meow!\nLevel: {stats['level']} | XP: {stats['xp']}"
            )
        else:
            bot.reply_to(
                message, "Oops! The bonus slipped away... Try again later!\n"
                f"Level: {stats['level']} | XP: {stats['xp']}")
    except Exception as e:
        print(f"⚠️ Error in /bonus command: {e}")


# Команда капсулы
@bot.message_handler(commands=['capsule'])
def capsule(message):
    try:
        user_id = message.from_user.id
        print(f"User {message.from_user.id} used /capsule")
        stats = get_user_stats(user_id)
        leveled_up = add_experience(user_id, 10)  # +10 XP за открытие капсулы

        reward_chance = random.randint(1, 100)

        if user_id not in user_balances:
            user_balances[user_id] = 0

        if reward_chance <= 65:
            base_reward = random.randint(1, 50)
            reward = calculate_reward(base_reward, stats["level"])
            user_balances[user_id] += reward
            message_text = f"You opened a capsule and found {reward} AICAT tokens!"
        elif reward_chance <= 85:
            message_text = "You opened the capsule... but it was full of air! Better luck next time."
        elif reward_chance <= 95:
            message_text = "You opened the capsule and found... a rubber duck. No tokens this time!"
        else:
            message_text = "You opened a glowing capsule and heard a mysterious sound... but found nothing."

        text = f"{message_text}\nLevel: {stats['level']} | XP: {stats['xp']}"
        if leveled_up:
            text += "\nMeow! You leveled up!"

        bot.reply_to(message, text)

    except Exception as e:
        print(f"❌ Error in /capsule: {e}")
        bot.reply_to(
            message,
            "An error occurred while opening the capsule. Try again later.")


# Команда погладить кота
@bot.message_handler(commands=['pet'])
def pet(message):
    try:
        user_id = message.from_user.id
        print(f"User {message.from_user.id} used /pet")
        luck = random.randint(1, 100)

        stats = get_user_stats(user_id)
        leveled_up = add_experience(user_id, 10)  # +10 XP за поглаживание

        if luck <= 5:
            reward = calculate_reward(10, stats["level"])
            user_balances[user_id] += reward
            bot.reply_to(
                message,
                f"Incredible! You received a MEGA blessing: +100 Happiness points and {reward} bonus AICAT tokens!\nLevel: {stats['level']} | XP: {stats['xp']}"
            )
        elif luck <= 20:
            reward = calculate_reward(5, stats["level"])
            user_balances[user_id] += reward
            bot.reply_to(
                message,
                f"You received a blessing: +50 Happiness points and {reward} bonus AICAT tokens!\nLevel: {stats['level']} | XP: {stats['xp']}"
            )
        else:
            bless = random.choice([
                "You earned +5 Happiness points!",
                "You earned +10 Happiness points!",
                "You earned +15 Happiness points!",
                "You earned +20 Happiness points!",
                "You earned +30 Happiness points!",
            ])
            text = f"Purr... {bless}\nLevel: {stats['level']} | XP: {stats['xp']}"
            if leveled_up:
                text += "\nMeow! You leveled up!"
            bot.reply_to(message, text)

    except Exception as e:
        print(f"⚠️ Error in /pet command: {e}")


# Команда магазин
@bot.message_handler(commands=['shop'])
def shop(message):
    try:
        print(f"User {message.from_user.id} used /shop")
        shop_text = "Welcome to the AICAT Shop! Choose an item to buy:\n\n"
        items = {
            1: "Catnip Toy - 50 AICAT",
            2: "Scratching Post - 100 AICAT",
            3: "Royal Cat Throne - 500 AICAT",
            4: "Fish - 50 AICAT",
            5: "Meat - 100 AICAT",
            6: "Shrimp - 200 AICAT",
            7: "Catnip (Valeriana) - 150 AICAT"
        }

        markup = InlineKeyboardMarkup()
        for num, label in items.items():
            shop_text += f"{num}. {label}\n"
            markup.add(
                InlineKeyboardButton(text=f"Buy {label.split('-')[0].strip()}",
                                     callback_data=f"buy_{num}"))

        bot.send_message(message.chat.id, shop_text, reply_markup=markup)
    except Exception as e:
        print(f"⚠️ Error in /shop command: {e}")


# Команда покупки товара
@bot.message_handler(commands=['buy'])
def buy(message):
    try:
        user_id = message.from_user.id
        print(f"User {user_id} used /buy")
        stats = get_user_stats(user_id)
        add_experience(user_id, 8)
        balance = user_balances.get(user_id, 0)

        parts = message.text.split()
        if len(parts) != 2 or not parts[1].isdigit():
            bot.reply_to(message, "Please use the correct format: /buy 1")
            return
        item_number = int(parts[1])

        items = {
            1: ("Catnip Toy", 50),
            2: ("Scratching Post", 100),
            3: ("Royal Cat Throne", 500),
            4: ("Fish", 50),
            5: ("Meat", 100),
            6: ("Shrimp", 200),
            7: ("Catnip (Valeriana)", 150)
        }

        if item_number not in items:
            bot.reply_to(
                message,
                "Invalid item number. Please choose a valid item from the shop."
            )
            return

        item_name, price = items[item_number]
        if balance >= price:
            user_balances[user_id] = balance - price

            if item_number == 4:  # Fish
                reward = calculate_reward(10, stats["level"])
                user_balances[user_id] += reward
                message_text = f"You bought {item_name} and gained +{reward} AICAT tokens! New balance: {user_balances[user_id]}"
            elif item_number == 5:  # Meat
                reward = calculate_reward(20, stats["level"])
                user_balances[user_id] += reward
                message_text = f"You bought {item_name} and gained +{reward} AICAT tokens! New balance: {user_balances[user_id]}"
            elif item_number == 6:  # Shrimp
                reward = calculate_reward(50, stats["level"])
                user_balances[user_id] += reward
                message_text = f"You bought {item_name} and gained +{reward} AICAT tokens! New balance: {user_balances[user_id]}"
            elif item_number == 7:  # Valeriana
                effect = random.choice(["good", "bad", "nothing"])
                if effect == "good":
                    bonus = calculate_reward(100, stats["level"])
                    user_balances[user_id] += bonus
                    message_text = f"The valerian made the cat VERY happy! +{bonus} AICAT tokens! New balance: {user_balances[user_id]}"
                elif effect == "bad":
                    penalty = 50
                    user_balances[user_id] = max(
                        user_balances[user_id] - penalty, 0)
                    message_text = f"The valerian made the cat angry! -{penalty} AICAT tokens! New balance: {user_balances[user_id]}"
                else:
                    message_text = "The valerian had no effect. Cat is sleeping peacefully..."
            else:
                message_text = f"Congratulations! You bought {item_name}. New balance: {user_balances[user_id]} AICAT tokens."
        else:
            message_text = "Not enough AICAT tokens to buy this item. Keep playing to earn more!"

        bot.reply_to(message, message_text)

    except Exception as e:
        print(f"⚠️ Error in /buy command: {e}")
        bot.reply_to(message, "An error occurred. Please try again later.")


# Обработка кнопок покупки
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def handle_buy_callback(call):
    print("Callback triggered:", call.data)

    try:
        print(f"User {call.from_user.id} clicked button {call.data}")
        item_number = int(call.data.split('_')[1])
        user_id = call.from_user.id
        stats = get_user_stats(user_id)
        add_experience(user_id, 8)
        balance = user_balances.get(user_id, 0)

        items = {
            1: ("Catnip Toy", 50),
            2: ("Scratching Post", 100),
            3: ("Royal Cat Throne", 500),
            4: ("Fish", 50),
            5: ("Meat", 100),
            6: ("Shrimp", 200),
            7: ("Catnip (Valeriana)", 150)
        }

        if item_number not in items:
            bot.answer_callback_query(call.id, "Invalid item.")
            return

        item_name, price = items[item_number]
        if balance >= price:
            user_balances[user_id] = balance - price

            if item_number == 4:
                reward = calculate_reward(10, stats["level"])
                user_balances[user_id] += reward
                message = f"You bought {item_name} and gained +{reward} AICAT tokens! New balance: {user_balances[user_id]}"
            elif item_number == 5:
                reward = calculate_reward(20, stats["level"])
                user_balances[user_id] += reward
                message = f"You bought {item_name} and gained +{reward} AICAT tokens! New balance: {user_balances[user_id]}"
            elif item_number == 6:
                reward = calculate_reward(50, stats["level"])
                user_balances[user_id] += reward
                message = f"You bought {item_name} and gained +{reward} AICAT tokens! New balance: {user_balances[user_id]}"
            elif item_number == 7:
                effect = random.choice(["good", "bad", "nothing"])
                if effect == "good":
                    bonus = calculate_reward(100, stats["level"])
                    user_balances[user_id] += bonus
                    message = f"The valerian made the cat VERY happy! +{bonus} AICAT tokens! New balance: {user_balances[user_id]}"
                elif effect == "bad":
                    penalty = 50
                    user_balances[user_id] = max(user_balances[user_id] - penalty, 0)
                    message = f"The valerian made the cat angry! -{penalty} AICAT tokens! New balance: {user_balances[user_id]}"
                else:
                    message = "The valerian had no effect. Cat is sleeping peacefully..."
            else:
                message = f"Congratulations! You bought {item_name}. New balance: {user_balances[user_id]} AICAT tokens."
        else:
            message = "Not enough AICAT tokens to buy this item. Keep playing to earn more!"

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, message)

    except Exception as e:
        print(f"⚠️ Error in handle_buy_callback: {e}")
        bot.answer_callback_query(call.id, "Oops! Something went wrong.")


if __name__ == "__main__":
    bot.infinity_polling()

