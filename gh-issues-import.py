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
    
    config.add_section('source')
    config.add_section('target')
    config.add_section('format')
    config.add_section('settings')
    
    arg_parser = argparse.ArgumentParser(description="Import issues from one GitHub repository into another.")
    
    arg_parser.add_argument('--config', help="The location of the config file (either absolute, or relative to the current working directory). Defaults to `config.ini` found in the same folder as this script.")
    arg_parser.add_argument('-source_u', '--source_username', help="The SOURCE username of the account on the SOURCE server the issues are to be copied from. The username will not be stored anywhere if passed in as an argument.")
    arg_parser.add_argument('-source_p', '--source_password', help="The SOURCE password of the account on the SOURCE server the issues are to be copied from. The username will not be stored anywhere if passed in as an argument.")
    arg_parser.add_argument('-target_u', '--target_username', help="The TARGET username of the account on the TARGET server the issues are to be copied from. The username will not be stored anywhere if passed in as an argument.")
    arg_parser.add_argument('-target_p', '--target_password', help="The TARGET password of the account on the TARGET server the issues are to be copied from. The username will not be stored anywhere if passed in as an argument.")
    arg_parser.add_argument('-source_s', '--source_server', help="The SOURCE server which the issues should be copied from. e.g. `github.com` or `github.mycompany.com` (for enterprise).")
    arg_parser.add_argument('-target_s', '--target_server', help="The TARGET server which the issues should be copied to. e.g. `github.com` or `github.mycompany.com` (for enterprise).")
    arg_parser.add_argument('-source_r', '--source_repo', help="The source repository which the issues should be copied from. Should be in the format `user/repository`.")
    arg_parser.add_argument('-target_r', '--target_repo', help="The destination repository which the issues should be copied to. Should be in the format `user/repository`.")
    
    arg_parser.add_argument('--ignore-comments',  dest='ignore_comments',  action='store_true', help="Do not import comments in the issue.")        
    arg_parser.add_argument('--ignore-milestone', dest='ignore_milestone', action='store_true', help="Do not import the milestone attached to the issue.")
    arg_parser.add_argument('--ignore-labels',    dest='ignore_labels',    action='store_true', help="Do not import labels attached to the issue.")
    
    arg_parser.add_argument("issues", type=int, nargs='*', help="The list of issues to import. If no issue ID is provided, all open issues will be imported.");
    
    args = arg_parser.parse_args()
    
    config_file_name = default_config_file
    if (args.config): config_file_name = args.config
    
    try:
        config_file = open(config_file_name)
        config.read_file(config_file)
    except FileNotFoundError:
        sys.exit("ERROR: Unable to find or open config file '%s'" % config_file_name);
    
    if (args.source_username): config.set('source', 'username', args.source_username)
    if (args.source_password): config.set('source', 'password', args.source_password)
    if (args.target_username): config.set('target', 'username', args.target_username)
    if (args.target_password): config.set('target', 'password', args.target_password)
    if (args.source_server): config.set('source', 'server', args.source_server)
    if (args.target_server): config.set('target', 'server', args.target_server)
    if (args.source_repo): config.set('source', 'repository', args.source_repo)
    if (args.target_repo): config.set('target', 'repository', args.target_repo)
    
    config.set('settings', 'import-comments',  str(not args.ignore_comments))
    config.set('settings', 'import-milestone', str(not args.ignore_milestone))
    config.set('settings', 'import-labels',    str(not args.ignore_labels))
    
    
    # Make sure no required config values are missing
    if not config.has_option('source','repository') :
        sys.exit("ERROR: There is no source repository specified either in the config file, or as an argument.")
    if not config.has_option('target','repository') :
        sys.exit("ERROR: There is no target repository specified either in the config file, or as an argument.")
    
    # Prompt for SOURCE username/password if none is provided in either the config or an argument
    if not config.has_option('source', 'username') :
        config.set('source', 'username', query.username("Enter your username for GitHub.com: "))
    if not config.has_option('source', 'password') :
        config.set('source', 'password', query.password("Enter your password for GitHub.com: "))
    
    # Prompt for TARGET username/password if none is provided in either the config or an argument
    if not config.has_option('target', 'username') :
        config.set('target', 'username', query.username("Enter your TARGET username for GitHub.com: "))
    if not config.has_option('target', 'password') :
        config.set('target', 'password', query.password("Enter your TARGET password for GitHub.com: "))
    
    
    # Everything is here! Continue on our merry way...
    global source_url, target_url

    # if SOURCE server is not github.com, then assume ENTERPRISE github (yourdomain.com/api/v3...)
    if (config.get('source','server') != "github.com") :
        source_api_server = config.get('source','server')
        source_url = "https://%s/api/v3/repos/%s" % (source_api_server, config.get('source','repository'))
    else :
        source_api_server = "api.github.com"
        source_url = "https://%s/repos/%s" % (source_api_server, config.get('source','repository'))

    # if TARGET server is not github.com, then assume ENTERPRISE github (yourdomain.com/api/v3...)
    if (config.get('target','server') != "github.com") :
        target_api_server = config.get('target','server')
        target_url = "https://%s/api/v3/repos/%s" % (target_api_server, config.get('target','repository'))
    else :
        target_api_server = "api.github.com"
        target_url = "https://%s/repos/%s" % (target_api_server, config.get('target','repository'))
    
    
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

