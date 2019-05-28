import hashlib

# 原始数据
teams = '''F-007	5	李硕业
F-2333	5	王游龙
F-404	5	刘禹杉
F-777	5	彭乃杰
F-8848	5	张佐
F-996	5	张瀚凯
F-Alpha	4	黄俊翔
F-Bravo	5	俞思濛
F-Chalie	1	张良琦
F-Delta	5	刘富康
F-Echo	5	吴子祺
F-Foxtrot	5	王旻宇
F-Golf	4	邓玄宇
F-Hotel	5	施新宇
F-Juliet	5	宋心仪
F-Kilo	4	周云龙
F-Lima	5	漆楹烽
F-Mike	5	张平
F-November	5	曹子倪
F-Oscar	5	秦贺铮
F-Papa	5	张祚同
F-Romeo	4	田雨沛
F-Tango	5	陈葆茵
F-Uniform	5	张湛川
F-Victor	4	赵睿
F-Whisky	5	杜卓晨
F-X-Ray	5	孙家祥
F-Zulu	5	徐多多
N-007	4	黄含青
N-119	4	刘奕好
N-2333	5	刘青林
N-404	5	张彦斌
N-520	5	李鸿宇
N-666	5	张星原
N-777	5	汪子健
N-8848	2	朱贺（旁听）
N-996	5	康怡安
N-Alpha	5	邢泽栋
N-Bravo	5	言浩雄
N-Charlie	4	汪弘毅
N-Delta	5	陈杨
N-Echo	5	雷寅嘉
N-Foxtrot	4	齐殿卿
N-Golf	5	臧芷育
N-Kilo	1	李仲生
N-Mike	5	王瑞刚
N-November	5	吾拉哈提·阿达力别克
N-Oscar	4	吴天昊
N-Papa	5	蒋诗琪
N-Sierra	2	韦宇
N-Tango	2	王威
N-Victor	5	谢中林
N-Whiskey	2	邹瑜
N-Yankee	5	黄志贤
N-Zulu	5	洪鹄'''.split('\n')

# 读入数据
pool = {'F': [], 'N': []}
for line in teams:
    pool[line[0]].append(line.split('\t'))


# 按hash值排序打乱
def shuffle(lst):
    def get_key(team):
        tmp = hashlib.md5()
        tmp.update(team[0].encode('utf-8'))
        tmp.update(team[2].encode('utf-8'))
        return tmp.hexdigest()

    for team in lst:
        team.insert(0, get_key(team))
    lst.sort()


[*map(shuffle, pool.values())]

# 分组输出
print_backup = print


def print(*a, **kw):
    print_backup(*a, **kw)
    print_backup(*a, **kw, file=f)


nteam = 8
with open('README.md', 'w', encoding='utf-8') as f:
    for FN in 'FN':
        print('# %s18小组赛安排:' % FN)
        print('\\#|Team1|Team2|Team3|Team4|\n-|-|-|-|-')
        for i in range(nteam):
            group = pool[FN][i::nteam]
            print(chr(65 + i), *(t[1] for t in group), sep='|')
