import os.path

import pandas as pd

def list_file(directory_path: str,extension : str) -> List[str]:
    """
    Returns the list of files to unzip present in the directory indicated in the variable directory_path.
    :param directory_path: Targerted directory
    :return: list of path.
    """
    files = []
    pwd = os.path.dirname(os.path.realpath(__file__))
    directory_absolut_path = os.path.join(pwd, directory_path)
    all_files_in_directory = listdir(directory_absolut_path)
    for file in all_files_in_directory:
        if file.find(extension) >= 0:
            files.append(file)

    return files

def read_csv():
    path = "C:/Users/arnau/Repo_GIT/SEPT23-BDE-OPA/data/spot/monthly/klines/BTCUSDT/1m/extract/"
    file = "BTCUSDT-1m-2017-08.csv"
    test = os.path.join(path, file)
    csv = pd.read_csv(test, delimiter=",", header=None)
    data = pd.DataFrame(data=csv)
    csv.head()

path2 = "C:/Users/arnau/Repo_GIT/SEPT23-BDE-OPA/data/spot/monthly/klines/BTCUSDT/1m/extract/"
result = list_file(path2,'.csv')
read_csv()