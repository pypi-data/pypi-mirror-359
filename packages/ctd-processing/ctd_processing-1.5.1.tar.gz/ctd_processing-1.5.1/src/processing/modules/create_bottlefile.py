from pathlib import Path
import numpy as np
from seabirdfilehandler import CnvFile, BottleLogFile


def get_bottle_file(
    input_path: Path | str, output_path: Path | str = None, save=True
):
    blf = BottleLogFile(input_path)
    cnv = CnvFile(blf.origin_cnv, create_dataframe=False)

    parameter_list = cnv.parameters.get_parameter_list()

    parameter_indexes = get_parameters(parameter_list)
    averages = get_averages(parameter_indexes, cnv, blf)

    if save:
        new_path = Path(output_path)
        create_btl(cnv.header, blf, averages, cnv, new_path)
    else:
        return create_btl(cnv.header, blf, averages, cnv, save=False)


def get_parameters(parameter_list: list) -> list:
    """gets the Indices of the required parameterts from the cnv

    Parameters
    ----------
    List of Parameters of the cnv

    Returns
    -------
    list of corresponding indices

    """
    req_parameters = [
        "prDM",
        "t090C",
        "t190C",
        "c0mS/cm",
        "c1mS/cm",
        "sbox0Mm/Kg",
        "sbox1Mm/Kg",
        "sal00",
        "sal11",
        "par",
        "spar",
        "flECO-AFL",
        "turbWETntu0",
    ]
    par_shortname_list = [x.name for x in parameter_list]
    par_index_list = []
    for i in range(len(req_parameters)):
        par_index_list.append(par_shortname_list.index(req_parameters[i]))
    return par_index_list


def get_averages(
    par_index_list: list, cnv: CnvFile, blf: BottleLogFile
) -> np.ndarray:
    cnv_data = cnv.parameters.full_data_array
    averages = np.array(
        [
            [None for x in range(len(par_index_list))]
            for y in range(len(blf.data_list))
        ]
    )

    for i in range(len(blf.data_list)):
        for j in range(len(par_index_list)):
            start_index = blf.data_list[i][2][0]
            end_index = blf.data_list[i][2][1]
            averages[i, j] = np.average(
                cnv_data[start_index:end_index, j]
            ).round(4)

    return averages


def create_btl(
    header: str,
    bottle_log_file: BottleLogFile,
    data_averages: np.ndarray,
    cnv: CnvFile,
    file_path: Path = None,
    save=True,
):
    req_parameters = [
        "prDM",
        "t090C",
        "t190C",
        "c0mS/cm",
        "c1mS/cm",
        "sbox0Mm/Kg",
        "sbox1Mm/Kg",
        "sal00",
        "sal11",
        "par",
        "spar",
        "flECO-AFL",
        "turbWETntu0",
    ]

    btl_file = ""

    names_and_spans = True

    for line in header:
        if line[0] == "#" and names_and_spans:
            if "Sensors" in line:
                names_and_spans = False
                btl_file += str(line)
            continue
        if "ascii" in line:
            btl_file += "# create_bottlefile \n"  # vor # filetype ascii # öfter pushen # test chekcs docker container zeugs

        btl_file += str(line)

    btl_base_id = int(cnv.metadata["WsStartID"]) - 1

    line = add_whitespace("Btl NR")
    line += add_whitespace("Btl ID")
    line += add_whitespace("Datetime", 22)
    for i in range(len(req_parameters)):
        line += add_whitespace(req_parameters[i])
    btl_file += line + "\n"

    for i in range(len(bottle_log_file.data_list)):
        line = ""

        line += add_whitespace(bottle_log_file.data_list[i][0])
        line += add_whitespace(bottle_log_file.data_list[i][0] + btl_base_id)
        line += add_whitespace(bottle_log_file.data_list[i][1], 22)

        for j in range(len(data_averages[0])):
            line += add_whitespace(data_averages[i, j])

        if i == len(bottle_log_file.data_list) - 1:
            btl_file += line
            continue

        btl_file += line + "\n"

    if save:
        f = open(file_path, "w")
        f.write(btl_file)
        f.close
    else:
        return btl_file


def add_whitespace(data, space: int = 11):
    return (space - len(str(data))) * " " + str(data)


if __name__ == "__main__":
    get_bottle_file(
        r"E:\Arbeit\Processing\processing\src\processing\modules\bl_test.bl",
        r"E:\Arbeit\Processing\processing\src\processing\bottlefiles\test.btl",
    )
