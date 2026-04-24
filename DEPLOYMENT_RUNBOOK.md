# MyTimetableNext 운영·배포 가이드

이 문서는 차세대 시간표 앱을 배포하고, 신학기 시간표·학사일정을 업데이트할 때 사용하는 운영 절차입니다.

---

## 1. 현재 구조 요약

### 공통 원칙

- PC 앱과 모바일 웹뷰어는 같은 Supabase 데이터를 사용합니다.
- 기존 PC 레거시 UI와 모바일 레거시 UI는 최대한 유지합니다.
- 시간표와 학사일정은 Supabase를 우선 사용하고, 문제가 있을 때는 `data` 폴더의 CSV를 fallback으로 사용합니다.
- Supabase 키가 들어 있는 `supabase_config.json`은 GitHub에 올리지 않습니다.

### 주요 폴더

```text
my-timetable-next/
├─ assets/                         로고, 아이콘
├─ build/                          빌드 설정 및 설치 스크립트
├─ data/                           fallback CSV 데이터
├─ desktop/                        PC 앱
├─ mobile/                         Streamlit 모바일 웹뷰어
├─ tools/                          관리자용 도구
└─ releases/                       로컬 배포 패키지 폴더, GitHub에는 올리지 않음
```

---

## 2. 교사용 PC 설치 안내

교사에게 배포할 기본 파일은 GitHub Release에 올린 설치파일입니다.

```text
MyTimetableNextSetup_v2.0.0.exe
```

### 설치 순서

1. 기존 설치본이 있으면 먼저 제거합니다.
   - Windows 설정 > 앱 > 설치된 앱
   - `명덕외고 시간표` 또는 `MyTimetableNext` 제거

2. 새 설치파일을 실행합니다.

3. 설치 후 앱을 실행합니다.

4. 첫 실행 후 확인합니다.
   - 시간표가 보이는지
   - 학사일정이 보이는지
   - 메모가 보이는지
   - 설정 > 업데이트 확인 / 데이터 새로고침 작동 여부

---

## 3. 모바일 웹뷰어 배포 안내

Streamlit Cloud 설정값은 다음과 같습니다.

```text
Repository: vyalsgh-tech/my-timetable-next
Branch: main
Main file path: mobile/app.py
```

Streamlit Secrets에는 아래 2개가 필요합니다.

```toml
SUPABASE_URL = "https://프로젝트주소.supabase.co"
SUPABASE_KEY = "Supabase anon key"
```

모바일 웹뷰어에서 문제가 생기면 다음을 확인합니다.

1. Streamlit Secrets가 입력되어 있는지
2. Supabase RLS 정책이 허용되어 있는지
3. `timetable_entries`, `academic_calendar`, `memos`, `custom_schedule`, `users` 테이블이 있는지
4. 모바일 앱이 최신 GitHub main 브랜치를 보고 있는지

---

## 4. 신학기 시간표 업데이트 절차

신학기 또는 중간 시간표 변경 시에는 PC 앱을 새로 배포하지 않고 Supabase 데이터만 갱신하면 됩니다.

### 1단계. CSV 교체

아래 두 파일을 최신 자료로 교체합니다.

```text
data/timetable.csv
data/academic_calendar.csv
```

형식은 반드시 다음과 같아야 합니다.

### timetable.csv

```csv
teacher,day,period,subject
표민호,월,1,통합과학
```

### academic_calendar.csv

```csv
date,event
2026-03-02,개학
```

---

### 2단계. Supabase 업데이트 도구 실행

저장소 루트에서 실행합니다.

```bat
cd /d Z:\1_Work_MH\0_2026\시간표앱_차세대\my-timetable-next
python tools\admin_update_supabase_data.py
```

업데이트 방식은 보통 다음 중 하나를 선택합니다.

```text
1. 안전 갱신
2. 전체 교체
```

권장 기준:

- 일부 교사 시간표만 수정: `1. 안전 갱신`
- 신학기 전체 시간표 교체: `2. 전체 교체`

단, 전체 교체를 해도 아래 테이블은 건드리지 않습니다.

```text
users
memos
custom_schedule
```

즉, 사용자 계정, 메모, 개인 수정 시간표는 유지됩니다.

---

### 3단계. 반영 확인

PC 앱:

```text
설정 > 업데이트 확인 / 데이터 새로고침
```

