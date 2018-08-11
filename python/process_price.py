import sys
# pip install inotify
import inotify.adapters

def _main(path):
    i = inotify.adapters.Inotify()
    
    i.add_watch(path[1])

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
              path, filename, type_names))
        

if __name__ == "__main__":
    print sys.argv
    sys.exit(_main(sys.argv))
