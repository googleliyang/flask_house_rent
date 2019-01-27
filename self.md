## frame quickly key

## 

- model all use remember, query build, query exec
- json.stringnify & content-type application/json
- http pass data resume origin datatype
- from captcha learn read source code
    - captcha return name ? use?
    - redis save captcah why the code is secret
- redis bind session work

## func

- 404 , error, deal redirect
- add pay platform
- qiniu 


## logic 

- 获验业返


## omit

- cause of date & important level , omit some validate..

## done

- frame your code, quickly develop, such as login ..
- orm very family
- table relation ship
- rebuild base, flask directory
- recently video & markdown
- finish todo
- restful api? djano will teach
- your model return should use to_dict method of model
- return jsonify(errno=RET.PARAMERR,errmsg='参数错误') this way
- why vsc always not found python model
- like Hose column, nullable default is true?
- this is restful maybe, cause get param all in path, post not care & use delete request..
- comments ....House model
- api doc write way
- filter add [], filter allow condition
- paginate


-  i jsonify
 ```python
jsonify(name=1, age=2) , source call dict(*args, **keyword)
```

# why so slow, api interface, --- aliyun sql , aliyun redis...

# 为什么发送短信处耗时，下一个请求也影响处理？？？？？？？？？？？？ 注册接口与之前发送验证码, 因为没有使用多线程部署 代码是运行于单线程

# 路由文件就不能像Laravel 那样简洁明了

# 一对多 多对多 orm 中数据表插值

#   images = db.relationship("HouseImage")  # 房屋的图片 这是什么关系

# 那个拆包

# 数据库关系图，一定要画清楚，这样思路不清楚的时候直接看表关系，不然单看orm 太混乱了，外加接口文档， 如订单编写时，自己订单与客户订单

# UnboundLocalError: local variable 'orders' referenced before assignment, orders 写在if中  Python 中有块级作用域? 没有 ipython3 测试de 

# 前端后退路径问题

# 日期模块处理记住，从数据库插入开始，baseModel 默认值

```python

import time,datetime

# date to str
print time.strftime("%Y-%m-%d %X", time.localtime())

#str to date
t = time.strptime("2009 - 08 - 08", "%Y - %m - %d")
y,m,d = t[0:3]

 s_d = datetime.strptime(start_date, "%Y-%m-%d")
    e_d = datetime.strptime(end_date, "%Y-%m-%d")
    day = e_d - s_d
    print(abs((dt01 - dt02).days)) # 相差多少天

print(abs((dt01 - dt02).seconds)) # 相差多少秒

print(abs((dt01 - dt02).microseconds)) # 相差多少微秒

# order 给自己上了一课 注意 商品只传 id 数量给服务器剩下的服务器自己计算！！！

    https://blog.csdn.net/u010159842/article/details/78331490

```

# 草 代码缺少 admin 的统计？？？？github 推送的, 没事代码拿来 自己 push

