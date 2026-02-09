@echo off
echo Running Warranty Migration...
.venv\Scripts\alembic.exe upgrade head
pause
