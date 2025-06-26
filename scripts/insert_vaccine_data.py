import os
import sys
import django

# 경로 및 설정 로드
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from onboard.models import Country, Vaccine, RequiredVaccine

vaccine_data = {
    'US': ['황열', '장티푸스', '말라리아'],
    'JP': ['일본뇌염'],
    'TH': ['말라리아', '장티푸스'],
    'IN': ['콜레라', 'A형간염'],
}

for code, vaccine_list in vaccine_data.items():
    country = Country.objects.filter(code=code).first()
    if not country:
        print(f"❌ {code}에 해당하는 Country 없음")
        continue

    for vaccine_name in vaccine_list:
        code_key = vaccine_name[:3].upper()

        vaccine, _ = Vaccine.objects.get_or_create(
            code=code_key,
            defaults={'name': vaccine_name}
        )

        RequiredVaccine.objects.get_or_create(
            country=country,
            vaccine=vaccine
        )

    print(f"✅ {country.name}에 백신 매핑 완료")
