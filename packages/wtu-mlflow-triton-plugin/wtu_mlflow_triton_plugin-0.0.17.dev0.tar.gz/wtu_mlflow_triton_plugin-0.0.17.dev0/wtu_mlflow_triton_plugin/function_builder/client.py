# client.py
from pathlib import Path
from typing import Any, Optional

from .models import FunctionConfig, ValidationResult
from .validator import FunctionValidator
from .venv_manager import VenvManager


class FunctionBuilder:
    """OpenWhisk 클라이언트"""

    def __init__(self, import_timeout: int = 30, execution_timeout: int = 60):
        # 초기화
        cache_dir = Path.home() / ".function_builder"
        self.venv_manager = VenvManager(cache_dir)
        self.validator = FunctionValidator(
            self.venv_manager, import_timeout, execution_timeout
        )

    def validate(
        self,
        python_file: str,
        requirements_file: Optional[str] = None,
        test_params: Optional[dict[str, Any]] = None,
    ) -> ValidationResult:
        """로컬 검증"""
        print("🔍 함수 검증 중...")

        result = self.validator.validate(python_file, requirements_file, test_params)

        self._print_validation_result(result)
        return result

    def deploy(
        self,
        config: FunctionConfig,
        validate_first: bool = True,
        test_params: Optional[dict[str, Any]] = None,
    ) -> bool:
        """함수 배포"""
        print(f"🚀 {config.name} 배포 시작...")

        # 검증
        if validate_first:
            validation = self.validate(
                config.python_file, config.requirements_file, test_params
            )
            if not validation.valid:
                print("❌ 검증 실패로 배포 중단")
                return False

        # 서버에 업로드
        success = self._upload_to_server(config)

        if success:
            print(f"✅ {config.name} 배포 완료!")
        else:
            print("❌ 배포 실패")

        return success

    def _upload_to_server(self, config: FunctionConfig) -> bool:
        """서버에 파일 업로드"""
        # 파일 준비
        files = {}

        # Context managers로 파일 처리
        try:
            with Path(config.python_file).open("rb") as main_file:
                files["main_py"] = ("main.py", main_file.read(), "text/x-python")

            if config.requirements_file:
                with Path(config.requirements_file).open("rb") as req_file:
                    files["requirements_txt"] = (
                        "requirements.txt",
                        req_file.read(),
                        "text/plain",
                    )

            data = {
                "function_name": config.name,
                "python_version": config.python_version.value,  # enum을 문자열로 변환
                "memory": config.memory,
                "timeout": config.timeout,
            }

            # TODO: 실제 서버 API 호출
            # response = requests.post(...)

            # Mock response
            return True
        except Exception:
            return False

    def _print_validation_result(self, result: ValidationResult):
        """검증 결과 출력"""
        print("\n📊 검증 결과:")
        print(f"   상태: {'✅ 통과' if result.valid else '❌ 실패'}")

        if result.info:
            if "main_line" in result.info:
                print(f"   main 함수: {result.info['main_line']}번째 줄")
            if "execution_time" in result.info:
                print(f"   실행 시간: {result.info['execution_time']:.3f}초")

        if result.warnings:
            print(f"\n⚠️  경고 ({len(result.warnings)}개):")
            for warning in result.warnings:
                print(f"   - {warning}")

        if result.errors:
            print(f"\n❌ 오류 ({len(result.errors)}개):")
            for error in result.errors:
                print(f"   - {error}")

        print()
