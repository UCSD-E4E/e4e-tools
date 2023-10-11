# Onboarding Application Extractor
```
usage: onboarding_app_extractor.py [-h] -p {aid,bom,fs,mm,rct,sf,rsg} -r RESPONSES -o OUTPUT_DIR

options:
  -h, --help            show this help message and exit
  -p {aid,bom,fs,mm,rct,sf,rsg}, --project {aid,bom,fs,mm,rct,sf,rsg}
  -r RESPONSES, --responses RESPONSES
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
```

Example usage:
```
$ python onboarding_app_extractor.py -p rsg -r '.\E4E Onboarding (Responses) - Form Responses 1.csv' -o rsg
```
