"""
1. "시군구 버스정류장" (ex. "서울특별시 강남구 버스정류장") 으로 버스정류장 300개 검색
2. 결과로 얻은 300개의 버스정류장들 중 주소에 검색주소가 포함되는 정류장들을 딕셔너리에 추가
3. 결과로 얻은 300개의 버스정류장들 중 뒤의 n개 위치정보를 기준으로 새롭게 주변 버스정류장 300개씩 검색
4. 3의 결과로 얻은 n*300개의 버스정류장들에 대해 2를 수행
5. 주변 버스정류장에 더이상 검색주소가 포함되지 않을 때까지 2~4 반복
"""

"""
요청을 보내도 응답이 오지 않는 경우가 잦아 fake_useragent를 사용했고,
약간의 텀을 두어 알맞은 요청을 받을 때까지 지속적으로 요청을 보내도록 설계
"""


import requests as req
import pandas as pd
import json
import xmltodict
import random
import time
from fake_useragent import UserAgent


# Request Parameters
# caller='pcweb', type='bus-station', lang='ko'
# query='PLACE 버스정류장' / query='버스정류장'
# displayCount=AROUND_BUSSTATION_NUM
# searchCoord='경도;위도'
URL = 'https://map.naver.com/v5/api/search'
ua = UserAgent()
# chrome_headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',}


AROUND_BUSSTATION_NUM = 300 # 검색할 주변 버스정류장 수 (최대300)
NEXT_BUSSTATION_NUM = 5 # 다음에 주변검색을 할 버스정류장 수
CITYNAMES = ['서울특별시 강남구', '서울특별시 중구', '서울특별시 종로구', '경상남도 거창군', '강원도 정선군']
CITYCOORDS = ['127.04383850097658;37.50993009823709', '126.9767189025879;37.560330016090184', '126.96873664855958;37.60148224354437', '129.38139438629153;36.08318198198435', '126.96904015393665;37.58262849999988']

INDEX = 4

busStation_dict = {}

def getBusStationDictByCity(cityIndex):
    cityName = CITYNAMES[cityIndex]
    cityCoord = CITYCOORDS[cityIndex]

    params = {
        'caller': 'pcweb',
        'query': '{} 버스정류장'.format(cityName),
        'type': 'all',
        'searchCoord': cityCoord,
        'page': 1,
        'displayCount': AROUND_BUSSTATION_NUM,
        'isPlaceRecommendationReplace': 'true',
        'lang': 'ko'
    }

    while True:
        headers = {'User-Agent': ua.random, 'referer': 'https://map.naver.com/'}
        response = req.get(URL, params=params, headers=headers)

        try:
            response_json = response.json()
            break
        except json.decoder.JSONDecodeError:
            print('에러발생 Response : {}'.format(response.status_code))
            time.sleep(random.random() * 5)

    for busStationInfo in response_json['result']['bus']['busStation']['list']:
        if cityName in busStationInfo['address'] and busStationInfo['id'] not in busStation_dict:
            new_busStation = {
                'name': busStationInfo['name'],
                'address': busStationInfo['address'],
                'x': busStationInfo['x'],
                'y': busStationInfo['y']
            }
            busStation_dict[busStationInfo['id']] = new_busStation


def getBusStationDictByCoord(x, y):
    params = {
        'caller': 'pcweb',
        'query': '버스정류장',
        'type': 'all',
        'searchCoord': '{};{}'.format(x, y),
        'page': 1,
        'displayCount': AROUND_BUSSTATION_NUM,
        'isPlaceRecommendationReplace': 'true',
        'lang': 'ko'
    }

    while True:
        headers = {'User-Agent': ua.random, 'referer': 'https://map.naver.com/'}
        response = req.get(URL, params=params, headers=headers)

        try:
            response_json = response.json()
            break
        except json.decoder.JSONDecodeError:
            # print('에러발생 (response{})Coord : {}, {}'.format(response.status_code, x, y))
            time.sleep(random.random() * 5)


    for busStationInfo in response_json['result']['bus']['busStation']['list']:
        if CITYNAMES[INDEX] in busStationInfo['address'] and busStationInfo['id'] not in busStation_dict:
            new_busStation = {
                'name': busStationInfo['name'],
                'address': busStationInfo['address'],
                'x': busStationInfo['x'],
                'y': busStationInfo['y']
            }
            busStation_dict[busStationInfo['id']] = new_busStation


getBusStationDictByCity(INDEX)
# print(len(busStation_dict))

for i in range(0, 5):
    busStation_list = list(busStation_dict.items())
    idx = len(busStation_list) - j
    nextCoords = []
    for j in range(1, NEXT_BUSSTATION_NUM + 1):
        nextCoords.append({'x': busStation_list[idx][1]['x'], 'y': busStation_list[idx][1]['y']})

    for nextCoord in nextCoords:
        getBusStationDictByCoord(nextCoord['x'], nextCoord['y'])

    print('{} : {}'.format(i, len(busStation_dict)))


contents = ''
for b in busStation_dict:
    contents += '{}\t{}\t({}, {})\n'.format(b, busStation_dict[b]['name'], busStation_dict[b]['x'], busStation_dict[b]['y'])

f = open('./busStations/{} 버스정류장들.txt'.format(CITYNAMES[INDEX]), 'w')
f.write(contents)
f.close()