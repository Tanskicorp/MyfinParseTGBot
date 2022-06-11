# MyfinParseTGBot
 Бот для парсинга курса криптовалюты сайта myfin

Бот основан на библиотеке aiogram, использует базу данных sql для хранения информации подписок пользователей, а для парсинга модуль requests и bs4.

1. Бот присылает средний курс криптовалюты после использования комманды /crypt ссылка*
2. Бот предлагает прислать информацию отдельно по каждой бирже, а также подписаться на валюту
(при подписке бот будет присылать каждых 5 минут (можно изменить при желании) средний курс валюты)
3. Также у бота есть меню вызываемое по комманде /menu с кнопками "Подписки" - 3.1, "Отписаться" - 3.2, "Выйти" - 3.3

3.1 Высылает список подписок пользователя

3.2 После нажатия под выдаст список подписок. Далее пользователь из списка должен ввести через пробел валюту от которой хочет отписаться, или ввести /cancel если он передумал

3.3 Удаляет сообщение с кнопками
***
# MyfinParseTGBot
Bot for parsing the cryptocurrency rate of the site myfin

The bot is based on the aiogram library, uses a sql database to store user subscription information, and for parsing, the requests and bs4 module.

1. The bot sends the average cryptocurrency rate after using the /crypt link* command
2. The bot offers to send information separately for each exchange, as well as subscribe to the currency
(when subscribing, the bot will send every 5 minutes (can be changed if desired) the average exchange rate)
3. The bot also has a menu called by the /menu command with the buttons "Subscriptions" - 3.1, "Unsubscribe" - 3.2, "Exit" - 3.3

3.1 Sends a list of user's subscriptions

3.2 After clicking under, it will display a list of subscriptions. Next, the user from the list must enter the currency from which he wants to unsubscribe, separated by a space, or enter / cancel if he changes his mind

3.3 Delete message with buttons
