#!/usr/bin/env python3

import urllib.request, urllib.error, urllib.parse
import json
import base64
import sys, os
import datetime
import argparse, configparser

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
default_config_file = os.path.join(__location__, 'config.ini')
config = configparser.ConfigParser()

source_url = None
target_url = None

def init_config():
	
	config.add_section('login')
	config.add_section('repository')
	config.add_section('format')
	
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument('--config', help="The location of the config file (either absolute, or relative to the current working directory). Defaults to `config.ini` found in the same folder as this script.")
	arg_parser.add_argument('-u', '--username', help="The username of the account that will create the new issues. The username will not be stored anywhere if passed in as an argument.")
	arg_parser.add_argument('-p', '--password', help="The password (in plaintext) of the account that will create the new issues. The password will not be stored anywhere if passed in as an argument.")
	arg_parser.add_argument('-s', '--source', help="The source repository which the issues should be copied from. Should be in the format `user/repository`.")
	arg_parser.add_argument('-t', '--target', help="The destination repository which the issues should be copied to. Should be in the format `user/repository`.")
	arg_parser.add_argument("issues", type=int, nargs='*', help="The list of issues to import. If no issue ID is provided, all open issues will be imported.");
	
	args = arg_parser.parse_args()
	
	if (args.config):
		config.read(args.config)
	else:
		config.read(default_config_file)
	
	if (args.username): config.set('login', 'username', args.username)
	if (args.password): config.set('login', 'password', args.password)
	
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

def send_post_request(url, data):
	req = urllib.request.Request(url, json.dumps(data).encode("utf-8"))
	
	username = config.get('login', 'username')
	password = config.get('login', 'password')
	req.add_header("Authorization", b"Basic " + base64.urlsafe_b64encode(username.encode("utf-8") + b":" + password.encode("utf-8")))
	
	req.add_header("Content-Type", "application/json")
	req.add_header("Accept", "application/json")

	response = urllib.request.urlopen(req)
	json_data = response.read()
	return json.loads(json_data.decode("utf-8"))

def send_get_request(url):
	response = urllib.request.urlopen(url)
	json_data = response.read()
	return json.loads(json_data.decode("utf-8"))

def get_milestones(url):
	return send_get_request("%s/milestones?state=open" % url)

def get_labels(url):
	return send_get_request("%s/labels" % url)
	
def get_issue_by_id(url, issue_id):
	return send_get_request("%s/issues/%d" % (url, issue_id))

def get_issues(url):
	issues = []
	i = 1
	while True:
		newIssues = send_get_request("%s/issues?state=open&direction=asc&page=%d" % (url, i))
		if not newIssues:
			break
		issues.extend(newIssues)
		i += 1
	return issues

def get_comments_on_issue(issue):
	if "comments" in issue \
	  and issue["comments"] is not None \
	  and issue["comments"] != 0:
		return send_get_request("%s/comments" % issue["url"])
	else :
		return []

def import_milestones(milestones):
	for source in milestones:
		data = {
			"title": source["title"],
			"state": "open",
			"description": source["description"],
			"due_on": source["due_on"]
		}
		
		res_milestone = send_post_request("%s/milestones" % target_url, data)
		print("Successfully created milestone '%s'" % res_milestone["title"])

def import_labels(labels):
	for source in labels:
		data = {
			"name": source["name"],
			"color": source["color"]
		}
		
		res_label = send_post_request("%s/labels" % target_url, data)
		print("Successfully created label '%s'" % res_label["name"])

def import_comments(comments, issue_number):
	for comment in comments:
	
		template_data = {}
		template_data['comment_creator_username'] = comment["user"]["login"]
		template_data['comment_creator_url'] = comment["user"]["html_url"]
		template_data['comment_date'] = format_date(comment["created_at"])
		template_data['comment_url'] =  comment["html_url"]
		template_data['comment_body'] = comment["body"]
		
		comment["body"] = format_comment(template_data)

		send_post_request("%s/issues/%s/comments" % (target_url, issue_number), comment)

def import_issues(issues, dst_milestones, dst_labels):
	for issue in issues:
		
		template_data = {}
		template_data['issue_creator_username'] = issue["user"]["login"]
		template_data['issue_creator_url'] = issue["user"]["html_url"]
		template_data['issue_date'] = format_date(issue["created_at"])
		template_data['issue_url'] =  issue["html_url"]
		template_data['issue_body'] = issue["body"]
		
		if "pull_request" in issue and issue["pull_request"]["html_url"] is not None:
			issue["body"] = format_pull_request(template_data)
		else:
			issue["body"] = format_issue(template_data)
		
		# Temporarily disable milestones! TODO: Fix this
		# This happens because "milestone" needs to be a uint of the id of the milestone,
		#  but the code that gets the milestone gives a whole bunch of unecessary details.
		del issue["milestone"]
		
		res_issue = send_post_request("%s/issues" % target_url, issue)

		comments = get_comments_on_issue(issue)
		import_comments(comments, res_issue["number"])

		print("Successfully created issue '%s'" % res_issue["title"])

def import_some_issues(issue_ids):
	
	# Ignore retrieveing new milestones and lables for now
	
	# Fetch existing milestones and labels
	#TODO: milestones = get_milestones(target_url)
	milestones = []
	labels = get_labels(target_url)

	# Populate issues based on issue IDs
	issues = []
	for issue_id in issue_ids:
		issues.append(get_issue_by_id(source_url, int(issue_id)))
	
	# Finally, import everything
	import_issues(issues, milestones, labels)
	
	
def import_all_open_issues():

	#get milestones and issues to import
	#TODO: milestones = get_milestones(source_url)
	milestones = []
	labels = get_labels(source_url)
	#do import
	#import_milestones(milestones)
	import_labels(labels)

	#get imported milestones and labels
	#TODO: milestones = get_milestones(target_url)
	milestones = []
	labels = get_labels(target_url)

	#process issues
	issues = get_issues(source_url)
	import_issues(issues, milestones, labels)


if __name__ == '__main__':
	
	issue_ids = init_config()
	
	if (len(issue_ids) > 0):
		import_some_issues(issue_ids)
	else:
		import_all_open_issues()
