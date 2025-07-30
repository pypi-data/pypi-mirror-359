## Sogon 프로젝트의 전문 CLI 도구화 계획: 설치부터 배포까지 (Hatchling 적용)

안녕하세요, Sogon 프로젝트 팀입니다.

Sogon은 유튜브 영상의 음성을 추출하고, 텍스트로 변환하며, 번역까지 수행하는 강력한 워크플로우를 제공합니다. 하지만 현재는 개발자나 Python 환경에 익숙한 사용자만이 `git clone` 후 복잡한 설치 과정을 거쳐야 사용할 수 있었습니다.

이러한 진입 장벽을 허물고, 누구나 Sogon의 가치를 손쉽게 경험할 수 있도록, 프로젝트를 **전문적인 CLI(Command-Line Interface) 도구로 패키징하고 PyPI(Python Package Index)에 배포**하기 위한 구체적인 기술 계획을 공유합니다. 이 계획은 최신 Python 개발 트렌드를 반영하여 `Hatch`와 `Hatchling`을 중심으로 구성되었습니다.

---

### 1. 비전: 왜 CLI 도구인가?

- **단순성 (Simplicity)**: 사용자는 더 이상 소스 코드 구조나 가상 환경에 대해 고민할 필요가 없습니다. 터미널에서 실행되는 하나의 명령어로 모든 기능에 접근할 수 있습니다.
- **접근성 (Accessibility)**: `pip install sogon` 단 한 줄로 설치가 완료됩니다. Python이 설치된 어떤 환경에서든 Sogon을 즉시 사용할 수 있게 됩니다.
- **신뢰성 (Reliability)**: PyPI를 통한 공식 배포는 사용자에게 신뢰를 주며, 체계적인 버전 관리를 통해 안정적인 업데이트를 제공할 수 있습니다.

우리의 목표는 Sogon을 '개발자를 위한 스크립트'에서 '모두를 위한 도구'로 발전시키는 것입니다.

---

### 2. 핵심 기술 스택 및 선정 이유

- **CLI 프레임워크: `Typer`**
  - **선정 이유**: Python의 타입 힌트(Type Hint)를 기반으로 동작하여, 최소한의 코드로 매우 직관적인 CLI를 만들 수 있습니다. 자동 완성 기능과 풍부한 도움말(`--help`) 자동 생성 기능은 사용자 경험을 극대화합니다.

- **패키징 표준: `pyproject.toml` (PEP 517/518)**
  - **선정 이유**: 기존의 `setup.py`를 대체하는 현대적인 Python 패키징 표준입니다. 빌드 시스템과 프로젝트 메타데이터를 명확하게 분리하여, 선언적인 방식으로 패키지를 정의할 수 있습니다.

- **프로젝트 관리 및 빌드 도구: `Hatch` & `Hatchling`**
  - **선정 이유**: `Hatch`는 가상 환경 관리, 빌드, 테스트, 배포를 아우르는 **통합 프로젝트 관리 도구**입니다. `Hatchling`은 그 일부로, 패키지를 빌드하는 백엔드입니다. 이 조합을 통해 `venv`, `build`, `twine` 등 여러 도구를 따로 사용할 필요 없이 `hatch` 명령어 하나로 개발 워크플로우를 통일할 수 있습니다. 또한, '합리적인 기본값(sensible defaults)'을 제공하여 `pyproject.toml` 설정을 매우 간결하게 유지해줍니다.

---

### 3. 세부 실행 계획 (Action Plan)

#### **1단계: `Typer`를 이용한 CLI 엔트리포인트 구현**

현재 `main.py`의 인자 파싱 로직을 `sogon/cli.py`라는 새로운 파일로 이전하고, `Typer`를 사용하여 재구성합니다. (이 단계는 이전 계획과 동일합니다.)

- **`sogon/cli.py` 예시 코드:**
  ```python
  import typer
  from typing_extensions import Annotated
  from sogon import main_processor # 핵심 로직을 담고 있는 모듈

  app = typer.Typer()

  @app.command()
  def run(
      url: Annotated[str, typer.Argument(help="The URL of the YouTube video.")],
      output_dir: Annotated[str, typer.Option("--output-dir", "-o", help="Directory to save the results.")] = None,
      lang: Annotated[str, typer.Option("--lang", "-l", help="Language for transcription.")] = "ko",
  ):
      """
      Downloads a YouTube video, transcribes it, and saves the result.
      """
      typer.echo(f"Processing video from URL: {url}")
      try:
          main_processor.run_workflow(url=url, output_dir=output_dir, lang=lang)
          typer.secho("Workflow completed successfully!", fg=typer.colors.GREEN)
      except Exception as e:
          typer.secho(f"An error occurred: {e}", fg=typer.colors.RED)
          raise typer.Exit(code=1)

  if __name__ == "__main__":
      app()
  ```

