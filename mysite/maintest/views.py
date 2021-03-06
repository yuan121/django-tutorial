from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.files.storage import DefaultStorage, default_storage, FileSystemStorage
from django.http import StreamingHttpResponse


from filebrowser.sites import site
from filebrowser.base import FileListing, FileObject
import os, json, re

# Create your views here.

DIRECTORY = os.path.join(site.storage.location, "uploads")


def index(request):
	return HttpResponse("This is the file management page.")


def dict2json(List):
	"""
	Change a dict to a json.
	:param dict:
	:return json:
	"""
	return render(request, 'maintest/test.html', {
		'List': json.dumps(List),
	})


"""
arithmetic app functions
"""


def _file_process(file, regex):
	dict = {}
	with open(file, "r") as fp:
		for line in fp.readlines():
			# print(line)
			m = regex.match(line)
			if m:
				dict[m.group(1)] = m.group(2)
	return dict


def data_parser(file):
	regex = re.compile(r'(data\d): (\d+)')
	return _file_process(file, regex)


def operator_parser(file):
	regex = re.compile(r'(operator): (0x80{6}\d)')
	return _file_process(file, regex)


def app_execution(data1, data2, operator):
	return_value = os.popen('sudo /BR0101/arith_math/arithmetic_intr_mmap_test_app' + data1 + data2 + operator).read()
	return return_value


def arithmetic_app(request):
	# TODO: ugly code.
	dataFile = "/home/keylab/work/virtualenv/web/work/django-tutorial/mysite/maintest/myTest/data"
	operatorFile = "/home/keylab/work/virtualenv/web/work/django-tutorial/mysite/maintest/myTest/operator"
	dataDict = data_parser(dataFile)
	operator = operator_parser(operatorFile)['operator']
	result = app_execution(dataDict['data1'], dataDict['data2'], operator)
	# result = app_execution(dataDict["data1"], dataDict["data2"], operator)
	return HttpResponse(result)


def treeview_parser(root=''):
	"""
	According to the given root, traverse its file tree and return a json object.
	:param root:
	:return dict:
	"""
	dataList=[]
	path = os.path.join(DIRECTORY, root)
	filelisting = FileListing(path, sorting_by='date', sorting_order='desc')
	for item in filelisting.listing():
		fileobject = FileObject(os.path.join(path, item))
		if fileobject.is_folder and not fileobject.is_empty:
			dataList.append({
				"text": item,
				"nodes": treeview_parser(fileobject.path_relative_directory)
			})
		else:
			dataList.append({"text": item})
	return dataList


def test(request):
	List = ['key', 'value']
	Dict = {'site': 'aaa', 'author': 'bbb'}
	# print(site.directory)
	# print(treeview_parser())
	# obj = [
	# 	{
	# 		"text": "Parent 1",
	# 		"nodes": [
	# 			{
	# 				"text": "Child 1",
	# 				"nodes": [
	# 					{
	# 						"text": "Grandchild 1"
	# 					},
	# 					{
	# 						"text": "Grandchild 2"
	# 					}
	# 				]
	# 			},
	# 			{
	# 				"text": "Child 2"
	# 			}
	# 		]
	# 	},
	# 	{
	# 		"text": "Parent 2"
	# 	},
	# 	{
	# 		"text": "Parent 3"
	# 	},
	# 	{
	# 		"text": "Parent 4"
	# 	},
	# 	{
	# 		"text": "Parent 5"
	# 	}
	# ]
	obj = treeview_parser("myTest")
	return render(request, 'maintest/test.html', {
		'List': json.dumps(List),
		'obj': json.dumps(obj),
		'Dict': json.dumps(Dict)
	})

