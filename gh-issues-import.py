#!/usr/bin/env python3

import urllib.request, urllib.error, urllib.parse
import json
import base64
import sys, os
import datetime
import argparse, configparser

import query

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
default_config_file = os.path.join(__location__, 'config.ini')
config = configparser.ConfigParser()

source_url = None
target_url = None

http_error_messages = {}
http_error_messages[401] = "ERROR: There was a problem during authentication.\nDouble check that your username and password are correct, and that you have permission to read from or write to the specified repositories."
http_error_messages[403] = http_error_messages[401]; # Basically the same problem. GitHub returns 403 instead to prevent abuse.
http_error_messages[404] = "ERROR: Unable to find the specified repository.\nDouble check the spelling for the source and target repositories. If either repository is private, make sure the specified user is allowed access to it."


def init_config():
	
	config.add_section('login')
	config.add_section('repository')
	config.add_section('format')
	config.add_section('settings')
	
	arg_parser = argparse.ArgumentParser()
	
	arg_parser.add_argument('--config', help="The location of the config file (either absolute, or relative to the current working directory). Defaults to `config.ini` found in the same folder as this script.")
	arg_parser.add_argument('-u', '--username', help="The username of the account that will create the new issues. The username will not be stored anywhere if passed in as an argument.")
	arg_parser.add_argument('-p', '--password', help="The password (in plaintext) of the account that will create the new issues. The password will not be stored anywhere if passed in as an argument.")
	arg_parser.add_argument('-s', '--source', help="The source repository which the issues should be copied from. Should be in the format `user/repository`.")
	arg_parser.add_argument('-t', '--target', help="The destination repository which the issues should be copied to. Should be in the format `user/repository`.")
	
	arg_parser.add_argument('--ignore-comments',  dest='ignore_comments',  action='store_true', help="Do not import comments in the issue.")		
	arg_parser.add_argument('--ignore-milestone', dest='ignore_milestone', action='store_true', help="Do not import the milestone attached to the issue.")
	arg_parser.add_argument('--ignore-labels',    dest='ignore_labels',    action='store_true', help="Do not import labels attached to the issue.")
	
	arg_parser.add_argument("issues", type=int, nargs='*', help="The list of issues to import. If no issue ID is provided, all open issues will be imported.");
	
	args = arg_parser.parse_args()
	
	if (args.config):
		config.read(args.config)
	else:
		config.read(default_config_file)
	
	if (args.username): config.set('login', 'username', args.username)
	if (args.password): config.set('login', 'password', args.password)
	
	config.set('settings', 'import-comments',  str(not args.ignore_comments))
	config.set('settings', 'import-milestone', str(not args.ignore_milestone))
	config.set('settings', 'import-labels',    str(not args.ignore_labels))
	
	# Prompt for username/password if none is provided in either the config or an argument
	if not config.has_option('login', 'username') :
		config.set('login', 'username', query.username("Enter your username for GitHub.com: "))
	if not config.has_option('login', 'password') :
		config.set('login', 'password', query.password("Enter your password for GitHub.com: "))
	
	#TODO: Make sure no config values are missing
	
	global source_url, target_url
	server = "api.github.com"
	source_url = "https://%s/repos/%s" % (server, config.get('repository', 'source'))
	target_url = "https://%s/repos/%s" % (server, config.get('repository', 'target'))
	
	return args.issues

def format_date(datestring):
	# The date comes from the API in ISO-8601 format
	date = datetime.datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%SZ")
	date_format = config.get('format', 'date', fallback='%A %b %d, %Y at %H:%M GMT', raw=True);
	return date.strftime(date_format)
	
def format_from_template(template_filename, template_data):
	from string import Template
	template_file = open(template_filename, 'r')
	template = Template(template_file.read())
	return template.substitute(template_data)

def format_issue(template_data):
	default_template = os.path.join(__location__, 'templates', 'issue.md')
	template = config.get('format', 'issue_template', fallback=default_template)
	return format_from_template(template, template_data)

def format_pull_request(template_data):
	default_template = os.path.join(__location__, 'templates', 'pull_request.md')
	template = config.get('format', 'pull_request_template', fallback=default_template)
	return format_from_template(template, template_data)

def format_comment(template_data):
	default_template = os.path.join(__location__, 'templates', 'comment.md')
	template = config.get('format', 'comment_template', fallback=default_template)
	return format_from_template(template, template_data)

def send_request(url, post_data=None):

	if (post_data != None):
		post_data = json.dumps(post_data).encode("utf-8")
	req = urllib.request.Request(url, post_data)
	
	username = config.get('login', 'username')
	password = config.get('login', 'password')
	req.add_header("Authorization", b"Basic " + base64.urlsafe_b64encode(username.encode("utf-8") + b":" + password.encode("utf-8")))
	
	req.add_header("Content-Type", "application/json")
	req.add_header("Accept", "application/json")

	try:
		response = urllib.request.urlopen(req)
		json_data = response.read()
	except urllib.error.HTTPError as error:
		
		error_details = error.read();
		error_details = json.loads(error_details.decode("utf-8"))
		print(error_details)
		if (error.code in http_error_messages):
			sys.exit(http_error_messages[error.code])
		else:
			error_message = "ERROR: There was a problem importing the issues.\n%s %s" % (error.code, error.reason)
			if ('message' in error_details):
				error_message += "\nDETAILS: " + error_details['message']
			sys.exit(error_message)
	
	return json.loads(json_data.decode("utf-8"))

def get_milestones(url):
	return send_request("%s/milestones?state=open" % url)

def get_labels(url):
	return send_request("%s/labels" % url)
	
def get_issue_by_id(url, issue_id):
	return send_request("%s/issues/%d" % (url, issue_id))

