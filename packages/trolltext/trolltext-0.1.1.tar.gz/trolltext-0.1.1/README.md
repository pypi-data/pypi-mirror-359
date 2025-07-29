pip install trolltext
 

Импортируйте нужные функции:
 

from trolltext import style\_text, allfont
 

Создайте переменную с текстом:
 

text = "Hello world!"
 

Преобразуйте текст в выбранный стиль (например, жирный):
 

bold\_text = style\_text(text, "bold")
 
print(bold\_text)
 

Выведите текст во всех доступных стилях:
 

print(allfont(text))
 

Доступные стили для параметра font в функции style\_text:
 

double\_struck, bold, italic, bold\_italic, script, fraktur, bold\_script, bold\_fraktur, monospace, circled
 

Если передать несуществующий стиль, библиотека выдаст ошибку:
 

style\_text("Hello", "unknown\_font") # ValueError: Шрифт 'unknown\_font' не найден.
 

Если у вас есть идеи или нашли баги — создайте issue или pull request в репозитории.
 

Лицензия: MIT © Ваше Имя
 

Спасибо за использование TrollText!