# FILE ROLE MAP

## 1. 현재 기준 원본 보관 파일
- mobile/legacy_app.py
  - 기존 운영 중인 모바일 앱 원본 보관용
  - 직접 수정하지 않는다
  - 차세대 모바일 코드 작성 시 참고만 한다

- desktop/legacy_timetable.pyw
  - 기존 운영 중인 데스크톱 앱 원본 보관용
  - 직접 수정하지 않는다
  - 차세대 데스크톱 코드 작성 시 참고만 한다

## 2. 앞으로 만들 차세대 실행 파일
- mobile/app.py
  - 차세대 모바일 뷰어 실행 파일
  - legacy_app.py를 직접 덮어쓰지 않고 새로 만든다

- desktop/timetable.pyw
  - 차세대 데스크톱 실행 파일
  - legacy_timetable.pyw를 직접 덮어쓰지 않고 새로 만든다

## 3. 공통 데이터 파일
- data/timetable.csv
  - 공통 시간표 데이터

- data/academic_calendar.csv
  - 공통 학사일정 데이터

- data/version.json
  - 데이터 버전 및 업데이트 기준 파일

## 4. 공통 자산 파일
- assets/logo.ico
- assets/logo.png

## 5. 작업 원칙
- legacy 파일은 보관용이며 직접 수정하지 않는다
- 새 기능은 반드시 새 실행 파일에만 반영한다
- 모바일과 데스크톱은 공통 데이터 구조를 사용한다
- 기존 운영 저장소는 계속 별도로 유지한다
