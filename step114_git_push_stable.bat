@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

REM ============================================================
REM Step114: 현재 안정 상태 GitHub 업로드용
REM 위치: 프로젝트 루트에서 실행
REM Y:\0_2026\시간표앱_차세대\my-timetable-next
REM ============================================================

cd /d "%~dp0"

echo ============================================================
echo Step114 GitHub 업로드 시작
echo 현재 폴더: %cd%
echo ============================================================
echo.

git --version > nul 2>&1
if errorlevel 1 (
    echo [오류] Git이 설치되어 있지 않거나 PATH에 없습니다.
    echo Git 설치 후 다시 실행하세요.
    pause
    exit /b 1
)

if not exist ".git" (
    echo [안내] 현재 폴더가 Git 저장소가 아닙니다. git init을 실행합니다.
    git init
    echo.
)

echo [1] 현재 Git 상태
git status --short
echo.

echo [2] 민감 파일 포함 여부 간단 점검
git status --short | findstr /i ".env secrets.toml service_role private_key api_key key.json" > nul
if not errorlevel 1 (
    echo.
    echo [주의] .env, secrets.toml, key 관련 파일이 변경 목록에 보입니다.
    echo Supabase URL은 괜찮을 수 있지만, API KEY / SERVICE ROLE KEY / 비밀번호가 포함되면 안 됩니다.
    echo.
    choice /c YN /m "그래도 계속 진행할까요? Y=진행, N=중단"
    if errorlevel 2 (
        echo [중단] 민감 파일 확인 후 다시 실행하세요.
        pause
        exit /b 1
    )
)

echo.
echo [3] 원격 저장소 확인
git remote -v
echo.

git remote get-url origin > nul 2>&1
if errorlevel 1 (
    echo [오류] origin 원격 저장소가 설정되어 있지 않습니다.
    echo.
    echo GitHub에서 저장소를 만든 뒤 아래 명령을 직접 실행하세요.
    echo 예시:
    echo git remote add origin https://github.com/사용자명/저장소명.git
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%b in ('git branch --show-current') do set BRANCH=%%b
if "%BRANCH%"=="" set BRANCH=main

echo [4] 현재 브랜치: %BRANCH%
echo.

set COMMIT_MSG=step114: stable web viewer after Step112
set /p USER_MSG=커밋 메시지를 바꾸려면 입력하세요. 그냥 Enter면 기본값 사용: 
if not "%USER_MSG%"=="" set COMMIT_MSG=%USER_MSG%

echo.
echo [5] 변경 파일 추가
git add .
if errorlevel 1 (
    echo [오류] git add 실패
    pause
    exit /b 1
)

echo.
echo [6] 커밋 생성
git diff --cached --quiet
if not errorlevel 1 (
    echo [안내] 커밋할 변경사항이 없습니다.
) else (
    git commit -m "%COMMIT_MSG%"
    if errorlevel 1 (
        echo [오류] git commit 실패
        pause
        exit /b 1
    )
)

echo.
echo [7] GitHub로 push
git push -u origin %BRANCH%
if errorlevel 1 (
    echo.
    echo [오류] push 실패
    echo 원인 후보:
    echo - GitHub 로그인이 안 되어 있음
    echo - origin 주소가 잘못됨
    echo - 브랜치명이 GitHub 기본 브랜치와 다름
    echo - 원격 저장소에 먼저 올라간 커밋이 있음
    echo.
    echo 상태 확인:
    echo git remote -v
    echo git branch --show-current
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [완료] GitHub 업로드가 끝났습니다.
echo ============================================================
pause