모바일 웹뷰어:

```text
브라우저 새로고침
```

---

## 5. PC 앱 재빌드 절차

PC 앱 코드가 바뀌었거나 설치파일을 새로 만들어야 할 때 사용합니다.

### 1단계. 빌드 실행

```bat
cd /d Z:\1_Work_MH\0_2026\시간표앱_차세대\my-timetable-next
build\build_pc_release.bat
```

### 2단계. EXE 확인

아래 파일을 직접 실행합니다.

```text
dist\MyTimetableNext.exe
```

확인할 것:

- 기존 레거시 UI로 보이는지
- 시간표가 보이는지
- 메모가 보이는지
- 설정 > 업데이트 확인 / 데이터 새로고침이 작동하는지

### 3단계. 설치파일 확인

Inno Setup이 설치되어 있으면 아래 파일이 생성됩니다.

```text
dist\installer\MyTimetableNextSetup.exe
```

이 설치파일을 실행해 설치 후에도 동일하게 정상 작동하는지 확인합니다.

---

## 6. 배포 패키지 생성 절차

빌드가 끝난 뒤 배포용 폴더를 정리합니다.

```bat
python tools\make_release_package.py
```

생성 위치:

```text
releases/
└─ MyTimetableNext_v2.0.0_data2026.2.0_YYYYMMDD/
```

포함 파일:

```text
MyTimetableNextSetup_v2.0.0.exe
MyTimetableNext_v2.0.0.exe
version.json
SHA256SUMS.txt
RELEASE_NOTES.txt
```

`releases/` 폴더는 GitHub 코드 저장소에는 올리지 않습니다.  
GitHub Releases 첨부파일로만 올립니다.

---

## 7. GitHub Release 생성 절차

GitHub 저장소 오른쪽의 `Releases`에서 `Create a new release`를 누릅니다.

### Tag

```text
v2.0.0
```

### Title

```text
MyTimetableNext v2.0.0
```

### Description 예시

```text
차세대 명덕외고 시간표 앱 v2.0.0

주요 내용
- 기존 PC 레거시 UI 유지
- Supabase 기반 시간표/학사일정 연동
- 모바일 Streamlit 웹뷰어 연동
- 관리자용 Supabase 데이터 업데이트 도구 추가
- PC 설치파일 생성
```

### 첨부 파일

`releases` 폴더에서 생성된 배포 폴더 안의 파일을 첨부합니다.

```text
MyTimetableNextSetup_v2.0.0.exe
MyTimetableNext_v2.0.0.exe
version.json
SHA256SUMS.txt
RELEASE_NOTES.txt
```

---

## 8. Git 커밋 기준

### GitHub에 올려도 되는 것

```text
assets/
build/
data/
desktop/
mobile/
tools/
README.md
DATA_RULES.md
FEATURES_TO_KEEP.md
FILE_ROLE_MAP.md
NEXT_STEPS.md
DEPLOYMENT_RUNBOOK.md
```

### GitHub에 올리면 안 되는 것

```text
supabase_config.json
.streamlit/secrets.toml
dist/
releases/
reports/
build/timetable/
*.exe
*.msi
```

---

## 9. 문제 발생 시 빠른 점검

### PC 앱에서 시간표가 안 보일 때

1. `data/timetable.csv`가 있는지 확인
2. Supabase `timetable_entries`에 데이터가 있는지 확인
3. 설정 > 업데이트 확인 / 데이터 새로고침 실행
4. `desktop/timetable.pyw` 직접 실행 후 EXE와 차이 비교

### 설치 후 UI가 이상할 때

1. `python desktop\timetable.pyw`로 원본 UI 확인
2. `build/timetable.spec`가 `desktop/timetable.pyw`를 빌드 대상으로 잡는지 확인
3. `dist`와 `build/timetable`을 삭제 후 재빌드

### 모바일 웹뷰어가 안 뜰 때

1. Streamlit Cloud logs 확인
2. Secrets 입력 확인
3. Supabase RLS 확인
4. GitHub main 브랜치 최신 반영 확인

---

## 10. 현재 안정 버전

```text
앱 버전: 2.0.0
데이터 버전: 2026.2.0
기준 브랜치: main
배포 방식: GitHub Releases + Supabase 데이터 업데이트
```
