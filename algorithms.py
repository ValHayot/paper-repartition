from enum import Enum

class Axes(Enum):
    i: 0,
    j: 1,
    k: 2

def compute_zones(B, O):
    """ Calcule les zones pour le dictionnaire "array"
    Arguments:
    ----------
        B: buffer shape
        O: output file shape
    """
    volumes_dictionary = dict()

    # for each buffer
    for buffer_index in range(nb_buffers):
        _3d_index = get3dpos(buffer_index)
        T = list()
        for i in range(3):
            C = (_3d_index[i] * B[i]) % O[i]
            T.append(B[i] - C)

        # I- compute volumes' positions following pillow indexing for rectangles
        volumes = {
            0: list(),
            1: [(B[Axes.i], 0, T[Axes.k]),
                (0, T[Axes.j], B[Axes.k])],
            2: [(B[Axes.i], T[Axes.j], T[Axes.k]),
                (0, B[Axes.j], B[Axes.k])],
            3: [(T[Axes.i], T[Axes.j], 0),
                (0, B[Axes.j], T[Axes.k])],
            4: [(B[Axes.i], 0, 0),
                (T[Axes.i], T[Axes.j], T[Axes.k])],
            5: [(B[Axes.i], 0, T[Axes.k]),
                (T[Axes.i], T[Axes.j], B[Axes.k])],
            6: [(B[Axes.i], T[Axes.j], 0),
                (T[Axes.i], B[Axes.j], T[Axes.k])],
            7: [(B[Axes.i], T[Axes.j], T[Axes.k]),
                (T[Axes.i], B[Axes.j], B[Axes.k])]
        }

        # II- compute hidden output files' positions (in F0)
        # a) get volume points
        l = list()
        for dim in range(3):
            values_in_dim = list()
            nb_hidden_files = T[dim]/O[dim]
            nb_complete = floor(nb_hidden_files)

            a = T[dim]
            values_in_dim.append(a)
            for _ in range(nb_complete):
                b = a - O[dim]
                values_in_dim.append(b)
                a = b
            if not 0 in values_in_dim:
                values_in_dim.append(0)
            values_in_dim.sort()
            l.append(values_in_dim)

        # b) compute volumes' positions from volume points
        p1 = [0,0,0]
        p2 = [1,1,1]
        for i in range(len(l[0])-1):
            for j in range(len(l[1])-1):
                for k in range(len(l[2])-1):
                    coords = [(l[0][p1[0]], l[1][p1[1]], l[2][p1[2]]),
                              (l[0][p2[0]], l[1][p2[1]], l[2][p2[2]])]
                    volumes[0].append(coords)
                    p1[Axis.k] += 1
                    p0[Axis.k] += 1
                p1[Axis.j] += 1
                p0[Axis.j] += 1
            p1[Axis.i] += 1
            p0[Axis.i] += 1

        # merge les deux structures de données contenant les volumes

        # III- Add offset: process positions to get real positions in reconstructed image

        # store volumes at index buffer_index
        volumes_dictionary[buffer_index] = volumes

    # IV - Assigner les volumes à tous les output files, en gardant référence du type de volume que c'est
    array_dict = dict()
    alloutfiles = list(range(nb_outfiles))
    for buffer_index in buffers:
        crossed_outfiles = get_crossed_outfiles(O, buffer_index)
        buffervolumes = volumes[bufer_index]
        for volume in buffervolumes:
            for outfile in crossed_outfiles:
                if included_in(outfile, volume):
                    add_to_array_dict(outfile, volume)
                    break # a volume can belong to only one output file

    # V - Pour chaque output file, pour chaque volume, si le volume doit être kept alors fusionner
    for outfileindex in array_dict.keys():
        volumes = array_dict[outfileindex]
        for volume in volumes:
            if volume.index in volumestokeep:
                merge_volumes(volumes, volume.index)
        array_dict[outfileindex] = map_to_slices(volumes)