import requests
from bs4 import BeautifulSoup

def data_extraction():
    """
    Harga Emas Hari Ini, 28 Jun 2025
    Butik Emas LM Grahadipta - Jakarta

    Harga di-update setiap hari pkl. 08.30 WIB

    Berat	Harga Dasar	Harga (+Pajak PPh 0.25%)

    Emas Batangan :
    0.5 gr	992,000	994,480
    1 gr	1,884,000	1,888,710
    2 gr	3,708,000	3,717,270
    3 gr	5,537,000	5,550,843
    5 gr	9,195,000	9,217,988
    10 gr	18,335,000	18,380,838
    25 gr	45,712,000	45,826,280
    50 gr	91,345,000	91,573,363
    100 gr	182,612,000	183,068,530
    250 gr	456,265,000	457,405,663
    500 gr	912,320,000	914,600,800
    1000 gr	1,824,600,000	1,829,161,500
    :return:
    """
    try:
        content = requests.get('https://www.lakuemas.com/')
    except Exception:
        return None
    if content.status_code == 200:
        soup = BeautifulSoup(content.text,'html.parser')
        results = soup.find('small', {'style': 'letter-spacing: 1px !important; font-size: 14px;'}) # find date and time
        results = results.text.split(',')
        prices_daily_at = results[2]
        update_gold_today = results[1]

        results = soup.find('h3', {'class':'font-weight-bold'}) # find buy price
        results = results.text
        buy_price = results

        results = soup.find('p',{'class':'font-weight-normal'}) # find weight
        results = results.text
        weight1 = results


        results = soup.find('div',{'class':'col-md-6 text-center border-left'})
        results = results.find_all()
        i = 0
        sell_price = None
        weight2 = None
        for res in results:
            if i == 1:
                sell_price = res.text
            elif i == 2:
                weight2 = res.text
            i = i + 1


        r = dict()
        r['update gold today'] = update_gold_today
        r['prices are update daily at'] = prices_daily_at
        r['buy price IDR'] = buy_price
        r['weight buy'] = weight1
        r['sell price'] = sell_price
        r['weight sell'] = weight2

        return r
    else:
        return None

def view_data(result):
    if result is None:
        print('Data not found!')
        return
    print('Update Price Gold Today source lakuemas.com')
    print('\n')
    print(f"Update gold today{result['update gold today']}")
    print(f"Prices are update daily at{result['prices are update daily at']}")
    print(f"Buy price {result['buy price IDR']}")
    print(f"Weight : {result['weight buy']}")
    print(f"Sell price {result['sell price']}")
    print(f"Weight : {result['weight sell']}")

if __name__ == '__main__':
    print('Main Application')
    print('\n')
    result = data_extraction()
    view_data(result)
