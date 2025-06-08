@echo off

REM Set console color to green on black
color 0A

echo.
echo ===============================
echo   Git Sync: Source -> Target
echo ===============================
echo.

REM Enable delayed expansion for variable operations
setlocal EnableDelayedExpansion

REM Prompt for source repository URL
set /p SRCURL=Enter source repository URL (you may include or omit "https://"): 
if /I "!SRCURL:~0,8!"=="https://" (
    set "FULLSRC=!SRCURL!"
) else (
    set "FULLSRC=https://!SRCURL!"
)

REM Prompt for destination repository URL
set /p DESTURL=Enter destination repository URL (you may include or omit "https://"): 
if /I "!DESTURL:~0,8!"=="https://" (
    set "FULLDEST=!DESTURL!"
) else (
    set "FULLDEST=https://!DESTURL!"
)

REM Prompt for commit message
set /p COMMITMSG=Enter commit message: 

echo.
echo Cloning source repository...
git clone "%FULLSRC%" src_temp --quiet || (
    echo Error: Failed to clone source. Exiting.& pause & exit /b 1
)
echo.
echo Cloning destination repository...
git clone "%FULLDEST%" dest_temp --quiet || (
    echo Error: Failed to clone destination. Exiting.& pause & exit /b 1
)
echo.
echo Copying files (this may take a moment)...
robocopy src_temp dest_temp /MIR /XD .git >nul
echo.
echo Creating commit in destination repository...
pushd dest_temp
git add .
git commit -m "%COMMITMSG%" || echo No changes to commit.

echo Pushing changes to remote...
git push origin HEAD --quiet || (
    echo Error: Failed to push changes.& pause & popd & exit /b 1
)
popd
echo.
echo Cleaning up temporary folders...
rd /s /q src_temp
rd /s /q dest_temp
if exist Target del /f "Target"
echo.
echo ===============================
echo     Operation Completed!
echo ===============================
echo.
pause