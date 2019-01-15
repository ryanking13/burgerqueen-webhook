import json
import logging
import requests
import azure.functions as func

BASE_URL = 'https://deliveryapp.co.kr/app/coupon/getCouponList.do'
BASE_HEADERS = {
    'Referer': 'https://deliveryapp.co.kr',
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
        'udid': udid,
        'appVersion': '3.0.9',
        'channel': '2',
        'delKingSe': '3',
    }

    if udid:
        r = requests.get(url=BASE_URL, params=params, headers=BASE_HEADERS)
        try:
            json_response = r.json()
            coupon_list = json_response['resultlist']
            return func.HttpResponse(json.dumps(coupon_list))
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
