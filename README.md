头疼


南风用zhenxin配置 点击一下 返回  弹出菜单

确定  在左下  二维码  在右下



外挂jar本地或者https不得多于2，否则wogg的网盘播放必挂(fan的https不算)。

网盘配置  重新加载 go  重新载入Alison weishi  可用

低端设备  heiping   强制使用32位



删除广告与辣鸡源：
1. 木叶       茶啊二中 跑马灯广告    241004
2. 360源      哈小浪 黄毒广告    240728
3. Ivdy影视   太多枪版            241020
4. 南瓜       与君初相识 跑马灯广告  241021  
5. 奇优影视   卡成狗        241021
6. 可可多线    冷面机长   跑马灯广告    241111   
7. 欢视多线    太多枪版  241128
8. 木星多线     跑马灯广告  2411129
9. AI4 跑马灯广告
10. 雨滴   同上
11.  暴风采集  注入文字赌博广告
12. 洽洽  黄毒广告
13. 黑木耳
14. 热播多线 
15. 天天/浪酷  太多枪版

16. 糯米秒播

17.潇洒QD影视  注入文字广告




默认进入直播  直播房子键   禁止标志  点成火箭


1、各种路径如jar 需要区分大小写

3、直播界面 菜单键 切换TV和广播 没有home键和菜单键的辣鸡电视千万不能要，home键方便一键回到桌面

4、加速链接 https://ghfast.top/

安装zhibo镜像 

docker run -d --restart always --privileged=true -p 35455:35455 --name allinone youshandefeiyang/allinone -tv=true -aesKey=人工获取 -userid=人工获取-token人工获取


格式化zhibo列表

docker run -d --restart=unless-stopped --pull=always -v /etc/allinone_format:/app/config -p 35456:35456 --name allinone_format yuexuangu/allinone_format:latest

查看镜像ID   docker images


定时更新


docker run -d --name watchtower --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --cleanup --schedule "0 2 * * *" \
  allinone

              





油管卡一分钟  UA=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0

