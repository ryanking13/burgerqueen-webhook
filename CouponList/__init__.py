import json
import logging
import requests
import azure.functions as func

BASE_URL = 'http://ec2-52-79-88-56.ap-northeast-2.compute.amazonaws.com/bkr-omni/BKR4001.json'
BASE_HEADERS = {
    'Host': 'app.burgerking.co.kr:443',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36',
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    udid = req.params.get('udid')

    if not udid:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('udid')

    params = {
        'header': {
            'result': 'true',
            # 'error_code': '',
            # 'error_text': '',
            # 'info_text': '',
            # 'message_version': '',
            # 'login_session_id': '',
            'trcode': 'BKR4001',
            # 'ip_address': '',
            'platform': '01',
            # 'id_member': '',
            # 'auth_token': '',
            'is_cryption': 'false',
        },
        'body': {
            'cdCouponObj': '3',
            'udid': udid,
        },
    }

    data = {
        'message': json.dumps(params)
    }

    if udid:
        r = requests.post(url=BASE_URL, data=data, headers=BASE_HEADERS)
        try:
            json_response = r.json()
            coupon_list = json_response['body']['couponList']
            return func.HttpResponse(
                json.dumps(coupon_list),
                headers = {
                    'Access-Control-Allow-Origin': '*',
                }
            )
        except Exception as e:
            logging.info('Exception ' + str(e))
            logging.info('Fail ' + r.text)
            return func.HttpResponse(
                "Fail to get couponList",
                status_code=400
            )
    else:
        return func.HttpResponse(
             "UDID not given",
             status_code=400
        )
