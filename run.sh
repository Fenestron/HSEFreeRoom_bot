#!/usr/bin/env bash


if [ "$(wc -l file.pid | awk '{print $1}')" != 0 ]
then
  echo 'Для начала необходимо завершить запущенные процессы!'
  echo '(Используйте ./stop или ./restart)'
  exit
fi


exec &>> ./logs/router.stderr
exec >> ./logs/router.log

python3 router.py &

echo $! > file.pid 


exec &>> ./logs/firstBot.stderr
exec >> ./logs/firstBot.log

python3 firstBot.py &

echo $! >> file.pid
