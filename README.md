# Prerequisites
1.
```bash
cd auto-booking
python3 -m venv venv
pip install -r requirements.txt
```

2. create your own `.env` file in the auto-booking directory, based on the provided .env.example:
```bash
cp .env.example .env
```

# Run
```bash
bash run_main.sh
```
# Stop
```bash
bash stop_main.py
```
# Log
```bash
tail -f .../auto-booking/log/process_0.log
```
