import re # Библиотека для работы с регулярными выражениями
import requests # Библиотека для работы с HTTP запросами
import xlsxwriter # Библиотека для создания Excel файлов
from bs4 import BeautifulSoup # Библиотека для парсинга HTML и XML

#Функция для получения названия техники по ее ID
def get_technique_title(id):
    url = f'https://attack.mitre.org/techniques/{id.replace(".", "/")}'# Формируем URL страницы техники
    response = requests.get(url)# Отправляем запрос и получаем ответ
    soup = BeautifulSoup(response.text, 'html.parser')# Парсим HTML код ответа
    title_element = soup.find('h1', id='') # Ищем заголовок <h1>
    if title_element:# Если заголовок найден
        title_text = title_element.get_text(strip=True) # Получаем текст заголовка
        if ':' in title_text: # Если в тексте есть двоеточие
            title = title_text.split(':', 1)[1].strip()# Разделяем строку по двоеточию и берем вторую часть
        else:
            title = title_text # Иначе весь текст
        return title# Возвращаем название
    else:
        return None# Если заголовок не найден, возвращаем None

#Функция для получения примеров процедур по ID техники
def get_procedure_examples(id):
    url = f'https://attack.mitre.org/techniques/{id.replace(".", "/")}'# Формируем URL
    response = requests.get(url)# Отправляем запрос
    soup = BeautifulSoup(response.text, 'html.parser')# Парсим HTML
    examples = []
    table = soup.select_one('table.table.table-bordered.table-alternate.mt-2')# Ищем нужную таблицу

    if table:  # Проверка, что таблица была найдена
        for row in table.find_all('tr'): # Перебираем строки
            cells = row.find_all('td')# Находим ячейки

            name = ""  # Инициализация переменной name
            description = ""  # Инициализация переменной description

            if len(cells) >= 2:# Если ячеек 2 или больше
                name = cells[1].text.strip()# Записываем текст из 2й ячейки в name

            if len(cells) >= 3:  
                description = cells[2].find('p').text.strip()# Записываем текст из 3й ячейки в description
                # Удаление текста внутри квадратных скобок и самих скобок, затем оставляем только первое предложение
                description = re.sub('\[.*?\]', '', description)#удалит все квадратные скобки и текст внутри них, включая любые символы между ними.

            if name and description:# Если есть name и description
                examples.append(f"{name} - {description}")# Добавляем в список
    else:
        examples.append("Примеры процедур не найдены.")  # Если таблица не найдена

    return examples# Возвращаем список

#Функция для получения описания техники
def get_explanation(id):
    url = f'https://attack.mitre.org/techniques/{id.replace(".", "/")}'# Формирование URL
    response = requests.get(url)# Отправка запроса
    html_content = response.content# Получение HTML кода
    soup = BeautifulSoup(html_content, 'html.parser')# Парсинг HTML
    description_div = soup.find('div', class_='description-body')# Поиск блока с описанием
    
    if description_div:# Если блок найден
        first_p_tag = description_div.find('p')# Находим первый тег <p>
        if first_p_tag:# Если тег найден
            extracted_text = first_p_tag.get_text()# Извлекаем текст
            return extracted_text# Возвращаем текст
        else:
            return "Описание не найдено."# Возвращаем текст
    else:
        return "Раздел с описанием не найден."# Если блок с описанием не найден

#Чтение файла 1.txt
with open('1.txt', 'r', encoding='utf-8') as f:
    file_content = f.read()
#Разделение на блоки по разделителю
blocks = re.split(r'={40,}', file_content)
rules = []
#Цикл по блокам
for block in blocks:
    lines = block.strip().split('\n')
    if lines:# Если в блоке есть строки
        # Словарь для данных о правиле
        rule_info = {'title': "Не удалось получить название", 'tactic': "Не удалось получить тактику", 'rule': "Не удалось получить правило", 'id': "Не удалось получить ID"}  
        for line in lines:# Цикл по строкам блока
            if "Правило:" in line:# Поиск строки с правилом
                rule_info['rule'] = line.split(': ')[1]
            elif "Tactic:" in line:# Поиск строки с тактикой
                rule_info['tactic'] = line.split(': ')[1]
            elif "ID:" in line:# Поиск строки с ID
                rule_info['id'] = line.split(': ')[1]
                title = get_technique_title(rule_info['id'])# Получаем название техники по ID
                if title: # Если название получено, записываем его 
                    rule_info['title'] = title
        rules.append(rule_info)# Добавляем словарь с информацией о правиле в список

# Создаем файл Excel
workbook = xlsxwriter.Workbook("маппинг_таблица.xlsx")
worksheet = workbook.add_worksheet()

# Устанавливаем ширину колонок
worksheet.set_column(0, 0, 55)
worksheet.set_column(1, 1, 25)
worksheet.set_column(2, 2, 10)
worksheet.set_column(3, 3, 40)
worksheet.set_column(4, 4, 100) 
worksheet.set_column(5, 5, 60)   

# Заголовки столбцов
worksheet.write(0, 0, "Rule")
worksheet.write(0, 1, "Tactic")
worksheet.write(0, 2, "ID")
worksheet.write(0, 3, "Techniques")
worksheet.write(0, 4, "Description")            
worksheet.write(0, 5, "Procedure Examples")  

# Заполняем таблицу данными
for row_num, rule_info in enumerate(rules, start=1):
    worksheet.write(row_num, 0, rule_info['rule'])
    worksheet.write(row_num, 1, rule_info['tactic'])
    worksheet.write(row_num, 2, rule_info['id'])
    worksheet.write(row_num, 3, rule_info['title'])
    
    # Получаем данные из функции и записываем их в столбец "Описание"
    explanation = get_explanation(rule_info['id'])
    worksheet.write(row_num, 4, explanation)  # Записываем в ячейку
    
    # Получаем данные из функции и записываем их в столбец "Procedure Examples"
    examples = get_procedure_examples(rule_info['id'])
    worksheet.write(row_num, 5, '\n'.join(examples))  # Записываем в ячейку с переносами строк

# Закрываем файл Excel
workbook.close()

print("Отчет успешно создан.")
