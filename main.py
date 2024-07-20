import sqlite3

connect = sqlite3.connect('client.sqlite')
cursor = connect.cursor()


def add_machines(machines: list[tuple[str, str]]) -> None:
    """Добавляет 3 станка: “Сварочный аппарат №1”, “Пильный аппарат №2”, “Фрезер №3” делает их активными"""

    try:
        cursor.executemany('INSERT INTO endpoints(name, active) VALUES(?, ?)', machines)
        connect.commit()
    except Exception as e:
        raise e


def add_reasons(repl_dict: dict[int, int]) -> None:
    """Копирует со станков: “Фрезерный станок”, “Старый, ЧПУ”, “Сварка”, причины простоя и переносит
    их на новые станки"""

    try:
        cursor.execute('''
            SELECT  reason_name, reason_hierarchy, endpoint_id
            FROM endpoint_reasons
            JOIN endpoints ON endpoint_reasons.endpoint_id = endpoints.id
            WHERE name IN (?,?,?)
            ORDER BY endpoint_id
    ''', ('Фрезерный станок', 'Старый ЧПУ', 'Сварка'))
    except Exception as e:
        raise e

    result = cursor.fetchall()

    try:
        for i, row in enumerate(result):
            result[i] = row[:-1] + (repl_dict.get(row[-1]),)
        cursor.executemany('''
                        INSERT INTO endpoint_reasons(reason_name, reason_hierarchy, endpoint_id) 
                        VAlUES(?, ?, ?)
                        ''', result)
        connect.commit()
    except Exception as e:
        raise e


def create_group() -> None:
    """Определяет группу “Цех №2” для новых станков"""

    try:
        cursor.execute('''SELECT  DISTINCT endpoint_id
            FROM endpoint_reasons
            JOIN endpoints ON endpoint_reasons.endpoint_id = endpoints.id
            WHERE name IN (?,?,?)
    ''', ('Сварочный аппарат №1', 'Пильный аппарат №2', 'Фрезер №3'))
    except Exception as e:
        raise e

    result = cursor.fetchall()
    try:
        for i in result:
            cursor.execute('''
                    INSERT INTO endpoint_groups(endpoint_id, name) VALUES(?, ?)''',
                           (*i, 'Цех №2'))
        connect.commit()
    except Exception as e:
        raise e


def add_group() -> None:
    """Добавляет станки “Пильный станок” и “Старый ЧПУ” к новой группе"""

    try:
        cursor.execute('''SELECT  DISTINCT endpoint_id
            FROM endpoint_reasons
            JOIN endpoints ON endpoint_reasons.endpoint_id = endpoints.id
            WHERE name IN (?,?)
    ''', ('Пильный станок', 'Старый ЧПУ'))
    except Exception as e:
        raise e
    result = cursor.fetchall()
    try:
        for i in result:
            cursor.execute('''
                UPDATE  endpoint_groups SET name = ? WHERE endpoint_id = ?
                ''', ('Цех №2', *i))
        connect.commit()
    except Exception as e:
        raise e


if __name__ == '__main__':
    add_machines([
        ("Сварочный аппарат №1", 'true'),
        ("Пильный аппарат №2", 'true'),
        ("Фрезер №3", 'true')
    ])

    add_reasons({
        1: 7,
        5: 8,
        6: 9
    })

    create_group()
    add_group()
