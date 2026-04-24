# DATA RULES

## 1. 공통 데이터 파일
차세대 모바일과 데스크톱은 아래 파일만 공통 기준으로 사용한다.

- data/timetable.csv
- data/academic_calendar.csv
- data/version.json

## 2. 시간표 파일 규칙
파일명:
- data/timetable.csv

헤더:
- teacher
- day
- period
- subject

설명:
- 한 줄은 하나의 수업 정보를 의미한다.
- teacher는 교사명이다.
- day는 월, 화, 수, 목, 금 중 하나여야 한다.
- period는 숫자여야 한다.
- subject는 과목명 또는 공강 등의 문자열이다.

예시:
- 표민호,월,1,통합과학
- 표민호,수,3,공강

검증 규칙:
- 필수 헤더가 하나라도 없으면 오류로 본다.
- day 값이 월, 화, 수, 목, 금이 아니면 오류로 본다.
- period가 숫자가 아니면 오류로 본다.
- teacher 또는 subject가 비어 있으면 오류로 본다.

## 3. 학사일정 파일 규칙
파일명:
- data/academic_calendar.csv

헤더:
- date
- event

설명:
- 한 줄은 하나의 날짜 일정이다.
- date는 YYYY-MM-DD 형식이어야 한다.
- event는 일정 이름이다.

예시:
- 2026-03-02,개학
- 2026-05-05,어린이날

검증 규칙:
- 필수 헤더가 하나라도 없으면 오류로 본다.
- date 형식이 YYYY-MM-DD가 아니면 오류로 본다.
- event가 비어 있으면 오류로 본다.
- 같은 date가 중복되면 경고 대상으로 본다.

## 4. 버전 파일 규칙
파일명:
- data/version.json

필수 키:
- app_min_version
- data_version
- updated_at
- files

files 내부 필수 키:
- timetable
- calendar

검증 규칙:
- 필수 키가 없으면 오류로 본다.
- files 안의 경로는 실제 저장소 구조와 일치해야 한다.

## 5. 앱 동작 원칙
- 모바일과 데스크톱은 같은 데이터 규칙을 사용한다.
- 새 데이터를 받았을 때 먼저 검증하고, 통과하면 반영한다.
- 검증 실패 시 기존 데이터를 유지한다.
- 데이터 일부가 잘못되어도 앱 전체가 바로 종료되지 않도록 설계한다.
- 사용자에게는 가능한 한 쉬운 오류 안내 문구를 보여준다.

## 6. 차세대 1차 버전의 범위
- 먼저 읽기 전용으로 안정화한다.
- 편집 기능은 나중 단계로 미룬다.
- 복잡한 자동 변환 기능은 나중 단계로 미룬다.
