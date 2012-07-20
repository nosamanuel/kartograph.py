
import tinycss


class MapStyle(object):

    def __init__(self, css):
        if css:
            parser = tinycss.make_parser()
            self.css = parser.parse_stylesheet(css)
        else:
            self.css = None

    def getStyle(self, layer_id, fprops=dict()):
        """
        Returns a dictionary of style rules for a given feature.
        """
        if self.css is None:
            return {}
        attrs = dict()
        for rule in self.css.rules:
            # Find out whether this rule matches
            if _checkRule(layer_id, fprops, rule):
                for decl in rule.declarations:
                    prop = ''
                    for val in decl.value:
                        if val.type == 'INTEGER':
                            prop += str(val.value)
                        elif val.type == 'DIMENSION':
                            prop += str(val.value) + val.unit
                        else:
                            prop += str(val.value)
                    attrs[decl.name] = prop
        return attrs


def _checkRule(layer_id, fprops, rule):
    parts = [[]]
    k = 0
    for sel in rule.selector:
        if sel.type == 'S':
            # Ignore white spaces
            continue
        if sel.type == 'DELIM' and sel.value == ',':
            # Proceed to next rule
            k += 1
            parts.append([])
            continue
        parts[k].append(sel)
    for p in parts:
        if len(p) > 0:
            if p[0].type == 'HASH' and p[0].value[1:] == layer_id or p[0].type == 'DELIM' and p[0].value == '*':
                if len(p) == 1:
                    return True
                else:
                    match = True
                    for r in p[1:]:
                        if r.type == '[' and r.content[0].type == 'IDENT' and r.content[len(r.content) - 1].type in ('IDENT', 'INTEGER'):
                            key = r.content[0].value
                            val = r.content[len(r.content) - 1].value
                            comp = ''
                            for c in r.content[1:len(r.content) - 1]:
                                if c.type == 'DELIM':
                                    comp += c.value
                                else:
                                    raise ValueError('problem while parsing map stylesheet at ' + rule.selector.as_css())
                            if key not in fprops:
                                match = False
                            else:
                                if comp == '=':
                                    match = match and fprops[key] == val
                                elif comp == '~=':
                                    vals = val.split(' ')
                                    match = match and fprops[key] in vals
                                elif comp == '|=':
                                    # Matches if the attribute begins with the value
                                    # Note that this is a slightly different interpretation than
                                    # the one used in the CSS specs, since we don't require the '-'
                                    match = match and fprops[key][:len(val)] == val
                                elif comp == '=|':
                                    # Matches if the attribute ends with the value
                                    match = match and fprops[key][-len(val):] == val
                                elif comp == '>':
                                    match = match and fprops[key] > val
                                elif comp == '>=':
                                    match = match and fprops[key] >= val
                                elif comp == '<':
                                    match = match and fprops[key] < val
                                elif comp == '<=':
                                    match = match and fprops[key] <= val
                        else:
                            print r
                            match = False
                    if match is True:
                        return True


def style_diff(d1, d2):
    res = dict()
    for key in d1:
        if key not in d2 or d2[key] != d1[key]:
            res[key] = d1[key]
    return res

if __name__ == "__main__":
    css = '''
/*
 * map styles for berlin map
 */

#industry, #urban-1 , #urban-2 {
    opacity: 0.0156863;
    stroke: none;
    fill: #c8c3c3;
}

#lakes, #rivers {
    opacity: 0.4;
    stroke: none;
    fill: #15aee5;
}

#roads-bg {
    fill: none;
    stroke: #fff;
}

#roads {
    fill: none;
    stroke: #e5e1e1;
}

#roads[highway=motorway][administrative=4],
#roads [highway|=motorway] {
    stroke-width: 3pt;
    stroke-dasharray: 3,4,5;
    border: 1px solid #ccc;
}

*[highway=primary] {
    stroke-wigth: 4px;
}

'''
    mapstyle = MapStyle(css)
    layer_css = mapstyle.getStyle('roads')
    full_css = mapstyle.getStyle('roads', dict(highway='motorway_link'))