#### **2단계: `pyproject.toml` 설정 및 종속성 정의 (Hatchling 적용)**

`Hatchling`을 빌드 백엔드로 사용하도록 `pyproject.toml`을 구성합니다. `setuptools`에 비해 훨씬 간결합니다.

- **`pyproject.toml` 설정 예시:**
  ```toml
  [build-system]
  requires = ["hatchling"]
  build-backend = "hatchling.build_meta"

  [project]
  name = "sogon"
  version = "0.1.0"
  authors = [
    { name="Your Name", email="your.email@example.com" },
  ]
  description = "A tool to download, transcribe, and process YouTube videos."
  readme = "README.md"
  requires-python = ">=3.8"
  classifiers = [
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
  ]
  dependencies = [
      "typer[all]",
      "youtube-dl",
      "openai-whisper",
      "torch",
      # ... 기타 모든 종속성
  ]

  [project.urls]
  "Homepage" = "https://github.com/your-repo/sogon"
  "Bug Tracker" = "https://github.com/your-repo/sogon/issues"

  # 이 부분이 `sogon` 명령어를 생성하는 핵심입니다.
  [project.scripts]
  sogon = "sogon.cli:app"
  ```
  *Hatchling은 `sogon` 디렉토리를 자동으로 패키지로 인식하므로 별도의 패키지 검색 설정이 필요 없습니다.*

#### **3단계: 로컬 빌드 및 검증 (Hatch 사용)**

`Hatch`를 사용하여 개발 환경을 구성하고, 빌드 및 테스트를 진행합니다.

1.  **`Hatch` 설치**: `pip install hatch`
2.  **패키지 빌드**: `hatch build`
    - 이 명령은 `dist/` 디렉토리에 `sdist`와 `wheel` 파일을 생성합니다.
3.  **`Hatch` 환경에서 테스트**:
    - `hatch`는 프로젝트별로 격리된 가상 환경을 자동으로 관리합니다.
    - `hatch run sogon --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --lang en`
    - 위 명령은 `hatch`가 관리하는 가상 환경에 종속성을 설치하고 `sogon` 명령어를 실행합니다.
    - 도움말 확인: `hatch run sogon --help`

#### **4단계: CI/CD 파이프라인 강화 (Hatch 사용)**

`.github/workflows/ci.yml`에 `Hatch`를 사용하는 빌드 및 검증 단계를 추가합니다.

- **`ci.yml`에 추가될 스텝 예시:**
  ```yaml
  - name: Set up Python
    uses: actions/setup-python@v4
    with:
      python-version: '3.10'

  - name: Install Hatch
    run: pip install hatch

  - name: Build package
    run: hatch build
  ```
Git 태그 생성 시 PyPI에 배포하는 워크플로우(`release.yml`)도 `hatch publish` 명령어를 사용하도록 구성하여 단순화할 수 있습니다.

#### **5단계: PyPI 배포 (Hatch 사용)**

`twine` 대신 `hatch`의 내장 배포 명령어를 사용합니다.

1.  **TestPyPI를 통한 예행연습**:
    - `hatch publish --repo test` 명령으로 TestPyPI에 업로드하여 배포 과정을 최종 점검합니다.
2.  **공식 PyPI 배포**:
    - 모든 것이 완벽하다면, `hatch publish` 명령으로 전 세계 사용자들이 `pip`를 통해 설치할 수 있도록 공식 PyPI에 Sogon을 등록합니다.

---

### 4. 기대 효과 및 향후 계획

이 계획이 성공적으로 완료되면, Sogon은 더 이상 소수의 개발자를 위한 코드가 아닌, **전 세계 누구나 쉽게 사용할 수 있는 강력한 미디어 처리 도구**로 거듭날 것입니다.

- **사용자층 확대**: 설치 장벽 제거를 통해 비개발자, 연구원, 콘텐츠 제작자 등 새로운 사용자층을 유입시킬 수 있습니다.
- **개발 경험 향상**: `Hatch`를 통해 프로젝트 관리 및 배포 워크플로우를 통합하여 개발 효율성을 높입니다.
- **커뮤니티 활성화**: 쉬운 접근성은 더 많은 사용자의 피드백과 기능 제안, 코드 기여(Contribution)로 이어질 수 있습니다.
- **지속 가능한 프로젝트**: 표준화된 배포 파이프라인은 향후 기능 추가 및 유지보수를 훨씬 효율적으로 만듭니다.

이 로드맵을 시작으로, Sogon 프로젝트의 새로운 장을 열고자 합니다. 진행 상황은 계속해서 공유드리겠습니다.

감사합니다.