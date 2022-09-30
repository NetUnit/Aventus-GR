init.py - serves to improve imports inside current directory
# create empty file
__init__.py

# virtual env create
python3 -m venv .
source bin/activate

# then install requiremnts
pip install -r requirements.txt

# check installed modules
pip freeze

# create your environment
python-decouple==3.6 - is installed from requirements (pip install python-decouple)
sudo touch .env
put variables into your .env file
like here: http://joxi.net/V2VPRbGiG7ZKjr
