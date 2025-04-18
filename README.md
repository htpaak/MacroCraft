# MacroCraft

고급 기능을 갖춘 매크로 녹화 및 실행 프로그램입니다. 키보드와 마우스 입력을 정확하게 녹화하고 편집하여 반복 작업을 자동화할 수 있습니다.

## 주요 기능

- **다양한 입력 이벤트 녹화**: 키보드 입력, 마우스 클릭, 마우스 이동, 스크롤 등 모든 입력 이벤트 녹화
- **실시간 녹화 모니터링**: 녹화 중 발생하는 이벤트를 실시간으로 확인 가능
- **딜레이 이벤트 지원**: 이벤트 간 시간 간격을 독립적인 딜레이 이벤트로 관리
- **이벤트 편집 기능**: 녹화된 이벤트의 삭제, 복제, 딜레이 추가 등 다양한 편집 기능
- **상대/절대 좌표 지원**: 화면 위치에 상관없이 작동하는 상대 좌표 모드 지원
- **매크로 저장 및 관리**: 여러 매크로를 저장하고 불러와 사용 가능
- **다양한 반복 옵션**: 매크로 실행 시 원하는 횟수만큼 반복 가능

## 설치 및 실행

```bash
# 필요 라이브러리 설치
pip install keyboard mouse PySimpleGUI

# 프로그램 실행
python main.py
```

## 모듈 구성

- **main.py**: 프로그램 진입점
- **recorder.py**: 키보드/마우스 이벤트 녹화 모듈
- **player.py**: 매크로 실행 모듈
- **editor.py**: 매크로 편집 기능 모듈
- **storage.py**: 매크로 저장 및 불러오기 모듈
- **gui.py**: 사용자 인터페이스 모듈

## 사용법

1. '녹화' 버튼을 클릭하여 새 매크로 녹화 시작
2. 원하는 동작 수행 (키보드 입력, 마우스 클릭 등)
3. '중지' 버튼을 클릭하여 녹화 종료
4. 녹화된 이벤트 편집 (필요한 경우)
5. '저장' 버튼을 클릭하여 매크로 저장
6. 매크로 목록에서 원하는 매크로를 선택하여 '실행' 버튼 클릭

## 라이센스

MIT License
