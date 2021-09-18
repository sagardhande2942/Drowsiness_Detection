import firebase_admin

# Firebase authentication
cred_obj = firebase_admin.credentials.Certificate('drowsinessdetection-c0493-firebase-adminsdk-qeyqj-74ccb3f0e6.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':'https://drowsinessdetection-c0493-default-rtdb.firebaseio.com/'
	})