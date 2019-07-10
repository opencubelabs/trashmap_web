from bottle import Bottle, run, route, static_file, request, response, template, redirect, get, post
from pymongo import MongoClient
from bson.json_util import dumps
from botocore.exceptions import ClientError
from bson.objectid import ObjectId
from string import Template
from pprint import pprint
import json
import pymongo
import datetime
import time
import math
import hashlib as hl
import os
import smtplib
import boto3
import uuid

app = Bottle(__name__)

client = MongoClient()
db = client.server

# Static Routes
@app.route('/<filename:re:.*\.html>')
def javascripts(filename):
	return static_file(filename, root='templates')

@app.route('/<filename:re:.*\.js>')
def javascripts(filename):
	return static_file(filename, root='static')

@app.route('/<filename:re:.*\.css>')
def stylesheets(filename):
	return static_file(filename, root='static')

@app.route('/<filename:re:.*\.(jpg|png|gif|ico|svg)>')
def images(filename):
	return static_file(filename, root='static')

@app.route('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
	return static_file(filename, root='static')

@app.route('/<filename:re:.*\.html>')
def javascripts(filename):
	return static_file(filename, root='static')

@app.route('/<filename:re:.*\.pdf>')
def pdfs(filename):
	return static_file(filename, root='static')

@app.route('/<filename:re:.*\.json>')
def javascripts(filename):
	return static_file(filename, root='static')

@app.route('/<filename:re:.*\.geojson>')
def geojson(filename):
	return static_file(filename, root='static')

@app.hook('after_request')
def enable_cors():
	response.headers['Access-Control-Allow-Origin'] = '*'
	response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
	response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


#index.html home page
@app.get('/')
def root():
	return static_file('index.html', root='templates/')


#login.html credentials look-up
@app.get('/login')
def login():
	return static_file('login.html', root='templates/')

@app.post('/login')
def login():
	username = request.forms.get('uname')
	password = request.forms.get('psw')

	hashpass1 = hl.sha256(password).hexdigest()
	
	cur = db.signupTable.find({'Username': username})
	data = json.loads(dumps(cur))
	
	if(len(data) != 0):
		if(data[0]["Password"] == hashpass1):
			redirect('/')
			#return {'status': 'User authenticated!', 'uname': username}
		else:
			return {'status': 'Invalid credentials'}
	else:
		return {'status': "User dosen't exist"}


#signup.html credentials
@app.get('/signup')
def signup():
	return static_file('signup.html', root='templates/')

@app.post('/signup')
def signup():
	fname = request.forms.get('fname')
	lname = request.forms.get('lname')
	username = request.forms.get('uname')
	password = hl.sha256(request.forms.get('psw')).hexdigest()
	email = request.forms.get('email')

	db.signupTable.insert_one({'First Name' : fname , 'Last Name' : lname , 'Username' : username , 'Password' : password , 'Email ID' : email})

	return "success"


#map-streets.html - map view
@app.get('/map')
def map():
	return static_file('map-streets.html', root='templates/')


#@app.get('/test_file')
#def test():
#	return static_file('test.html', root='templates/')

@app.get('/test')
def test():
	lati = float(request.GET.get('lati'))
	longi = float(request.GET.get('longi'))

	#print(lati)
	#print(longi)
	dust = []
	#db.test.insert_one({'Latitude' : lati , 'Longitude' : longi})
	x = db.dustbin2.find({"geometry" : {"$nearSphere" : {"$geometry" : {"type" : "Point", "coordinates" : [ longi, lati ]}, "$maxDistance" : 500}}});
	for doc in x:
		data = json.loads(dumps(doc))
		#print(data)
		dust.append(data)
	abc= {'dustbins' : dust} 
	#pprint(abc)
	return abc
	#message = {'greetings' : 'Hello from trashSalman!!!'}
	#return json.loads(dumps(message))


#Credentials for dustbin details
@app.get('/dustbins')
def dustbins():
	return static_file('build-streets.js', root='static/')

@app.post('/dustbins')
def dustbins():
	dtype = request.forms.get('dtype')
	yn = request.forms.get('access')
	lati = float(request.forms.get('lati'))
	longi = float(request.forms.get('long'))

	db.dustbin2.insert_one({"type": "Feature",
	"properties": {
		"dtype" : dtype,
		"access": yn
	},
	"geometry": {
		"type": "Point",
		"coordinates": [
			longi,
			lati
		]
	}})
	redirect('/map')


"""@app.route('/images3')
def images3():
	S3_BUCKET = 'trashmap2'

	file_name = request.GET.get('file_name') + '-' + uuid.uuid4().hex
	file_type = request.GET.get('file_type')
	folder_name = 'files'

	s3 = boto3.client('s3', region_name='us-east-1', aws_access_key_id=os.environ['aws_access_key_id'], aws_secret_access_key=os.environ['aws_secret_access_key'])

	presigned_post = s3.generate_presigned_post(
		Bucket = S3_BUCKET,
		Key = folder_name+'/'+file_name,
		Fields = {"acl": "public-read", "Content-Type": file_type},
		Conditions = [
		  {"acl": "public-read"},
		  {"Content-Type": file_type}
		],
		ExpiresIn = 3600
	)

	# print presigned_post

	return json.dumps({
	'data': presigned_post,
	'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, folder_name+'/'+file_name)
})"""


#team.html team members
@app.get('/team')
def team():
	return static_file('team.html', root='templates/')


#opportunities.html opportunities page
@app.get('/opportunities')
def opportunities():
	return static_file('opportunities.html', root='templates/')


#email api
@app.get('/message')
def message():
	return static_file('index.html', root='templates/')

@app.post('/message')
def message():
	name = request.forms.get('name')
	email = request.forms.get('email')
	subject = request.forms.get('subject')
	message = request.forms.get('mesg')

	db.messagedata.insert_one({'name' : name , 'email' : email , 'subject' : subject , 'message' : message})
	
	SENDER = "TrashMap <hello@ocl.space>"

# Replace recipient@example.com with a "To" address. If your account 
# is still in the sandbox, this address must be verified.
	RECIPIENT = email

# Specify a configuration set. If you do not want to use a configuration
# set, comment the following variable, and the 
# ConfigurationSetName=CONFIGURATION_SET argument below.
#CONFIGURATION_SET = "ConfigSet"

# If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
	AWS_REGION = "region"

# The subject line for the email.
	SUBJECT = subject
			
# The HTML body of the email.
	BODY_HTML = """<!doctype html>
<html>
  <head>
	<meta name="viewport" content="width=device-width" />
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<title>TrashMap</title>
	<style>
	  img {
		border: none;
		-ms-interpolation-mode: bicubic;
		max-width: 100%; 
	  }

	  body {
		background-color: #f6f6f6;
		font-family: sans-serif;
		-webkit-font-smoothing: antialiased;
		font-size: 14px;
		line-height: 1.4;
		margin: 0;
		padding: 0;
		-ms-text-size-adjust: 100%;
		-webkit-text-size-adjust: 100%; 
	  }

	  table {
		border-collapse: separate;
		mso-table-lspace: 0pt;
		mso-table-rspace: 0pt;
		width: 100%; }
		table td {
		  font-family: sans-serif;
		  font-size: 14px;
		  vertical-align: top; 
	  }

	  .body {
		background-color: #f6f6f6;
		width: 100%; 
	  }

	  /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
	  .container {
		display: block;
		margin: 0 auto !important;
		/* makes it centered */
		max-width: 580px;
		padding: 10px;
		width: 580px; 
	  }

	  /* This should also be a block element, so that it will fill 100% of the .container */
	  .content {
		box-sizing: border-box;
		display: block;
		margin: 0 auto;
		max-width: 580px;
		padding: 10px; 
	  }

	  /* -------------------------------------
		  HEADER, FOOTER, MAIN
	  ------------------------------------- */
	  .main {
		background: #ffffff;
		border-radius: 3px;
		width: 100%; 
	  }

	  .wrapper {
		box-sizing: border-box;
		padding: 20px; 
	  }

	  .content-block {
		padding-bottom: 10px;
		padding-top: 10px;
	  }

	  .footer {
		clear: both;
		margin-top: 10px;
		text-align: center;
		width: 100%; 
	  }
		.footer td,
		.footer p,
		.footer span,
		.footer a {
		  color: #999999;
		  font-size: 12px;
		  text-align: center; 
	  }

	  /* -------------------------------------
		  TYPOGRAPHY
	  ------------------------------------- */
	  h1,
	  h2,
	  h3,
	  h4 {
		color: #000000;
		font-family: sans-serif;
		font-weight: 400;
		line-height: 1.4;
		margin: 0;
		margin-bottom: 30px; 
	  }

	  h1 {
		font-size: 35px;
		font-weight: 300;
		text-align: center;
		text-transform: capitalize; 
	  }

	  p,
	  ul,
	  ol {
		font-family: sans-serif;
		font-size: 14px;
		font-weight: normal;
		margin: 0;
		margin-bottom: 15px; 
	  }
		p li,
		ul li,
		ol li {
		  list-style-position: inside;
		  margin-left: 5px; 
	  }

	  a {
		color: #3498db;
		text-decoration: underline; 
	  }

	  /* -------------------------------------
		  BUTTONS
	  ------------------------------------- */
	  .btn {
		box-sizing: border-box;
		width: 100%; }
		.btn > tbody > tr > td {
		  padding-bottom: 15px; }
		.btn table {
		  width: auto; 
	  }
		.btn table td {
		  background-color: #ffffff;
		  border-radius: 5px;
		  text-align: center; 
	  }
		.btn a {
		  background-color: #ffffff;
		  border: solid 1px #3498db;
		  border-radius: 5px;
		  box-sizing: border-box;
		  color: #3498db;
		  cursor: pointer;
		  display: inline-block;
		  font-size: 14px;
		  font-weight: bold;
		  margin: 0;
		  padding: 12px 25px;
		  text-decoration: none;
		  text-transform: capitalize; 
	  }

	  .btn-primary table td {
		background-color: #3498db; 
	  }

	  .btn-primary a {
		background-color: #3498db;
		border-color: #3498db;
		color: #ffffff; 
	  }

	  /* -------------------------------------
		  OTHER STYLES THAT MIGHT BE USEFUL
	  ------------------------------------- */
	  .last {
		margin-bottom: 0; 
	  }

	  .first {
		margin-top: 0; 
	  }

	  .align-center {
		text-align: center; 
	  }

	  .align-right {
		text-align: right; 
	  }

	  .align-left {
		text-align: left; 
	  }

	  .clear {
		clear: both; 
	  }

	  .mt0 {
		margin-top: 0; 
	  }

	  .mb0 {
		margin-bottom: 0; 
	  }

	  .preheader {
		color: transparent;
		display: none;
		height: 0;
		max-height: 0;
		max-width: 0;
		opacity: 0;
		overflow: hidden;
		mso-hide: all;
		visibility: hidden;
		width: 0; 
	  }

	  .powered-by a {
		text-decoration: none; 
	  }

	  hr {
		border: 0;
		border-bottom: 1px solid #f6f6f6;
		margin: 20px 0; 
	  }

	  /* -------------------------------------
		  RESPONSIVE AND MOBILE FRIENDLY STYLES
	  ------------------------------------- */
	  @media only screen and (max-width: 620px) {
		table[class=body] h1 {
		  font-size: 28px !important;
		  margin-bottom: 10px !important; 
		}
		table[class=body] p,
		table[class=body] ul,
		table[class=body] ol,
		table[class=body] td,
		table[class=body] span,
		table[class=body] a {
		  font-size: 16px !important; 
		}
		table[class=body] .wrapper,
		table[class=body] .article {
		  padding: 10px !important; 
		}
		table[class=body] .content {
		  padding: 0 !important; 
		}
		table[class=body] .container {
		  padding: 0 !important;
		  width: 100% !important; 
		}
		table[class=body] .main {
		  border-left-width: 0 !important;
		  border-radius: 0 !important;
		  border-right-width: 0 !important; 
		}
		table[class=body] .btn table {
		  width: 100% !important; 
		}
		table[class=body] .btn a {
		  width: 100% !important; 
		}
		table[class=body] .img-responsive {
		  height: auto !important;
		  max-width: 100% !important;
		  width: auto !important; 
		}
	  }

	  /* -------------------------------------
		  PRESERVE THESE STYLES IN THE HEAD
	  ------------------------------------- */
	  @media all {
		.ExternalClass {
		  width: 100%; 
		}
		.ExternalClass,
		.ExternalClass p,
		.ExternalClass span,
		.ExternalClass font,
		.ExternalClass td,
		.ExternalClass div {
		  line-height: 100%; 
		}
		.apple-link a {
		  color: inherit !important;
		  font-family: inherit !important;
		  font-size: inherit !important;
		  font-weight: inherit !important;
		  line-height: inherit !important;
		  text-decoration: none !important; 
		}
		#MessageViewBody a {
		  color: inherit;
		  text-decoration: none;
		  font-size: inherit;
		  font-family: inherit;
		  font-weight: inherit;
		  line-height: inherit;
		}
		.btn-primary table td:hover {
		  background-color: #34495e !important; 
		}
		.btn-primary a:hover {
		  background-color: #34495e !important;
		  border-color: #34495e !important; 
		} 
	  }

	</style>
  </head>
  <body class="">
	<table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
	  <tr>
		<td>&nbsp;</td>
		<td class="container">
		  <div class="content">

			<!-- START CENTERED WHITE CONTAINER -->
			<table role="presentation" class="main">

			  <!-- START MAIN CONTENT AREA -->
			  <tr>
				<td class="wrapper">
				  <table role="presentation" border="0" cellpadding="0" cellspacing="0">
					<tr>
					  <td>
						<img align="center" src="http://trashmap.opencubelabs.com/img/emailphoto.png" alt=""><br><br>
						<p>Hello """ + name + """,</p>
						<p>Thank you for contacting TrashMap.<br>You can reply to the email if you have any other further queries<br>Meanwhile,spread the word about the project and be a part of the initiative :)<br><br>Regards,<br>TrashMap Team.</p>
		  
					  </td>
					</tr>
				  </table>
				</td>
			  </tr>

			<!-- END MAIN CONTENT AREA -->
			</table>
			<!-- END CENTERED WHITE CONTAINER -->

			<!-- START FOOTER -->
			<div class="footer">
			  <table role="presentation" border="0" cellpadding="0" cellspacing="0">
				<tr>
				  <td class="content-block">
					<span align="center" class="apple-link">OpencubeLabs<br> #15,Bhuvi,8th Cross, Bhuvaneshwari Nagar<br> Dasarahalli Main Road, Kempapura, Hebbal<br> Bangalore, India, 560024<br>hello@ocl.space<br>+91-8553236639</span>
				  </td>
				</tr>
				
			  </table>
			</div>
			<!-- END FOOTER -->

		  </div>
		</td>
		<td>&nbsp;</td>
	  </tr>
	</table>
  </body>
</html>

				"""            

# The character encoding for the email.
	CHARSET = "UTF-8"

# Create a new SES resource and specify a region.
	client = boto3.client('ses',region_name=AWS_REGION)

# Try to send the email.
	try:
	#Provide the contents of the email.
		response = client.send_email(
			Destination={
				'ToAddresses': [
					RECIPIENT,
				],
			},
			Message={
				'Body': {
					'Html': {
						'Charset': CHARSET,
						'Data': BODY_HTML,
					},
					'Text': {
						'Charset': CHARSET,
						'Data': BODY_TEXT,
					},
				},
				'Subject': {
					'Charset': CHARSET,
					'Data': SUBJECT,
				},
			},
			ReplyToAddresses=[
				'fellowship@ocl.space'],

			Source=SENDER,
		# If you are not using a configuration set, comment or delete the
		# following line
		#ConfigurationSetName=CONFIGURATION_SET,
		)
 # Display an error if something goes wrong. 
	except ClientError as e:
		print(e.response['Error']['Message'])
	else:
		print("Email sent! Message ID:"),
		print(response['MessageId'])

#app.run(host='127.0.0.1', port=8080)
