import os
import argparse
import datetime

class Tombstone:
    def __init__(self, directory=None, level=1, depth=0, threshold=None):

        # base directory to start monitoring
        self._directory = directory

        # Name of tombstone file
        self._filename = "download_complete.txt"

        # monitor subdirs this many levels below the base
        self._level = level

        # how many levels for subdirs to examine for a monitored directory
        self._depth = depth

        # most recent list of monitored directories and ages
        self._monitor=None

        # most recent list of static directories without a tombstone
        self._static=None

        # Age (in seconds) used to trigger the creation of a tombstone
        self._threshold=threshold

    @property
    def depth(self):
        return self._depth
    
    @depth.setter
    def depth(self, value: int):
        self._depth = value

    @property
    def directory(self):
        return self._directory
    
    @directory.setter
    def directory(self, value: str):
        if not os.path.isdir(value):
            raise ValueError(f'Not a directory: {value}')
        self._directory = value

    @property
    def filename(self):
        return self._filename
    
    @filename.setter
    def filename(self, value: str):
        self._filename = value

    @property
    def level(self):
        return self._level
    
    @level.setter
    def level(self, value: int):
        self._level = value

    @property
    def monitor(self):
        return self._monitor

    @monitor.setter
    def monitor(self, value: list | None):
        self._monitor = value

    @property
    def static(self):
        return self._static
    
    @static.setter
    def static(self, value: list | None):
        self._static = value

    @property
    def threshold(self):
        return self._threshold
    
    @threshold.setter
    def threshold(self, value: int | None):
        if value < 0:
            raise ValueError(f'Invalid threhsold: {value}')
        self._threshold = value        

    # Get the list of directories to monitor. These are subdirectories that
    #   are the specified number of levels below the base directory
    #   and do not currently contain a tombstone file
    def get_dirs_list(self, directories: list, levels: int, continuous: bool):
        dlevel = 0
        outlist = []
        finished = False
        dlist = directories

        while (dlevel < levels) and not finished:

            ilist = []
            for d in dlist:
                ilist = ilist + [os.path.join(d,x) for x in os.listdir(d) if os.path.isdir(os.path.join(d,x))]

            finished = len(ilist) == 0 

            dlevel = dlevel + 1
            if not finished:
                if continuous:
                    outlist = outlist + ilist
                else:
                    if dlevel == levels:
                        outlist = ilist
                
            dlist = ilist

        if self.filename is not None:   
            outlist = [x for x in outlist if not os.path.exists(os.path.join(x,self.filename))]
        outlist = [ {'name':x, 'age': os.path.getmtime(x)} for x in outlist ]

        return(outlist)


    def update(self, make_tombstones=True):

        # current timestamp for reference
        timestamp = datetime.datetime.now().timestamp()

        # If only monitoring the base directory
        if self._level == 0:
             return([[self._directory, timestamp-os.path.getmtime(self._directory)]])
        
        # get last mod time for directories of interest
        self.monitor = self.get_dirs_list([self.directory], self.level, False)

        # Get age in seconds of each directory
        for d in range(len(self.monitor)):
            self.monitor[d]['age'] = timestamp - self.monitor[d]['age']


        # Get ages of subdirectoires within each monitored directory
        # Set age of monitoried dir to youngest subdir under it 
        for d in range(len(self.monitor)):
            d_subs = self.get_dirs_list( [self.monitor[d]['name']], self.depth, True)
            for s in range(len(d_subs)):
                age = timestamp - d_subs[s]['age']
                if age < self.monitor[d]['age']:
                    self.monitor[d][1] = age

        # Sort to oldest first
        self.monitor.sort(key=lambda x: x['age'])

        # get dirs considered "static"
        self.static = [x for x in self.monitor if x['age'] > self.threshold ]

        retlist = []
        if make_tombstones:
            for d in self.static:
                tombname = os.path.join(d['name'], self.filename)
                with open(tombname, 'w') as f:
                    retlist.append(tombname)
                    
        return(retlist)
    
def main():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Create tombstone files in static directories")
    parser.add_argument("--path", '-p', type=str, required=True, help="Location to save dicom images") 
    parser.add_argument("--level", '-l', type=int, help="Number of levels down to monitor", default=1)
    parser.add_argument("--depth", '-d', type=int, help="How many level deep with a dir to monitor to changes to subdirs", default=0)
    parser.add_argument("--threshold", '-t', type=float, help="How many seconds to be considered static", default=0)
    parser.add_argument("--filename", '-f', type=str, help="Filename for tombstone file", default=None)
    parser.add_argument("--info", '-i', action='store_true', help="List info but don't create tombstones")
    parser.add_argument("--verbose", '-v', action='store_true', help="Verbose output")
    args = parser.parse_args()            

    t = Tombstone(args.path, args.level, args.depth, args.threshold)
    t.filename = args.filename

    make_tombstones = (args.filename is not None) and (not args.info)

    tlist = t.update(make_tombstones)

    if args.verbose:

        print("Directories to monitor")        
        for d in t.monitor:
            print("  " + d['name'] + " " + str(d['age']))

        print("Static directories")
        for d in t.static:
            print("  "+d['name'] + " " + str(d['age']))

        if len(tlist) > 0:
            print("Created tombstones")
            for f in tlist:
                print("  "+f)

if __name__ == "__main__":
    main()


