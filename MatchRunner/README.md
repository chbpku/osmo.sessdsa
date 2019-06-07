# 比赛设施

## 内容
课堂小组赛与淘汰赛使用的运行工具与各组提交代码

## 文件
1. manage.py
    * 用于运行小组赛与淘汰赛
    * 详细功能见**使用方法**部分
1. group_stat.py
    * 用于统计小组赛出线结果
    * 直接运行后根据schedule/all_matches.json输出各出线队名至同目录res.txt中

## 目录
1. schedule
    * 参赛代码分组情况+各阶段比赛结果统计
1. code
    * 各组参赛代码
1. obs
    * 输出用于OBS赛况直播的文本信息

## 使用方法
1. 将文件夹内所有内容合并至src文件夹
1. 将schedule文件夹内groupf.json或groupn.json复制为group.json
1. (可选) 删除all_matches.json，重置比赛进度
1. 运行manage.py，并按如下顺序执行指令运行比赛：
    * 3轮小组赛 ("R1", "R2", "R3")
    * 统计小组赛出线结果 ("S")
    * 16进8 ("K8")
    * 8进4 ("K4")
    * 半决赛 ("K2")
    * 决赛+季军争夺 ("FINAL", "3-4 FINAL")