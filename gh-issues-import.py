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

def get_milestones(url):
	response = urllib.request.urlopen("%s/milestones?state=open" % url)
	result = response.read()
	milestones = json.loads(result.decode("utf-8"))
	return milestones

def get_labels(url):
	response = urllib.request.urlopen("%s/labels" % url)
	result = response.read()
	labels = json.loads(result.decode("utf-8"))
	return labels

def get_issues(url):
	issues = []
	i = 1
	while True:
		response = urllib.request.urlopen("%s/issues?state=open&page=%d" % (url, i))
		result = response.read()
		newIssues = json.loads(result.decode("utf-8"))
		if not newIssues:
			break
		issues.extend(newIssues)
		i += 1
	return issues

def get_comments_on_issue(issue):
	if "comments" in issue \
	  and issue["comments"] is not None \
	  and issue["comments"] != 0:
		response = urllib.request.urlopen("%s/comments" % issue["url"])
		result = response.read()
		comments = json.loads(result.decode("utf-8"))
		return comments
	else :
		return []

def import_milestones(milestones):
	for source in milestones:
		dest = json.dumps({
			"title": source["title"],
			"state": "open",
			"description": source["description"],
			"due_on": source["due_on"]})

		req = urllib.request.Request("%s/milestones" % dst_url, dest)
		req.add_header("Authorization", "Basic " + base64.urlsafe_b64encode("%s:%s" % (username, password)))
		req.add_header("Content-Type", "application/json")
		req.add_header("Accept", "application/json")
		res = urllib.request.urlopen(req)

		data = res.read()
		res_milestone = json.loads(data.decode("utf-8"))
		print("Successfully created milestone %s" % res_milestone["title"])

def import_labels(labels):
	for source in labels:
		dest = json.dumps({
			"name": source["name"],
			"color": source["color"]
		})

		req = urllib.request.Request("%s/labels" % dst_url, dest)
		req.add_header("Authorization", "Basic " + base64.urlsafe_b64encode("%s:%s" % (username, password)))
		req.add_header("Content-Type", "application/json")
		req.add_header("Accept", "application/json")
		res = urllib.request.urlopen(req)

		data = res.read()
		res_label = json.loads(data.decode("utf-8"))
		print("Successfully created label %s" % res_label["name"])

def import_comments(comments, issue_number):
	for comment in comments:
		comment_creator = comment["user"]["login"]
		comment["body"] = "Comment by: [%s](http://github.com/%s)\n\n%s" % (comment_creator, comment_creator, comment["body"])

		req = urllib.request.Request("%s/issues/%s/comments" % (dst_url, issue_number), json.dumps(comment))
		req.add_header("Authorization", b"Basic " + base64.urlsafe_b64encode(username.encode("utf-8") + b":" + password.encode("utf-8")))
		req.add_header("Content-Type", "application/json")
		req.add_header("Accept", "application/json")
		urllib.request.urlopen(req)

def import_pull_requests(issue, issue_number):
	if "pull_request" in issue and issue["pull_request"]["html_url"] is not None:
		committer_name = issue["user"]["login"]
		comment = json.dumps({"body": "**[#%s](%s)** added a commit: %s" % (committer_name, committer_name, issue["pull_request"]["html_url"])})

		req = urllib.request.Request("%s/issues/%s/comments" % (dst_url, issue_number), comment)
		req.add_header("Authorization", b"Basic " + base64.urlsafe_b64encode(username.encode("utf-8") + b":" + password.encode("utf-8")))
		req.add_header("Content-Type", "application/json")
		req.add_header("Accept", "application/json")
		urllib.request.urlopen(req)

def import_issues(issues, dst_milestones, dst_labels):
	for issue in issues:

		issue_creator = issue["user"]["login"]
		issue_url = issue["html_url"]
		issue_id = issue["number"]

		if "body" in issue and issue["body"] is not None:
			issue_header = "Issue [#%s](%s) by: [%s](http://github.com/%s)\n" % (issue_id, issue_url, issue_creator, issue_creator)
			issue["body"] = issue_header + "\n\n\n" + issue["body"]

		req = urllib.request.Request("%s/issues" % dst_url, json.dumps(issue))
		req.add_header("Authorization", b"Basic " + base64.urlsafe_b64encode(username.encode("utf-8") + b":" + password.encode("utf-8")))
		req.add_header("Content-Type", "application/json")
		req.add_header("Accept", "application/json")
		res = urllib.request.urlopen(req)

		data = res.read()
		res_issue = json.loads(data.decode("utf-8"))

		import_pull_requests(issue, res_issue["number"])

		comments = get_comments_on_issue(issue)
		import_comments(comments, res_issue["number"])

		print("Successfully created issue %s" % res_issue["title"].encode("utf-8"))

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