
def load_calibration_matrix(filename):

    map =  list()
    with open(filename) as fd:
        for line in fd:
            cols = line.strip().split(',')

            items = list()
            for col in cols:
                item = list()
                for i in col.strip().split(' '):
                    item.append(float(i))
                items.append(item)

            map.append(items)

    return map

def load_gcode_commands(filename):

    commands = list()

    with open(filename) as fd:

        prev_cmnd = {"cmd": 'shit', 'X': 0, 'Y': 0, 'Z': 0}

        for line in fd:

            parts = line.strip().split(' ')
            gcode, parts = parts[0], parts[1:]

            command = {"cmd": gcode}

            for part in parts:
                command[part[0]] = part[1:]

            for axis in "XYZ":
                if axis not in command:
                    command[axis] = prev_cmnd[axis]

            commands.append(command)

            prev_cmnd = command


    return commands
