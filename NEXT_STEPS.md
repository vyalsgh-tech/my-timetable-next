# NEXT STEPS

## 차세대 버전 개발 원칙
- 현재 운영 중인 기존 저장소는 건드리지 않는다.
- 차세대 저장소에서만 새 구조를 개발한다.
- 기존 원본 코드는 보관용(legacy)으로만 유지한다.
- 새 코드는 legacy 파일을 직접 수정하지 않고 별도 파일로 만든다.
- 에러 최소화를 최우선으로 한다.
- 데스크톱 앱과 모바일 뷰어는 공통 데이터 구조를 사용한다.
- 시간표와 학사일정 데이터는 GitHub의 data 폴더 기준으로 관리한다.
- 업데이트 기능은 data/version.json을 기준으로 동작하게 설계한다.

## 현재 보관된 원본
- mobile/legacy_app.py
- desktop/legacy_timetable.pyw

## 현재 공통 데이터 파일
- data/timetable.csv
- data/academic_calendar.csv
- data/version.json

## 다음 작업 순서
1. 모바일과 데스크톱의 유지 기능 목록 정리
2. 차세대 공통 데이터 규칙 확정
3. 모바일 차세대 app.py 초안 작성
4. 데스크톱 차세대 timetable.pyw 초안 작성
5. GitHub 데이터 업데이트 기능 추가
6. 설치형 배포 구조 준비