def get_open_issues(url):
	issues = []
	page = 1
	while True:
		new_issues = send_request("%s/issues?state=open&direction=asc&page=%d" % (url, page))
		if not new_issues:
			break
		issues.extend(new_issues)
		page += 1
	return issues

def get_comments_on_issue(issue):
	if issue['comments'] != 0:
		return send_request("%s/comments" % issue['url'])
	else :
		return []

def import_milestone(source):
	data = {
		"title": source['title'],
		"state": "open",
		"description": source['description'],
		"due_on": source['due_on']
	}
	
	result_milestone = send_request("%s/milestones" % target_url, source)
	print("Successfully created milestone '%s'" % result_milestone['title'])
	return result_milestone

def import_label(source):
	data = {
		"name": source['name'],
		"color": source['color']
	}
	
	result_label = send_request("%s/labels" % target_url, source)
	print("Successfully created label '%s'" % result_label['name'])
	return result_label

def import_comments(comments, issue_number):
	result_comments = []
	for comment in comments:
	
		template_data = {}
		template_data['comment_creator_username'] = comment['user']['login']
		template_data['comment_creator_url'] = comment['user']['html_url']
		template_data['comment_date'] = format_date(comment['created_at'])
		template_data['comment_url'] =  comment['html_url']
		template_data['comment_body'] = comment['body']
		
		comment['body'] = format_comment(template_data)

		result_comment = send_request("%s/issues/%s/comments" % (target_url, issue_number), comment)
		result_comments.append(result_comment)
		
	return result_comments

# Will only import milestones and issues that are in use by the imported issues, and do not exist in the target repository
def import_issues(issues):
	
	known_milestones = get_milestones(target_url)
	def get_milestone_by_title(title):
		for milestone in known_milestones:
			if milestone['title'] == title : return milestone
		return None
	
	known_labels = get_labels(target_url)
	def get_label_by_name(name):
		for label in known_labels:
			if label['name'] == name : return label
		return None
	
	new_issues = []
	num_new_comments = 0
	new_milestones = []
	new_labels = []
	
	for issue in issues:
		
		new_issue = {}
		new_issue['title'] = issue['title']
		
		if config.getboolean('settings', 'import-comments') and 'comments' in issue and issue['comments'] != 0:
			num_new_comments += int(issue['comments'])
			new_issue['comments'] = get_comments_on_issue(issue)
		
		if config.getboolean('settings', 'import-milestone') and 'milestone' in issue and issue['milestone'] is not None:
			# Since the milestones' ids are going to differ, we will compare them by title instead
			found_milestone = get_milestone_by_title(issue['milestone']['title'])
			if found_milestone:
				new_issue['milestone_object'] = found_milestone
			else:
				new_milestone = issue['milestone']
				new_issue['milestone_object'] = new_milestone
				known_milestones.append(new_milestone) # Allow it to be found next time
				new_milestones.append(new_milestone)   # Put it in a queue to add it later
		
		if config.getboolean('settings', 'import-labels') and 'labels' in issue and issue['labels'] is not None:
			new_issue['label_objects'] = []
			for issue_label in issue['labels']:
				found_label = get_label_by_name(issue_label['name'])
				if found_label:
					new_issue['label_objects'].append(found_label)
				else:
					new_issue['label_objects'].append(issue_label)
					known_labels.append(issue_label) # Allow it to be found next time
					new_labels.append(issue_label)   # Put it in a queue to add it later
		
		template_data = {}
		template_data['issue_creator_username'] = issue['user']['login']
		template_data['issue_creator_url'] = issue['user']['html_url']
		template_data['issue_date'] = format_date(issue['created_at'])
		template_data['issue_url'] =  issue['html_url']
		template_data['issue_body'] = issue['body']
		
		if "pull_request" in issue and issue['pull_request']['html_url'] is not None:
			new_issue['body'] = format_pull_request(template_data)
		else:
			new_issue['body'] = format_issue(template_data)
		
		new_issues.append(new_issue)
	
	print("You are about to add to '" + config.get('repository', 'target') + "':")
	print(" *", len(new_issues), "new issues") 
	print(" *", num_new_comments, "new comments") 
	print(" *", len(new_milestones), "new milestones") 
	print(" *", len(new_labels), "new labels") 
	if not query.yes_no("Are you sure you wish to continue?"):
		sys.exit()
	
	for milestone in new_milestones:
		result_milestone = import_milestone(milestone)
		milestone['number'] = result_milestone['number']
		milestone['url'] = result_milestone['url']
	
	for label in new_labels:
		result_label = import_label(label)
	
	result_issues = []
	for issue in new_issues:
		
		if 'milestone_object' in issue:
			issue['milestone'] = issue['milestone_object']['number']
			del issue['milestone_object']
		
		if 'label_objects' in issue:
			issue_labels = []
			for label in issue['label_objects']:
				issue_labels.append(label['name'])
			issue['labels'] = issue_labels
			del issue['label_objects']
		
		result_issue = send_request("%s/issues" % target_url, issue)
		print("Successfully created issue '%s'" % result_issue['title'])
		
		if 'comments' in issue:
			result_comments = import_comments(issue['comments'], result_issue['number'])		
			print(" > Successfully added", len(result_comments), "comments.")
		
		result_issues.append(result_issue)

	return result_issues

def import_some_issues(issue_ids):
	# Populate issues based on issue IDs
	issues = []
	for issue_id in issue_ids:
		issues.append(get_issue_by_id(source_url, int(issue_id)))
	
	return import_issues(issues)
		
def import_all_open_issues():
	issues = get_open_issues(source_url)
	return import_issues(issues)


if __name__ == '__main__':
	
	issue_ids = init_config()
	
	if (len(issue_ids) > 0):
		import_some_issues(issue_ids)
	else:
		import_all_open_issues()
	

