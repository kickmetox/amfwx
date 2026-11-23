from amfwx import scan_network
for ep in scan_network("192.168.178.0/24", ports=(9096,443,8443,80,631), timeout=0.35):
    print(ep)
