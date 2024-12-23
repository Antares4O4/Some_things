# Лабораторные работы по курсу "ПАСЗИ"

Данный репозиторий содержит общий список лабораторных работ, которые необходимо выполнить в рамках курса.

## Список лабораторных работ

1. **Реализация hash-функции**  
    Создание хеш-функции в соответствии с индивидуальным вариантом.
    
2. **Реализация электронной цифровой подписи (ЭЦП)**  
    Разработка ЭЦП на основе хеш-функции, созданной в предыдущей лабораторной работе.
    
3. **Реализация программы "Нотариат"**  
    Имитация работы системы нотариального заверения данных.
    
4. **Реализация слепой подписи**  
    Создание системы слепой подписи по заданному варианту.
    
5. **Использование GPG в почтовых клиентах**  
    Настройка и применение GPG для шифрования, подписывания и проверки писем.
    
6. **Имитация атаки "Гроссмейстер"**  
    Реализация модели, демонстрирующей особенности атаки типа "Гроссмейстер".
    
7. **Имитация атаки "Захват канала"**  
    Симуляция атаки, связанной с перехватом и контролем канала связи.
    
8. **Имитация атаки "Расщепление подтверждения"**  
    Моделирование атаки, направленной на рассогласование подтверждающих данных.
    

---

## Примечание

Для успешного завершения курса необходимо выполнить 6 лабораторных работ:

- Обязательные работы: **первые 5 пунктов**.
- Дополнительно: **любую одну работу из пунктов 6, 7, и 8** на ваш выбор.

-----

# MITM Attack Tool (Lab_6)

## Описание
Инструмент для демонстрации атаки "человек посередине" (Man-in-the-Middle, MITM) в локальной сети. Программа позволяет перехватывать незашифрованный HTTP-трафик между целевым устройством и шлюзом.

## Функциональность
- Автоматическое определение сетевого интерфейса
- Определение шлюза по умолчанию
- ARP-спуфинг для перехвата трафика
- Мониторинг HTTP-трафика
- Корректное восстановление сети после завершения

## Требования
- Python 3.x
- Root/Administrator права
- Kali Linux система
- Установленные библиотеки:
  ```bash
  sudo pip3 install scapy
  sudo pip3 install colorama
  sudo pip3 install psutil
  sudo pip3 install netifaces
  ```

## Использование
```bash
sudo python3 mitm.py
```

После запуска:
1. Выберите целевой IP-адрес
2. Дождитесь инициализации и начала перехвата
3. Для остановки нажмите Ctrl+C

## Предупреждение
⚠️ Данный инструмент предназначен только для образовательных целей и тестирования безопасности в собственной сети.

## Ограничения
- Работает только с незашифрованным HTTP-трафиком
- Требуется нахождение в одной сети с целью
- Некоторые системы могут блокировать ARP-спуфинг





