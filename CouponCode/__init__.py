import json
import logging
import requests
import logging
import azure.functions as func

BASE_URL = 'https://deliveryapp.co.kr/app/coupon/getCouponPinData.do'
BASE_HEADERS = {
    'Referer': 'https://deliveryapp.co.kr',
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    udid = req.params.get('udid')
    couponpk = req.params.get('couponpk')

    if not udid:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('udid')
            couponpk = req_body.get('couponpk')

    params = {
        'udid': udid,
        'couponPk': couponpk,
        'appVersion': '3.0.9',
        'channel': '2',
        'delKingSe': '3',
    }

    if udid and couponpk:
        r = requests.get(url=BASE_URL, params=params, headers=BASE_HEADERS)
        try:
            json_response = r.json()
            coupon_code = json_response['resultMap']['couponPinData']
            return func.HttpResponse(
                json.dumps(coupon_code),
                headers = {
                    'Access-Control-Allow-Origin': '*',
                }
            )
        except Exception as e:
            logging.info('Exception ' + str(e))
            logging.info('Fail ' + r.text)
            return func.HttpResponse(
                "Fail to get couponCode",
                status_code=400
            )
    else:
        return func.HttpResponse(
             "UDID or couponPk not given",
             status_code=400
        )
