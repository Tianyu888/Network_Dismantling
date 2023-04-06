def find_directed(G, points, xlb, ylb, bombwidth, bomblength):
    ret = []
    for i in range(len(G)):
        point1 = i+1
        x1, y1 = points[point1][0], points[point1][1]
        for point2 in G[i]:
            x2, y2 = points[point2][0], points[point2][1]
            k = 0
            if x2 - x1 == 0:
                k = float("inf")
            else:
                k = float(y2 - y1) / float(x2 - x1)
            b = y1 - x1 * k

            if xlb <= x1 <= xlb + bombwidth and xlb <= x2 <= xlb + bombwidth \
                and ylb <= y1 <= ylb + bomblength and ylb <= y2 <= ylb + bomblength:
                ret.append({point1,point2})
                continue
            if k == 0:
                if ylb <= y1 <= ylb + bomblength and (min(x1,x2) <= xlb <= max(x1,x2)
                   or min(x1,x2) <= xlb + bombwidth <= max(x1,x2) ):
                    ret.append({point1, point2})
                    continue
                else:
                    continue
            if k == float("inf"):
                if xlb <= x1 <= xlb + bombwidth and (min(y1,y2) <= ylb <= max(y1,y2)
                   or min(y1,y2) <= ylb + bomblength <= max(y1,y2)):
                    ret.append({point1, point2})
                    continue
                else:
                    continue
            if min(x1,x2) <= xlb <= max(x1,x2):
                tmp = xlb * k + b
                if ylb <= tmp <= ylb + bomblength:
                    ret.append({point1,point2})
                    continue
            if min(y1, y2) <= ylb <= max(y1, y2):
                tmp = (float(ylb) -b) /k
                if xlb <= tmp <= xlb + bombwidth:
                    ret.append({point1,point2})
                    continue
            if min(x1, x2) <= xlb + bombwidth <= max(x1, x2):
                tmp = (xlb + bombwidth) * k + b
                if ylb <= tmp <= ylb + bomblength:
                    ret.append({point1,point2})
                    continue
            if min(y1, y2) <= ylb+bomblength <= max(y1, y2):
                tmp = (float(ylb + bomblength) - b) / k
                if xlb <= tmp <= xlb + bombwidth:
                    ret.append({point1, point2})
                    continue
    return ret

def find_undirected(edges, points, xlb, ylb, bombwidth, bomblength):
    ret = []
    for i in edges:
        point1, point2 = i[0], i[1]
        x1, y1 = points[point1][0], points[point1][1]
        x2, y2 = points[point2][0], points[point2][1]
        k = 0
        if x2 - x1 == 0:
            k = float("inf")
        else:
            k = float(y2 - y1) / float(x2 - x1)
        b = y1 - x1 * k

        if xlb <= x1 <= xlb + bombwidth and xlb <= x2 <= xlb + bombwidth \
                and ylb <= y1 <= ylb + bomblength and ylb <= y2 <= ylb + bomblength:
            ret.append({point1, point2})
            continue
        if k == 0:
            if ylb <= y1 <= ylb + bomblength and (min(x1, x2) <= xlb <= max(x1, x2)
                                                  or min(x1, x2) <= xlb + bombwidth <= max(x1, x2)):
                ret.append({point1, point2})
                continue
            else:
                continue
        if k == float("inf"):
            if xlb <= x1 <= xlb + bombwidth and (min(y1, y2) <= ylb <= max(y1, y2)
                                                 or min(y1, y2) <= ylb + bomblength <= max(y1, y2)):
                ret.append({point1, point2})
                continue
            else:
                continue
        if (xlb == x1 and ylb == y1) or (xlb + bombwidth == x1 and ylb == y1)\
            or (xlb == x1 and ylb+ bombwidth == y1) or (xlb+ bombwidth == x1 and ylb+ bombwidth == y1) \
            or (xlb == x2 and ylb == y2) or (xlb + bombwidth == x2 and ylb == y2) \
            or (xlb == x2 and ylb + bombwidth == y2) or (xlb + bombwidth == x2 and ylb + bombwidth == y2):
            ret.append({point1, point2})
            continue
        if min(x1, x2) <= xlb <= max(x1, x2):
            tmp = xlb * k + b
            if ylb <= tmp <= ylb + bomblength:
                ret.append({point1, point2})
                continue
        if min(y1, y2) <= ylb <= max(y1, y2):
            tmp = (float(ylb) - b) / k
            if xlb <= tmp <= xlb + bombwidth:
                ret.append({point1, point2})
                continue
        if min(x1, x2) <= xlb + bombwidth <= max(x1, x2):
            tmp = (xlb + bombwidth) * k + b
            if ylb <= tmp <= ylb + bomblength:
                ret.append({point1, point2})
                continue
        if min(y1, y2) <= ylb + bomblength <= max(y1, y2):
            tmp = (float(ylb + bomblength) - b) / k
            if xlb <= tmp <= xlb + bombwidth:
                ret.append({point1, point2})
                continue
    edges_new = []
    #print(ret)
    for i in edges:
        if {i[0], i[1]} in ret:

            continue
        else:
            #print((points[i[0]], points[i[1]]))
            edges_new.append((i[0], i[1]))
    return edges_new

