import requests
from bs4 import BeautifulSoup
from pprint import pprint


def get_content(faculty, type_list):
    session = requests.Session()
    html = session.get('https://abiturient.nsu.ru/').text
    soup = BeautifulSoup(html, 'lxml')
    csrf = soup.find('meta', {'name': 'csrf-token'})['content']
    data = {'_csrf-frontend': csrf,
            'type': type_list,
            'condition': 10,
            'faculty': faculty
            }
    r = session.post(
        'https://abiturient.nsu.ru/bachelor/list-content',
        data=data)
    return r.json()


def get_es(fs, type_list, acronyms):
    es = {}
    ds = []
    for f in fs:
        ds += get_content(fs[f], type_list)

    for d in ds:
        name_d = d["info"]["speciality"]["name"]
        for e in d['table']:
            name = e['name']
            if name not in es:
                es[name] = {}
            es[name][acronyms[name_d]] = {
                'number': e['number'],
                'dis': e['disciplines'],
                'spd': e['sumPointDiscipline'],
                'spa': e['sumPointAchievement'],
                'spt': e['sumPointTotal'],
                'consent': acronyms[name_d] if e['consent'] else 'Нет',
                'condition': 'БВИ' if e['condition'] == 'Без вступительных испытаний' else ''
            }
    return es


def get_article(direction, name, typ):
    fs = {'ММФ': 6, 'ФИТ': 8}
    type_list = {'Конкурс': 20, 'Зачисление': 30}
    acronyms = {
        'Математика': 'М',
        'Прикладная математика и информатика': 'ПМИ',
        'Математика и компьютерные науки': 'МКН',
        'Информатика и вычислительная техника': 'ИВТ',
        'Механика и математическое моделирование': 'МММ'
    }

    es = get_es(fs, type_list[typ], acronyms)
    es = {e: es[e] for e in es if direction in es[e]}
    es_sort = sorted(es, key=lambda x: int(es[x][direction]['number']))
    es_directions = get_es(fs, 20, acronyms)

    with open('base.html', encoding='utf-8') as bs:
        template = BeautifulSoup(bs, 'lxml')

    template.title.string = name
    for name in es_sort:
        tr = BeautifulSoup(
            f'<tr><td>{es[name][direction]["number"]}.</td><td>{name} {es[name][direction]["condition"]}</td>'
            f'<td>{es[name][direction]["spt"]}</td>'
            f'<td>{", ".join(es_directions[name])}</td>'
            f'<td>{es[name][direction]["consent"]}</td></tr>', 'lxml')
        template.tbody.append(tr)
    return template.prettify()


def main():
    fs = {"ММФ": 6, "ФИТ": 8}
    acronyms = {
        'Математика': 'М',
        'Прикладная математика и информатика': 'ПМИ',
        'Математика и компьютерные науки': 'МКН',
        'Информатика и вычислительная техника': 'ИВТ'
    }
    es = get_es(fs, 30, acronyms)
    es = {e: es[e] for e in es if 'ПМИ' in es[e]}
    es_sort = sorted(es, key=lambda x: int(es[x]['ПМИ']['number']))
    res = ''
    for name in es_sort:
        res += f'{es[name]["ПМИ"]["number"]}. {name}\n\n' \
               f'Сумма баллов: {es[name]["ПМИ"]["spt"]}\n' \
               f'Направления: {", ".join(es[name])}\n' \
               f'Согласие: {es[name]["ПМИ"]["consent"] if es[name]["ПМИ"]["consent"] else "Нет"}\n\n'
    print(res)


if __name__ == "__main__":
    main()
