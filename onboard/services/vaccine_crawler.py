import requests
import xml.etree.ElementTree as ET


def get_vaccine_info():
    url = "http://apis.data.go.kr/1790387/vcninfo/getCondVcnCd"
    service_key = "pioNaBQBJ/ABwVXqTllZFvr7FUBvhyIvfwaaH/0hZSC+8LDRLjenEw0ed5uWdL0bptwm5vBBFZyei0p4dieK+Q=="

    params = {
        "serviceKey": service_key
    }

    try:
        response = requests.get(url, params=params)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall(".//item")

            result = []
            for item in items:
                code = item.findtext("cd", default="정보 없음")
                name = item.findtext("cdNm", default="이름 없음")
                result.append({"code": code, "name": name})

            return {"vaccine_info": result}
        else:
            return {"error": f"요청 실패: 상태 코드 {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"요청 중 오류 발생: {e}"}
    except ET.ParseError as e:
        return {"error": f"XML 파싱 오류 발생: {e}"}
