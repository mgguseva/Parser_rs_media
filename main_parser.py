import os
from multiprocessing import Process
from tqdm.asyncio import tqdm

from atv_parser import run as run_atv_parser
from frontal_parser import run as run_frontal_parser
from nezavisne_parser import run as run_nezavisne_parser
from rtrs_parser import run as run_rtrs_parser
from rtvbn_parser import run as run_rtvbn_parser
from patriotesrpske_parser import run as run_patriotesrpske_parser

def track_progress(processes):
    with tqdm(total=len(processes)) as pbar:
        for p in processes:
            p.join()
            pbar.update(1)

def main():

    if not os.path.exists('Parser_rs_media/data'):
        os.makedirs('Parser_rs_media/data')
    

    parsers = [run_nezavisne_parser, run_rtrs_parser, run_patriotesrpske_parser, run_atv_parser, run_frontal_parser, run_rtvbn_parser]
    
    processes = []

    for parser in parsers:
        p = Process(target=parser)
        processes.append(p)
        p.start()
    
    # Track progress of parsers using tqdm
    track_progress(processes)

if __name__ == "__main__":
    main()
