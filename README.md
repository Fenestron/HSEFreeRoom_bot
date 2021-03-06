# <p align="center"> HSE Free Room bot

[HSEFreeRoom](https://telegram.me/HSEFreeRoom_bot) - Телеграм-бот для поиска свободных аудиторий в корпусах НИУ ВШЭ.

В данный момент доступны аудитории для всех рабочих корпусов в Москве.

## Использование

Для того, чтобы бот заработал, нужно выполнить следующие действия: 

Для начала нужно настроить все необходимые компоненты для запуска. 
Для этого достаточно запустить bash-script `setup.sh`. 
ВАЖНО: Обратите особое внимание на генерацию серитефиката. В консоле будет выведено сообщение-подсказка, что нужно сделать. 
Вам необходимо ввести свой внешний ip-адрес в поле _Common Name_ при генерации.
```
$ bash setup.sh
```

Далее необходимо вставить свои данные (токен бота, адрес сервера) в файл `config.py`.

Чтобы включить бота, запустите `run.sh`
```
$ bash run.sh
```

После выполнения этой команды бот будет запущен.

Чтобы выключить бота, воспользуйтесь скриптом `stop.sh` (или `restart.sh` для перезагрузки)

Для того, чтобы спользовать бота в _Long poll_ режиме, запустите файл `main.py`
```
$ python3 main.py
```


Этот проект можно использовать как шаблон для любого Телеграм-бота. Достаточно просто заменить все обработчики в файле `message_handlers.py` на свои.

