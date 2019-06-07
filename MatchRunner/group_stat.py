import json

with open('schedule/all_matches.json') as f:
    ALL_MATCHES = json.load(f)

with open('schedule/group.json') as f:
    name_tmp = json.load(f)
    name_map = {}
    for k, teams in name_tmp.items():
        for i, t in enumerate(teams):
            name_map[k + str(i)] = t

tot_score = {ch: [[0] * 6 for i in range(4)] for ch in "ABCDEFGH"}
all_group_stage = {
    **ALL_MATCHES["group_stage"]["round1"],
    **ALL_MATCHES["group_stage"]["round2"],
    **ALL_MATCHES["group_stage"]["round3"]
}
for plrs, score in all_group_stage.items():
    if score == [0, 0]:
        continue
    plrs = plrs.split('-')
    for i in range(2):
        d_score = [
            1,
            score[i] > score[1 - i],
            score[i] < score[1 - i],
            score[i] == score[1 - i],
            score[i],
            score[1 - i],
        ]
        for j in range(6):
            tot_score[plrs[i][0]][int(plrs[i][1])][j] += d_score[j]

ranking = {i: [None for j in range(4)] for i in "ABCDEFGH"}
named_score = [[[
    i + str(j), (tot_score[i][j][1] * 3 + tot_score[i][j][3] * 1),
    tot_score[i][j][4]
] for j in range(4)] for i in "ABCDEFGH"]
for lst in named_score:
    lst.sort(key=lambda x: -x[2])
    lst.sort(key=lambda x: -x[1])
for i in range(4):
    a_lst = [0, 2, 4, 6]
    b_lst = [1, 3, 5, 7]
    ALL_MATCHES["final_stage"]["8th_final"].update({
        named_score[a_lst[i]][0][0] + "-" + named_score[b_lst[i]][1][0]:
        None,
        named_score[a_lst[i]][1][0] + "-" + named_score[b_lst[i]][0][0]:
        None
    })

res = ALL_MATCHES["final_stage"]["8th_final"].keys()
print(res)

with open('res.txt', 'w') as f:
    for x in res:
        a, b = x.split('-')
        tmp = name_map[a] + ' - ' + name_map[b]
        print(tmp)
        print(tmp, file=f)
