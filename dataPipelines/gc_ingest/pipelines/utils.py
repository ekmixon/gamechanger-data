import sys

def announce(text: str):
    print(f"#### PIPELINE INFO #### {text}", file=sys.stderr)