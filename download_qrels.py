import os

if __name__ == '__main__':

    qrels2021 = "https://trec.nist.gov/data/trials/qrels2021.txt"
    qrels2022 = "https://trec.nist.gov/data/trials/qrels2022.txt"

    os.system(f"wget {qrels2021} -P data/external/")
    os.system(f"wget {qrels2022} -P data/external/")
