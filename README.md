# ecmexample
An e-commercial system example

## 参考了两个示例

### 基于Django的电商网站开发高级

https://blog.csdn.net/hello2013zzy/article/details/79650167

<https://github.com/ScrappyZhang/ecommerce_website_development>


### 天天生鲜项目实战-思路 数据库设计
https://www.cnblogs.com/welan/p/9231530.html

https://github.com/weilanhanf/daily_fresh_demo

## 本项目启动说明
### 辅助功能准备

fastdfs: Ubuntu下FastDFS分布式文件系统配置与部署

https://blog.csdn.net/lswnew/article/details/79128794

redis:

`apt-get install redis-server`

celery异步任务处理

https://www.cnblogs.com/wdliu/p/9517535.html

### 启动

uwsgi配合nginx常规启动

虚拟环境下启动celery异步任务处理

`celery worker -A celery_tasks -l debug`

后台商品添加完毕后，需要执行如下命令重建商品索引

`python manage.py rebuild_index`


