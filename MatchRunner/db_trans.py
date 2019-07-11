import os, sqlite3, json, zlib, pickle


def parse_db(path):
    """ sqlite -> dict """
    conn = sqlite3.connect(path)
    cur = conn.cursor()

    res = {
        "players": ['code1', 'code2'],
        "winner": -1,
        "cause": None,
        "detail": [0, 0],
        "data": [],
    }

    # 1. read frames
    frame_tables = cur.execute(
        "select name from sqlite_master where type='table' and name like 'FRAME%'"
    )
    frame_tables = [x[0] for x in frame_tables]
    for table in frame_tables:
        frame = []
        for cell in cur.execute("select * from " + table):
            frame.append(cell[1:])
        res['data'].append(frame)
        pass

    # 2. read meta data
    for meta, info in cur.execute("select * from meta").fetchall():
        res[meta] = eval(info)

    conn.close()
    return res


def dump_record(obj, path):
    """ dict -> zipped object """
    raw = pickle.dumps(obj)
    zraw = zlib.compress(raw, -1)
    os.makedirs(os.path.dirname(path), exist_ok=1)
    with open(path, 'wb') as f:
        f.write(zraw)


for root, _, files in os.walk('data'):
    for f in files:
        path = os.path.join(root, f)
        if not path.endswith('.db'):
            continue
        try:
            names, tail = f.rsplit('-', 1)
            names = eval(names)
            tail = tail.split('.', 1)[0]
            name = '%s_%s_%s.zlog' % (*names, tail)
            r1 = root.replace('data', 'data_pickle', 1)
            pathn = os.path.join(r1, name)
        except:
            continue
        data = parse_db(path)
        dump_record(data, pathn)
        print(pathn)