def send_request(which, url, post_data=None, req_method=None):
    if (post_data != None):
        post_data = json.dumps(post_data).encode("utf-8")
    

    req = urllib.request.Request(url,post_data)
    
    username = config.get(which,'username')
    password = config.get(which,'password')
    
    if (req_method != None):
        req.method = req_method
    
    req.add_header("Authorization", b"Basic " + base64.urlsafe_b64encode(username.encode("utf-8") + b":" + password.encode("utf-8")))
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "IQAndreas/github-issues-import")
    
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

def get_milestones(which, state, url):
    if (state == "all") :
        return send_request(which,"%s/milestones" % (url))
    else :
        return send_request(which,"%s/milestones?state=%s" % (url, state))
    
def get_labels(which, url):
    return send_request(which,"%s/labels" % url)
    
def get_issue_by_id(which, url, issue_id):
    return send_request(which,"%s/issues/%d" % (url, issue_id))

def get_issues(which, state, url):
    issues = []
    page = 1
    while True:
        if (state == "all") :
            open_issues = send_request(which,"%s/issues?state=open&direction=asc&page=%d" % (url, page))
            closed_issues = send_request(which,"%s/issues?state=closed&direction=asc&page=%d" % (url, page))
            if (not open_issues and not closed_issues):
                break
            issues.extend(open_issues)
            issues.extend(closed_issues)
        else :
            new_issues = send_request(which,"%s/issues?state=%s&direction=asc&page=%d" % (url, state, page))
            if not new_issues:
                break
            issues.extend(new_issues)
        
        page += 1
    return issues

def get_comments_on_issue(which,issue):
    if issue['comments'] != 0:
        return send_request(which,"%s/comments" % issue['url'])
    else :
        return []

def import_milestone(source):
    data = {
        "title": source['title'],
        "state": source['state'],
        "description": source['description'],
        "due_on": source['due_on']
    }
    
    result_milestone = send_request("target","%s/milestones" % target_url, source)
    print("Successfully created milestone '%s'" % result_milestone['title'])
    return result_milestone

def import_label(source):
    data = {
        "name": source['name'],
        "color": source['color']
    }
    
    result_label = send_request("target","%s/labels" % target_url, source)
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

        result_comment = send_request("target","%s/issues/%s/comments" % (target_url, issue_number), comment)
        result_comments.append(result_comment)
        
    return result_comments

# Will only import milestones and issues that are in use by the imported issues, and do not exist in the target repository
def import_issues(state, issues):
    
    known_milestones = get_milestones("target", state, target_url)
    def get_milestone_by_title(title):
        for milestone in known_milestones:
            if milestone['title'] == title : return milestone
        return None
    
    known_labels = get_labels("target",target_url)
    def get_label_by_name(name):
        for label in known_labels:
            if label['name'] == name : return label
        return None
    
    new_issues = []
    closed_issues = []
    num_new_comments = 0
    new_milestones = []
    new_labels = []
    
    for issue in issues:
        new_issue = {}
        new_issue['title'] = issue['title']
        if config.getboolean('settings', 'import-comments') and 'comments' in issue and issue['comments'] != 0:
            num_new_comments += int(issue['comments'])
            new_issue['comments'] = get_comments_on_issue("source",issue)
        
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
        
        if (issue['state'] == "closed") :
            close_issue = {}
            close_issue['number'] = issue['number']
            close_issue['state'] = "closed"
            closed_issues.append(close_issue)
    
    print("You are about to add to '" + config.get('target','repository') + "':")
    print(" *", len(new_issues), "creating issues") 
    print(" *", len(closed_issues), "closing issues") 
    print(" *", num_new_comments, "new comments") 
    print(" *", len(new_milestones), "new milestones") 
    print(" *", len(new_labels), "new labels") 
    if not query.yes_no("Are you sure you wish to continue?"):
        sys.exit()
    
    for milestone in new_milestones:
        result_milestone = import_milestone(state, milestone)
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
        
        result_issue = send_request("target","%s/issues" % target_url, issue)
        print("Successfully created issue '%s'" % result_issue['title'])
        
        if 'comments' in issue:
            result_comments = import_comments(issue['comments'], result_issue['number'])        
            print(" > Successfully added", len(result_comments), "comments.")
        
        result_issues.append(result_issue)
    
    for issue in closed_issues:
        result_issue = send_request("target","%s/issues/%d" % (target_url,issue['number']), issue, 'PATCH')
        print("Successfully closed issue '%s'" % result_issue['title'])
        
        #result_issues.append(result_issue)

    return result_issues
def import_some_issues(issue_ids):
    # Populate issues based on issue IDs
    issues = []
    for issue_id in issue_ids:
        issues.append(get_issue_by_id("source",source_url, int(issue_id)))
    
    return import_issues(issues)

def import_open_issues():
    # Populate issues based on issue IDs
    issues = []
    
    issues.append(get_issues("source","open",source_url))
    
    return import_issues(issues)

def import_closed_issues():
    # Populate issues based on issue IDs
    issues = []
    issues.append(get_issues("source","closed",source_url))
    
    return import_issues(issues)

def import_all_issues():
    issues = get_issues("source","all",source_url)
    return import_issues("all",issues)

if __name__ == '__main__':
    
    issue_ids = init_config()
    
    if (len(issue_ids) > 0):
        import_some_issues(issue_ids)
    else:
        import_all_issues()
    

