import json
import logging
import random
from bs4 import BeautifulSoup
import requests
import azure.functions as func

SURVEY_URL = 'https://kor.tellburgerking.com/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
CODE_ERROR_MSG = '입력하신 정보로 설문조사를 진행할 수 없습니다.'


def find_next_url(soup):
    return soup.find('form').get('action')


def find_IoNF(soup):
    return soup.find('input', {'id': 'IoNF'}).get('value')


def find_PostedFNS(soup):
    return soup.find('input', {'id': 'PostedFNS'}).get('value')


def find_ValCode(soup):
    return soup.find('p', {'class': 'ValCode'})


def init_survey(code):
    initial_data = {
        'JavaScriptEnabled': '1',
        'FIP': 'True',
        'AcceptCookies': 'Y',
        'CN1': code[0:3],
        'CN2': code[3:6],
        'CN3': code[6:9],
        'CN4': code[9:12],
        'CN5': code[12:15],
        'CN6': code[15],
    }

    sess = requests.Session()
    sess.headers.update({'User-Agent': USER_AGENT})

    r = sess.get(SURVEY_URL)
    next_url = find_next_url(BeautifulSoup(r.text, 'html.parser'))

    r = sess.post(SURVEY_URL + next_url, data=initial_data)
    next_url = find_next_url(BeautifulSoup(r.text, 'html.parser'))

    r = sess.post(SURVEY_URL + next_url, data=initial_data)

    if CODE_ERROR_MSG in r.text:
        raise ValueError('Wrong Survey Code')

    return sess, r


def run_survey(sess, resp):
    page = resp.text
    soup = BeautifulSoup(page, 'html.parser')

    ValCode = find_ValCode(soup)
    if ValCode:
        return ValCode.text[len('확인 코드: '):]

    IoNF = find_IoNF(soup)
    PostedFNS = find_PostedFNS(soup)
    next_url = find_next_url(soup)

    data = {}
    for column in PostedFNS.split('|'):
        data[column] = random.randint(1, 2)

    data.update({
        'IoNF': IoNF,
        'PostedFNS': PostedFNS,
    })

    # print('next: ', next_url)
    r = sess.post(SURVEY_URL + next_url, data=data)
    return run_survey(sess, r)


def retrieve_code(survey_code):

    if len(survey_code) != 16:
        return -1

    try:
        sess, resp = init_survey(survey_code)
    except ValueError as e:
        return -1

    code = run_survey(sess, resp)
    return code


def main(req: func.HttpRequest) -> func.HttpResponse:
    code = req.params.get('code')

    if not code:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            code = req_body.get('code')

    if not code:
        return func.HttpResponse(
            "설문조사 코드를 입력하세요",
            status_code=400,
            headers={
                'Access-Control-Allow-Origin': '*',
            }
        )

    try:
        val_code = retrieve_code(code)
    except Exception as e:
        logging.info('Exception ' + str(e))
        return func.HttpResponse(
            "Undefined Error",
            status_code=400,
            headers={
                'Access-Control-Allow-Origin': '*',
            }
        )

    if val_code == -1:
        return func.HttpResponse(
            "잘못된 설문조사 코드입니다",
            status_code=400,
            headers={
                'Access-Control-Allow-Origin': '*',
            }
        )

    return func.HttpResponse(
        json.dumps({'valCode': val_code}),
        headers={
            'Access-Control-Allow-Origin': '*',
        }
    )
