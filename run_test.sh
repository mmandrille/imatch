#!/bin/bash
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 
# You can pass like to pytest
# a folder, or test file to test only that
# Example: 
#   ./tests.sh resources/brands/tests/test_brands.py
# 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
clear
printf "TESTING: $(pwd)\n"
printf "YOU SHOULD RUN THIS ON enviroments/local, Inside VIRTUAL ENVIROMENT:"

printf "\n\nStarting containers\n"
docker-compose -f docker-compose.yml up --build --detach --remove-orphans

printf "\n\nCheck Pip8\n"
pycodestyle

printf "\n\nRunning Tests\n"
python wait_for_imatch.py
pytest $1 $2

# printf "\n\nStoping containers"
# docker-compose -f docker-compose.yml down