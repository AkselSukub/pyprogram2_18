#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date
import json
import argparse
import os.path
from jsonschema import validate, ValidationError
import sys

def get_worker(staff, point, number, type):
    """
    Запросить данные о рейсе.
    """
    # Создать словарь.
    staff.append(
        {
            'point': point,
            'number': number,
            'type': type
        }
    )
    return staff

def display_workers(staff):
    """
    Отобразить список рейсов.
    """
    # Проверить, что список рейсов не пуст.
    if staff:
        # Заголовок таблицы.
        line = "+-{}-+-{}-+-{}-+-{}-+".format(
            "-" * 4, "-" * 30, "-" * 10, "-" * 20
        )
        print(line)
        print(
            "| {:^4} | {:^30} | {:^10} | {:^20} |".format(
                "No", "Пункт назначения", "No рейса", "Тип самолета"
            )
        )
        print(line)
        # Вывести данные о всех рейсах.
        for idx, worker in enumerate(staff, 1):
            print(
                "| {:>4} | {:<30} | {:<10} | {:>20} |".format(
                    idx,
                    worker.get("point", ""),
                    worker.get("number", 0),
                    worker.get("type", ""),
                )
            )
        print(line)
    else:
        print("Список рейсов пуст.")


def select_workers(staff, period):
    """
    Выбрать работников с заданным стажем.
    """
    # Получить текущую дату.
    today = date.today()
    # Сформировать список рейсов.
    result = []
    for employee in staff:
        if today.year - employee.get("year", today.year) >= period:
            result.append(employee)
    # Возвратить список выбранных рейсов.
    return result


def save_workers(file_name, staff):
    """
    Сохранить все рейсы в файл JSON.
    """
    # Открыть файл с заданным именем для записи.
    with open(file_name, "w", encoding="utf-8") as fout:
        # Выполнить сериализацию данных в формат JSON.
        # Для поддержки кирилицы установим ensure_ascii=False
        json.dump(staff, fout, ensure_ascii=False, indent=4)


def load_workers(file_name):
    """
    Загрузить все рейсы из файла JSON.
    """
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "point": {"type": "string"},
                "number": {"type": "integer"},
                "type": {"type": "string"},
            },
            "required": [
                "point",
                "number",
                "type",
            ],
        },
    }
    # Проверить, существует ли файл
    if os.path.exists(file_name):
        # Открыть файл с заданным именем для чтения.
        with open(file_name, "r", encoding="utf-8") as fin:
            data = json.load(fin)
        
        try:
            # Валидация
            validate(instance=data, schema=schema)
            print("JSON валиден по схеме.")
        except ValidationError as e:
            print(f"Ошибка валидации: {e.message}")
        return data
    else:
        print(f"Файл {file_name} не найден.")
        sys.exit(1)

def main(command_line=None):
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "filename",
        action="store",
        help="The data file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("staff")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления маршрута.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new staff"
    )
    add.add_argument(
        "-p",
        "--point",
        action="store",
        required=True,
        help="The start of the staff"
    )
    add.add_argument(
        "-n",
        "--number",
        action="store",
        type=int,
        required=True,
        help="The finish of the staff"
    )
    add.add_argument(
        "-t",
        "--type",
        action="store",
        required=True,
        help="The number of the staff"
    )
    # Создать субпарсер для отображения всех маршрутов.
    display = subparsers.add_parser(
        "display",
        parents=[file_parser], # Добавьте file_parser как родительский парсер
        help="Display all staff"
    )
    # Создать субпарсер для выбора маршрута.
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the staff"
    )
    select.add_argument(
        "-p",
        "--period",
        action="store",
        type=int,
        required=True,
        help="The staff"
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    # Загрузить все маршруты из файла, если файл существует.
    is_dirty = False
    if os.path.exists(args.filename):
        staff = load_workers(args.filename)
    else:
        staff = []

    # Добавить маршрут.
    if args.command == "add":
        staff = get_worker(
            staff,
            args.point,
            args.number,
            args.type
        )
        is_dirty = True

    # Отобразить все маршруты.
    elif args.command == "display":
        display_workers(staff)

    # Выбрать требуемые маршруты.
    elif args.command == "select":
        selected = select_workers(staff, args.period)
        display_workers(selected)

    # Сохранить данные в файл, если список маршрутов был изменен.
    if is_dirty:
        save_workers(args.filename, staff)


if __name__ == '__main__':
    main()