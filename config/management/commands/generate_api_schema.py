from django.core.management.base import BaseCommand
from drf_spectacular.management.commands.spectacular import (
    Command as SpectacularCommand,
)
import os


class Command(BaseCommand):
    help = "API 스키마를 생성하고 저장합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="api_schema.json",
            help="출력 파일명 (기본값: api_schema.json)",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["json", "yaml"],
            default="json",
            help="출력 형식 (json 또는 yaml)",
        )

    def handle(self, *args, **options):
        output_file = options["output"]
        output_format = options["format"]

        # drf-spectacular의 기본 커맨드를 사용하여 스키마 생성
        spectacular_cmd = SpectacularCommand()

        try:
            # 스키마를 파일로 출력
            if output_format == "yaml":
                output_file = output_file.replace(".json", ".yaml")

            spectacular_cmd.handle(
                file=output_file,
                format=output_format,
                validate=True,
                fail_on_warn=False,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ API 스키마가 성공적으로 생성되었습니다: {output_file}"
                )
            )

            # 파일 크기 정보 출력
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                self.stdout.write(f"📄 파일 크기: {file_size} bytes")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ 스키마 생성 중 오류가 발생했습니다: {str(e)}")
            )
