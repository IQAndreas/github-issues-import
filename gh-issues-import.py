import urllib.request, urllib.error, urllib.parse
import json
import base64

#==== configurations =======
username = "username"
password = "password"
src_repo = "octocat/HelloWorld"
dst_repo = "demo/HelloWorld"
#==== end of configurations ===

server = "api.github.com"
src_url = "https://%s/repos/%s" % (server, src_repo)
dst_url = "https://%s/repos/%s" % (server, dst_repo)

def send_post_request(url, data):
	req = urllib.request.Request(url, json.dumps(data).encode("utf-8"))
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

def get_issues(url):
	issues = []
	i = 1
	while True:
		newIssues = send_get_request("%s/issues?state=open&page=%d" % (url, i))
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
		
		res_milestone = send_post_request("%s/milestones" % dst_url, data)
		print("Successfully created milestone '%s'" % res_milestone["title"])

def import_labels(labels):
	for source in labels:
		data = {
			"name": source["name"],
			"color": source["color"]
		}
		
		res_label = send_post_request("%s/labels" % dst_url, data)
		print("Successfully created label '%s'" % res_label["name"])

def import_comments(comments, issue_number):
	for comment in comments:
		comment_creator = comment["user"]["login"]
		comment["body"] = "Comment by: [%s](http://github.com/%s)\n\n%s" % (comment_creator, comment_creator, comment["body"])

		send_post_request("%s/issues/%s/comments" % (dst_url, issue_number), comment)

def import_pull_requests(issue, issue_number):
	if "pull_request" in issue and issue["pull_request"]["html_url"] is not None:
		committer_name = issue["user"]["login"]
		comment = {"body": "**[#%s](%s)** added a commit: %s" % (committer_name, committer_name, issue["pull_request"]["html_url"])}

		send_post_request("%s/issues/%s/comments" % (dst_url, issue_number), comment)

def import_issues(issues, dst_milestones, dst_labels):
	for issue in issues:

		issue_creator = issue["user"]["login"]
		issue_url = issue["html_url"]
		issue_id = issue["number"]

		if "body" in issue and issue["body"] is not None:
			issue_header = "Issue [#%s](%s) by: [%s](http://github.com/%s)\n" % (issue_id, issue_url, issue_creator, issue_creator)
			issue["body"] = issue_header + "\n\n\n" + issue["body"]

		res_issue = send_post_request("%s/issues" % dst_url, issue)
		import_pull_requests(issue, res_issue["number"])

		comments = get_comments_on_issue(issue)
		import_comments(comments, res_issue["number"])

		print("Successfully created issue '%s'" % res_issue["title"])

def main():
	#get milestones and issues to import
	milestones = get_milestones(src_url)
	labels = get_labels(src_url)
	#do import
	import_milestones(milestones)
	import_labels(labels)

	#get imported milestones and labels
	milestones = get_milestones(dst_url)
	labels = get_labels(dst_url)

	#process issues
	issues = get_issues(src_url)
	import_issues(issues, milestones, labels)


if __name__ == '__main__':
	main()
