#-*- coding: UTF-8 -*-   

import time
import urllib2
from flask import Flask,g,request,make_response
import hashlib
import xml.etree.ElementTree as ET
import json
import random
import re
import urllib
import sys
import pylibmc


app=Flask(__name__)
app.debug=True

def youdao(word):
	quary=urllib2.quote(word)
	baseurl=r'http://fanyi.youdao.com/openapi.do?keyfrom=自己的&key=自己的&type=data&doctype=json&version=1.1&q='
	url=baseurl+quary
	resp=urllib2.urlopen(url)
	fanyi=json.loads(resp.read())
	if fanyi['errorCode'] == 0:
		if 'basic' in fanyi.keys():
			trans=u'%s:\n%s\n%s\n网络释意:\n%s'%(fanyi['query'],''.join(fanyi['translation']),' '.join(fanyi['basic']['explains']),''.join(fanyi['web'][0]['value']))
			return trans
		else:
			trans =u'%s:\n基本翻译:%s\n'%(fanyi['query'],''.join(fanyi['translation']))        
			return trans
	elif fanyi['errorCode'] == 20:
		return u'对不起，要翻译的文本过长'
	elif fanyi['errorCode'] == 30:
		return u'对不起，无法进行有效的翻译'
	elif fanyi['errorCode'] == 40:
		return u'对不起，不支持的语言类型'
	else:
		return u'对不起，您输入的单词%s无法翻译,请检查拼写'% word

def joke():
	try:
		for i in random.sample(range(335),1):
			page='page='+str(i)
			full_url='http://apis.baidu.com/showapi_open_bus/showapi_joke/joke_text?'+page
			req = urllib2.Request(full_url)
			req.add_header("apikey", "自己的key")
			resp = urllib2.urlopen(req,timeout=5)
			data= json.loads(resp.read())		
		for i in random.sample(range(len(data['showapi_res_body']['contentlist'])),1):
			return data['showapi_res_body']['contentlist'][i]['title']+'\n'+data['showapi_res_body']['contentlist'][i]['text']+'\n'	
	except Exception:
		return u'抱歉，你运气不好，没有人愿意给你讲笑话，请重试。'
		

def weather(city_name):
	str_city='city='+str(city_name)
	url='http://apis.baidu.com/heweather/weather/free?'+str_city
	req = urllib2.Request(url)
	req.add_header("apikey", "自己的")
	resp = urllib2.urlopen(req)
	content= resp.read().decode('utf-8')
	city=re.findall(r'"city":"(.*?)"',content,re.S)
	update=re.findall(r'"loc":"(.*?)"',content,re.S)
	txt=re.findall(r'"txt_d":"(.*?)"',content,re.S)
	max_t=re.findall(r'"max":"(.*?)"',content,re.S)
	min_t=re.findall(r'"min":"(.*?)"',content,re.S)
	hum=re.findall(r'"hum":"(.*?)"',content,re.S)
	pcpn=re.findall(r'"pcpn":"(.*?)"',content,re.S)
	vis=re.findall(r'"vis":"(.*?)"',content,re.S)
	wind_dir=re.findall(r'"dir":"(.*?)"',content,re.S)
	wind_sc=re.findall(r'"sc":"(.*?)"',content,re.S)
	wind_spd=re.findall(r'"spd":"(.*?)"',content,re.S)
	return u'城市：'+city[0]+'\n'+u'更新时间：'+update[0]+'\n'+u'天气情况：'+txt[0]+'\n'+u'最高温度：'+max_t[0]+u'度'+'\n'+u'最低温度：'+min_t[0]+u'度'+'\n'+u'相对湿度：'+hum[0]+'%'+'\n'+u'降水量：'+pcpn[0]+'mm'+'\n'+u'能见度：'+vis[0]+'km'+'\n'+u'风向：'+wind_dir[0]+'\n'+u'风力：'+wind_sc[0]+'\n'+u'风速：'+wind_spd[0]+'km/h'+'\n'


@app.route('/',methods=['GET','POST'])
def wechat():
	if request.method=='GET':
		token='自己的'
		data=request.args
		signature=data.get('signature','')
		timestamp=data.get('timestamp','')
		nonce =data.get('nonce','')
		echostr=data.get('echostr','')
		s=[timestamp,nonce,token]
		s.sort()
		s=''.join(s)
		if(hashlib.sha1(s).hexdigest()==signature):
			return make_response(echostr)
	else:
		rec=request.stream.read()
		xml_rec=ET.fromstring(rec)
		tou = xml_rec.find('ToUserName').text
		fromu = xml_rec.find('FromUserName').text
		content = xml_rec.find('Content').text
 		xml_rep = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"
		if content.lower()=='joke':
			response = make_response(xml_rep % (fromu,tou,str(int(time.time())),joke()))
			response.content_type='application/xml'
			return response
		elif 'tianqi' in content.lower():
			if type(content).__name__ == "unicode":
				content = content.encode('UTF-8')
				place=content.lower().replace('+tianqi','')
				response = make_response(xml_rep % (fromu,tou,str(int(time.time())),weather(place)))
				response.content_type='application/xml'
				return response
			else:
				place=content.lower().replace('+tianqi','')
				response = make_response(xml_rep % (fromu,tou,str(int(time.time())),weather(place)))
				response.content_type='application/xml'
				return response
		else:
			if type(content).__name__ == "unicode":
				content = content.encode('UTF-8')
				new_word=youdao(content)
				response = make_response(xml_rep % (fromu,tou,str(int(time.time())),new_word))
				response.content_type='application/xml'
				return response
			else:
				new_word=youdao(content)
				response = make_response(xml_rep % (fromu,tou,str(int(time.time())),new_word))
				response.content_type='application/xml'
				return response

