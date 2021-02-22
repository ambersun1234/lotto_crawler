# lotto_crawler
crawler to get lotto history data([台灣彩券](https://www.taiwanlottery.com.tw/header.asp#))

## Disclaimer
+ This repository is only for educational usage, any illegal operation belongs to one's behavior
+ Author doesn't bear any legal responsibility

## Basics
+ This project support crawling `威力彩`, `大樂透`, `今彩539`, `雙贏彩`, `三星彩`, `四星彩`, `38樂合彩`, `49樂合彩`, `39樂合彩`
+ Crawler will fetch all history data starting from year `2014(103)`
+ All the data will be store with `history/LOTTERY_TYPE.csv`

## Prerequisites
```=1
make install
source ./env/bin/activate
make package
```

## Clone repo
```=1
git clone https://github.com/ambersun1234/lotto_crawler.git
```

## Run
```=1
python3 main.py
```

## License
+ This project is licensed under MIT license - see the [MIT License](./LICENSE) file for detail