def find_undirected(G, xlb, ylb, bombwidth, bomblength):
    ret = []
    for i in G.edges:
        point1, point2 = i[0], i[1]
        x1, y1 = G.nodes[point1]['pos'][0], G.nodes[point1]['pos'][1]
        x2, y2 = G.nodes[point2]['pos'][0], G.nodes[point2]['pos'][1]
        k = 0
        if x2 - x1 == 0:
            k = float("inf")
        else:
            k = float(y2 - y1) / float(x2 - x1)
        b = y1 - x1 * k

        if xlb <= x1 <= xlb + bombwidth and xlb <= x2 <= xlb + bombwidth \
                and ylb <= y1 <= ylb + bomblength and ylb <= y2 <= ylb + bomblength:
            ret.append({point1, point2})
            continue
        if k == 0:
            if ylb <= y1 <= ylb + bomblength and (min(x1, x2) <= xlb <= max(x1, x2)
                                                  or min(x1, x2) <= xlb + bombwidth <= max(x1, x2)):
                ret.append({point1, point2})
                continue
            else:
                continue
        if k == float("inf"):
            if xlb <= x1 <= xlb + bombwidth and (min(y1, y2) <= ylb <= max(y1, y2)
                                                 or min(y1, y2) <= ylb + bomblength <= max(y1, y2)):
                ret.append({point1, point2})
                continue
            else:
                continue
        if (xlb == x1 and ylb == y1) or (xlb + bombwidth == x1 and ylb == y1)\
            or (xlb == x1 and ylb+ bombwidth == y1) or (xlb+ bombwidth == x1 and ylb+ bombwidth == y1) \
            or (xlb == x2 and ylb == y2) or (xlb + bombwidth == x2 and ylb == y2) \
            or (xlb == x2 and ylb + bombwidth == y2) or (xlb + bombwidth == x2 and ylb + bombwidth == y2):
            ret.append({point1, point2})
            continue
        if min(x1, x2) <= xlb <= max(x1, x2):
            tmp = xlb * k + b
            if ylb <= tmp <= ylb + bomblength:
                ret.append({point1, point2})
                continue
        if min(y1, y2) <= ylb <= max(y1, y2):
            tmp = (float(ylb) - b) / k
            if xlb <= tmp <= xlb + bombwidth:
                ret.append({point1, point2})
                continue
        if min(x1, x2) <= xlb + bombwidth <= max(x1, x2):
            tmp = (xlb + bombwidth) * k + b
            if ylb <= tmp <= ylb + bomblength:
                ret.append({point1, point2})
                continue
        if min(y1, y2) <= ylb + bomblength <= max(y1, y2):
            tmp = (float(ylb + bomblength) - b) / k
            if xlb <= tmp <= xlb + bombwidth:
                ret.append({point1, point2})
                continue
    edges_new = []
    #print(ret)
    for i in G.edges:
        if {i[0], i[1]} in ret:

            continue
        else:
            #print((points[i[0]], points[i[1]]))
            edges_new.append((i[0], i[1]))
    return edges_new

def modify(G, mod):
    newG = []
    for i in range(len(G)):
        newG.append([])
    for i in range(len(G)):
        for j in G[i]:
            if {i+1,j} not in mod:
                newG[i].append(j)
    return newG






