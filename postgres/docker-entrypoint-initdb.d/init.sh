psql -U postgres -c " CREATE EXTENSION vector;"

# The only way to load the env, I'm unable (yet) to load env variables
# with something like export asd="{asd}"
# is not reading the env variables in the format {asd}
source ./.env
python3 01_insert_data.py 