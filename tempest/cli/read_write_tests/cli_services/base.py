class CliClientBase(object):

    @classmethod
    def list_table2dict(self, body, mod):
        entries = {mod : []}
        fields = ()
        body = body.strip()
        body = body.split("\n")
        for line in body:
            entry = {}
            # get rid of +--- lines
            if not line.strip().startswith("+-"):
            # weed out first and last | and get rid of whitespace
                cells = [x.strip() for x in line.split("|")[1:-1] ]
                    # first get field names if we don't have it already
                if len(fields) == 0:
                    fields = [cell for cell in cells]
                    # do not process this line and skip to next in file
                    continue

                # we already found the field names
                if len(fields) != 0:
                    for (key,value) in zip(fields, cells):
                        entry[key] = value
                    entries[mod].append(entry)

        return entries

    @classmethod
    def create_table2dict(self, body, mod):
        new_cell = []
        entry = {}
        body = body.strip()
        body = body.split("\n")
        if not body[0].strip().startswith("+-"):
            body = body[1:]

        for line in body:
            # get rid of +--- lines
            if not line.strip().startswith("+-"):
                # weed out first and last | and get rid of whitespace
                cells = [x.strip() for x in line.split("|")[1:-1] ]
                if cells[0] != '':
                    new_cell.append(cells)
                else:
                    new_cell[-1][1] += " " + cells[1]

        for k,v in new_cell[1:]:
            entry[k] = v
        entries = {mod : entry}
        return entries
