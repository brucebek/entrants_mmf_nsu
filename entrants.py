import requests
from bs4 import BeautifulSoup
from pprint import pprint


def get_content(faculty):
    session = requests.Session()
    html = session.get('https://abiturient.nsu.ru/').text
    soup = BeautifulSoup(html, 'lxml')
    csrf = soup.find('meta', {'name': 'csrf-token'})['content']
    data = {'_csrf-frontend': csrf,
            'type': 20,
            'condition': 10,
            'faculty': faculty
            }
    r = session.post(
        'https://abiturient.nsu.ru/bachelor/list-content',
        data=data)
    return r.json()


def get_es_sort(fs, acronyms):
    es = {}
    ds = []
    for f in fs:
        ds += get_content(fs[f])

    for d in ds:
        name_d = d["info"]["speciality"]["name"]
        if name_d == "Механика и математическое моделирование":
            continue
        for e in d['table']:
            name = e['name']
            if name in es:
                es[name]['directions'].append(acronyms[name_d])
                if e['consent']:
                    es[name]['consent'] = name_d
                continue

            if e['condition'] == "Без вступительных испытаний":
                e['sumPointTotal'] = 1000

            es[name] = {
                'directions': [acronyms[name_d]],
                'dis': [
                    {
                        'name': dis['name'],
                        'point': int(
                            dis['point']) if e['sumPointTotal'] != 1000 else dis['point']} for dis in e['disciplines']],
                'sumDis': int(
                    e['sumPointDiscipline']),
                'sumAchiv': int(
                    e['sumPointAchievement']),
                'sumTotal': int(
                    e["sumPointTotal"]),
                'consent': name_d if e['consent'] else None,
                'condition': e['condition']}

        names = list(es.keys())
        for name in names:
            if 'ИВТ' in es[name]['directions'] and len(
                    es[name]['directions']) == 1:
                del es[name]

        es_sort = sorted(
            es,
            key=lambda x: (
                es[x]['sumTotal'],
                es[x]['dis'][0]['point'],
                es[x]['dis'][1]['point'],
                es[x]['dis'][2]['point'],
                es[x]['sumAchiv']),
            reverse=True)
    return es, es_sort


def get_article(flt, name):
    fs = {"ММФ": 6, "ФИТ": 8}
    acronyms = {
        'Математика': 'М',
        'Прикладная математика и информатика': 'ПМИ',
        'Математика и компьютерные науки': 'МКН',
        'Информатика и вычислительная техника': 'ИВТ'
    }
    es, es_sort = get_es_sort(fs, acronyms)
    with open('base.html', encoding='utf-8') as bs:
        template = BeautifulSoup(bs, 'lxml')

    i = 1
    for name in es_sort:
        es[name]['sumTotal'] = es[name]['sumDis'] + es[name]['sumAchiv']

        if flt(es[name]):
            tr = BeautifulSoup(
                f'<tr><td>{i}.</td><td> {name}{" БВИ" if es[name]["condition"] == "Без вступительных испытаний" else ""}</td>' \
                f'<td>{es[name]["sumTotal"]}</td>' \
                f'<td>{", ".join(es[name]["directions"])}</td>' \
                f'<td>{es[name]["consent"] if es[name]["consent"] else "Нет"}</td></tr>', 'lxml')
            i += 1
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
    es, es_sort = get_es_sort(fs, acronyms)

    res = ''
    i = 1
    for name in es_sort:
        if 'М' in es[name]['directions'] and es[name]['sumTotal'] > 257:
            es[name]['sumTotal'] = es[name]['sumDis'] + es[name]['sumAchiv']
            res += f'{i}. {name}\n\n' \
                   f'Сумма баллов: {es[name]["sumTotal"]}\n' \
                   f'Направления: {", ".join(es[name]["directions"])}\n' \
                   f'Согласие: {es[name]["consent"] if es[name]["consent"] else "Нет"}\n\n'
            i += 1
    print(res)


if __name__ == "__main__":
    main()
