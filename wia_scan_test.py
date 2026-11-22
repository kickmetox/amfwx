from amfwx import WiaScanner
try: WiaScanner(device_id='x').acquire('x.png')
except Exception as e: print(type(e).__name__, e)
