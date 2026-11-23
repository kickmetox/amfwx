from amfwx import AppConfig
print(AppConfig.parse(['--list-cameras']).list_cameras)
print(AppConfig.parse(['--camera-tether','x','--camera-frames','2']).camera_frames)
